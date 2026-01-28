import re
from typing import overload
from urllib.parse import urlencode

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from app.passmark.schema import PassmarkCoreDetails, PassmarkSearchResult, PassmarkCpuDetails, PassmarkPECoreCpuDetails, \
    PassmarkStandardCpuDetails


def _parse_pe_core_details(tag: Tag) -> PassmarkCoreDetails:
    return PassmarkCoreDetails(
        cores=int(re.search(r'(\d+)(\s*[Cc]ores)', tag.text).group(1)),
        threads=int(re.search(r'(\d+)(\s*[Tt]hreads)', tag.text).group(1)),
        clock=float(re.search(r'(\d+\.?\d*)(\s*[GgHhZz]+\s*[Bb]ase)', tag.text).group(1)),
        turbo_clock=float(re.search(r'(\d+\.?\d*)(\s*[GgHhZz]+\s*[Tt]urbo)', tag.text).group(1)),
    )


class PassmarkScraper:
    _cached_cpu_list: list[PassmarkSearchResult] = None

    def _create_cpu_session(self):
        return ClientSession(
            base_url="https://www.cpubenchmark.net",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            }
        )

    async def retrieve_cpu_list(self) -> list[PassmarkSearchResult]:
        if self._cached_cpu_list is not None:
            return self._cached_cpu_list

        results = []
        async with self._create_cpu_session() as session:
            async with session.get("/cpu-list/all") as response:
                if response.status != 200:
                    raise RuntimeError("Request to server was not successful.")

                soup = BeautifulSoup(await response.text(), "html.parser")
                tags = soup.find_all("tr", id=re.compile(r'^cpu\d+$'))

                for tag in tags:
                    cpu_name = tag.find("a").text

                    cpu_id = int(re.search(r'\d+', tag.get("id")).group())
                    score = int(re.search(r'\d+', tag.find_all("td")[1].text).group())

                    results.append(PassmarkSearchResult(
                        name=cpu_name,
                        passmark_id=cpu_id,
                        multithread_score=score,
                    ))

        self._cached_cpu_list = results
        return self._cached_cpu_list

    async def search_cpu(self, query: str = None) -> list[PassmarkSearchResult]:
        if query is None:
            return await self.retrieve_cpu_list()
        else:
            results = []
            for cpu in await self.retrieve_cpu_list():
                if query.lower() in cpu.name.lower(): #TODO: Better search algorithm
                    results.append(cpu)
            return results


    async def find_cpu(self, query: str = None) -> PassmarkSearchResult | None:
        results = await self.search_cpu(query)
        if len(results) >= 1:
            return results[0]
        else:
            return None


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
                result.multithread_score = int(multi_label.find_next_sibling("div").text)
                single_label = soup.find("div", string=re.compile(r'[Ss]ingle\s+[Tt]hread\s+[Rr]ating'))
                result.single_thread_score = int(single_label.find_next_sibling("div").text)

        return result
