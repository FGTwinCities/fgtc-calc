import asyncio
from dataclasses import dataclass, field

from aiohttp import ClientSession

from app.extern.benchmark.benchmark_data_source import BenchmarkDataSource
from app.extern.benchmark.passmark import PassmarkScraper
from app.extern.benchmark.schema import BenchmarkComponentResult


@dataclass
class GeekbenchComponentResult(BenchmarkComponentResult):
    geekbench_id: int = None


class GeekbenchDataSource(BenchmarkDataSource):
    _cached_cpu_list: list[GeekbenchComponentResult] | None = None
    _cached_gpu_list: list[GeekbenchComponentResult] | None = None

    def _create_session(self) -> ClientSession:
        return ClientSession(
            base_url="https://browser.geekbench.com",
            trust_env=True,
        )

    async def _fetch_cpu_list(self) -> list[GeekbenchComponentResult]:
        results = []

        async with self._create_session() as session:
            async with session.get("processor-benchmarks.json") as response:
                if not response.ok:
                    raise RuntimeError("Unable to retrieve CPU benchmark data from Geekbench.")

                data = await response.json()
                devices = data.get("devices", [])
                for device in devices:
                    results.append(GeekbenchComponentResult(
                        geekbench_id=device.get("id"),
                        name=device.get("name"),
                        score=device.get("multicore_score"),
                    ))

        return results

    async def _fetch_gpu_list(self) -> list[GeekbenchComponentResult]:
        results = []

        async with self._create_session() as session:
            async with session.get("gpu-benchmarks.json") as response:
                if not response.ok:
                    raise RuntimeError("Unable to retrieve CPU benchmark data from Geekbench.")

                data = await response.json()
                devices = data.get("devices", [])
                for device in devices:
                    results.append(GeekbenchComponentResult(
                        geekbench_id=device.get("id"),
                        name=device.get("name"),
                        score=device.get("vulkan"),
                    ))

        return results

    async def retrieve_cpu_list(self) -> list[BenchmarkComponentResult]:
        if self._cached_cpu_list is None:
            self._cached_cpu_list = await self._fetch_cpu_list()

        return self._cached_cpu_list

    async def retrieve_gpu_list(self) -> list[BenchmarkComponentResult]:
        if self._cached_gpu_list is None:
            self._cached_gpu_list = await self._fetch_gpu_list()

        return self._cached_gpu_list

    async def _search(self, retrieve_callable, query: str = None) -> list[GeekbenchComponentResult]:
        if query is None:
            return await retrieve_callable()
        else:
            return list(filter(lambda i: query.lower() in i.name.lower(), await retrieve_callable()))

    async def _find(self, retrieve_callable, query: str) -> GeekbenchComponentResult:
        res = await self._search(retrieve_callable, query)
        return res[0] if len(res) > 0 else None

    async def search_cpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        return await self._search(self.retrieve_cpu_list, query)

    async def find_cpu(self, query: str) -> BenchmarkComponentResult | None:
        return await self._find(self.retrieve_cpu_list, query)

    async def search_gpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        return await self._search(self.retrieve_gpu_list, query)

    async def find_gpu(self, query: str) -> BenchmarkComponentResult:
        return await self._find(self.retrieve_gpu_list, query)


if __name__ == "__main__":
    gb = PassmarkScraper()
    res = asyncio.run(gb.find_cpu("i7-10700k"))
    print(res)