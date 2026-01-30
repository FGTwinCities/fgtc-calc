import re
from urllib.parse import urlencode

from aiohttp import ClientSession, ClientResponse
from bs4 import BeautifulSoup, Tag

from app.extern.benchmark.benchmark_data_source import BenchmarkDataSource
from app.extern.benchmark.schema import BenchmarkComponentResult
from app.lib.util import try_int
from app.extern.benchmark.passmark.schema import PassmarkCoreDetails, PassmarkSearchResult, PassmarkCpuDetails, PassmarkPECoreCpuDetails, \
    PassmarkStandardCpuDetails, PassmarkGpuDetails


def attempt_cpu_parse(query: str) -> str:
    query = re.sub(r'\s{2,}', ' ', query)

    ryzen = re.search(r'(?:r?y?zen)[-_\s]*(\d)[-_\s]*(pro)?[-_\s]*(\d+\w*)', query.lower())
    intel_core_i = re.search(r'(i\d)[-_\s]*(\d+)(\w*)', query.lower())
    if ryzen:
        query = f"amd ryzen {ryzen.group(1)} {ryzen.group(2) or ""} {ryzen.group(3)}"
    elif intel_core_i:
        query = f"intel core {intel_core_i.group(1)}-{intel_core_i.group(2)}{intel_core_i.group(3) or ''}"

    query = re.sub(r'\s{2,}', ' ', query)
    return query


def attempt_gpu_parse(query: str) -> str:
    return query


def _parse_pe_core_details(tag: Tag) -> PassmarkCoreDetails:
    return PassmarkCoreDetails(
        cores=int(re.search(r'(\d+)(\s*[Cc]ores)', tag.text).group(1)),
        threads=int(re.search(r'(\d+)(\s*[Tt]hreads)', tag.text).group(1)),
        clock=float(re.search(r'(\d+\.?\d*)(\s*[GgHhZz]+\s*[Bb]ase)', tag.text).group(1)),
        turbo_clock=float(re.search(r'(\d+\.?\d*)(\s*[GgHhZz]+\s*[Tt]urbo)', tag.text).group(1)),
    )


class PassmarkScraper(BenchmarkDataSource):
    _cached_cpu_list: list[PassmarkSearchResult] = None
    _cached_gpu_list: list[PassmarkSearchResult] = None

    def _create_cpu_session(self):
        return ClientSession(
            base_url="https://www.cpubenchmark.net",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            },
            trust_env=True,
        )

    def _create_gpu_session(self):
        return ClientSession(
            base_url="https://www.videocardbenchmark.net",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            },
            trust_env=True,
        )


    async def _retrieve_list(self, response: ClientResponse) -> list[PassmarkSearchResult]:
        results = []
        if response.status != 200:
            raise RuntimeError("Request to server was not successful.")

        soup = BeautifulSoup(await response.text(), "html.parser")
        tags = soup.find_all("tr", id=re.compile(r'^[cg]pu\d+$'))

        for tag in tags:
            name = tag.find("a").text

            id = int(re.search(r'\d+', tag.get("id")).group())
            score = int(re.search(r'\d+', tag.find_all("td")[1].text).group())

            results.append(PassmarkSearchResult(
                name=name,
                passmark_id=id,
                score=score,
            ))
        return results


    async def retrieve_cpu_list(self) -> list[BenchmarkComponentResult]:
        if self._cached_cpu_list is not None:
            return self._cached_cpu_list

        async with self._create_cpu_session() as session:
            async with session.get("/cpu-list/all") as response:
                self._cached_cpu_list = await self._retrieve_list(response)
        return self._cached_cpu_list


    async def retrieve_gpu_list(self) -> list[BenchmarkComponentResult]:
        if self._cached_gpu_list is not None:
            return self._cached_gpu_list

        async with self._create_gpu_session() as session:
            async with session.get("/gpu_list.php") as response:
                self._cached_gpu_list = await self._retrieve_list(response)
        return self._cached_gpu_list


    async def _search(self, ret_callable, query: str = None) -> list[PassmarkSearchResult]:
        if query is None:
            return await ret_callable()
        else:
            results = []
            for item in await ret_callable():
                if query.lower() in item.name.lower(): #TODO: Better search algorithm
                    results.append(item)
            return results


    async def _find(self, ret_callable, query: str) -> PassmarkSearchResult | None:
        results = await self._search(ret_callable, query)
        if len(results) >= 1:
            return results[0]
        else:
            return None


    async def search_cpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        return await self._search(self.retrieve_cpu_list, attempt_cpu_parse(query))

    async def find_cpu(self, query: str) -> BenchmarkComponentResult | None:
        return await self._find(self.retrieve_cpu_list, attempt_cpu_parse(query))

    async def search_gpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        return await self._search(self.retrieve_gpu_list, attempt_gpu_parse(query))

    async def find_gpu(self, query: str) -> BenchmarkComponentResult | None:
        return await self._find(self.retrieve_gpu_list, attempt_gpu_parse(query))


    async def retrieve_cpu(self, cpu: PassmarkSearchResult) -> PassmarkCpuDetails:
        return await self.retrieve_cpu_by_id(cpu.passmark_id)


    async def retrieve_cpu_by_id(self, cpu_id: int) -> PassmarkCpuDetails:
        result = None

        async with self._create_cpu_session() as session:
            async with session.get("cpu.php?" + urlencode({"id": cpu_id})) as response:
                if response.status != 200:
                    raise RuntimeError("Request to server was not successful.")

                soup = BeautifulSoup(await response.text(), "html.parser")

                cpu_name = soup.find(["span", "p"], class_="cpuname").text

                class_elem = soup.find(["p", "strong", "b"], string=re.compile(r'[Cc]lass:')).parent
                cpu_class = re.search(r'[Cc]lass:\s*([\w]+)', class_elem.text)
                if cpu_class:
                    cpu_class = cpu_class.group(1)

                socket_elem = soup.find(["p", "strong", "b"], string=re.compile(r'[Ss]ocket:')).parent
                socket = re.search(r'[Ss]ocket:\s*([\w\d]+)', socket_elem.text)
                if socket:
                    socket = socket.group(1)

                total_cores_threads = soup.find(["p", "strong", "b"], string=re.compile(r'[Tt]otal\s[Cc]ores:'))

                if total_cores_threads:
                    # Parse as a CPU that has both performance and efficiency cores
                    result = PassmarkPECoreCpuDetails(
                        name=cpu_name,
                        passmark_id=cpu_id,
                        cpu_class=cpu_class,
                        socket=socket,
                    )

                    try:
                        performance = soup.find(["p", "strong", "b"], string=re.compile(r'[Pp]erformance\s*[Cc]ores:')).parent
                        result.performance_cores = _parse_pe_core_details(performance)
                        efficient = soup.find(["p", "strong", "b"], string=re.compile(r'[Ee]fficient\s*[Cc]ores:')).parent
                        result.efficient_cores = _parse_pe_core_details(efficient)
                    except AttributeError:
                        pass
                else:
                    # Parse as a CPU with only one type of core
                    result = PassmarkStandardCpuDetails(
                        name=cpu_name,
                        passmark_id=cpu_id,
                        cpu_class=cpu_class,
                        socket=socket,
                    )

                    try:
                        cores_thread = soup.find(["p", "strong", "b"], string=re.compile(r'[Cc]ores:')).parent
                        result.cores = int(re.search(r'([Cc]ores:\s*)(\d+)', cores_thread.text).group(2))
                        result.threads = int(re.search(r'([Tt]hreads:\s*)(\d+)', cores_thread.text).group(2))
                    except AttributeError:
                        pass

                    try:
                        clock_tag = soup.find(["p", "strong", "b"], string=re.compile(r'[Cc]lockspeed:')).parent
                        result.clock = float(re.search(r'([Cc]lockspeed:\s*)(\d+\.?\d*)', clock_tag.text).group(2))
                    except AttributeError:
                        pass

                    try:
                        turbo_tag = soup.find(["p", "strong", "b"], string=re.compile(r'[Tt]urbo\s*[Ss]peed:')).parent
                        result.turbo_clock = float(re.search(r'([Tt]urbo\s*[Ss]peed:\s*)(\d+\.?\d*)(\s*[GgHhZz]*)', turbo_tag.text).group(2))
                    except AttributeError:
                        pass

                # Parse CPU ratings
                multi_label = soup.find("div", string=re.compile(r'[Mm]ultithread\s+[Rr]ating'))
                result.score = int(multi_label.find_next_sibling("div").text)
                single_label = soup.find("div", string=re.compile(r'[Ss]ingle\s+[Tt]hread\s+[Rr]ating'))
                result.single_thread_score = int(single_label.find_next_sibling("div").text)

        return result


    async def retrieve_gpu(self, gpu: PassmarkSearchResult) -> PassmarkGpuDetails:
        return await self.retrieve_gpu_by_id(gpu.passmark_id)


    async def retrieve_gpu_by_id(self, gpu_id: int) -> PassmarkGpuDetails:
        result = None

        async with self._create_gpu_session() as session:
            async with session.get("gpu.php?" + urlencode({"id": gpu_id})) as response:
                if response.status != 200:
                    raise RuntimeError("Request to server was not successful.")

                soup = BeautifulSoup(await response.text(), "html.parser")

                gpu_name = soup.find(["span", "p"], class_="cpuname").text
                header_r = soup.find("div", string=re.compile(r'[Aa]verage\s+[Gg]3[Dd]\s+[Mm]ark'))
                g3d_score = try_int(header_r.find_next_sibling("span").text)

                g2d_score = try_int(re.search(r'[Aa]verage\s+[Gg]2[Dd]\s+[Mm]ark:?\s*(\d+)', header_r.parent.text).group(1))

                desc_body = soup.find("div", class_="desc-body")
                category = re.search(r'[Vv]ideo[Cc]ard\s*[Cc]ategory:?\s*(\w+)', desc_body.text)
                if category is not None:
                    category = category.group(1)

                result = PassmarkGpuDetails(
                    name=gpu_name,
                    passmark_id=gpu_id,
                    score=g3d_score,
                    score_g2d=g2d_score,
                    gpu_category=category,
                )

        return result
