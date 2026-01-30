import asyncio
from dataclasses import dataclass, field

from aiohttp import ClientSession


@dataclass
class GeekbenchSearchResult:
    geekbench_id: int = field()
    name: str = field()
    score: int | None = field()


class GeekbenchDataSource:
    _cached_cpu_list: list[GeekbenchSearchResult] | None = None
    _cached_gpu_list: list[GeekbenchSearchResult] | None = None

    def _create_session(self) -> ClientSession:
        return ClientSession(
            base_url="https://browser.geekbench.com",
            trust_env=True,
        )

    async def _fetch_cpu_list(self) -> list[GeekbenchSearchResult]:
        results = []

        async with self._create_session() as session:
            async with session.get("processor-benchmarks.json") as response:
                if not response.ok:
                    raise RuntimeError("Unable to retrieve CPU benchmark data from Geekbench.")

                data = await response.json()
                devices = data.get("devices", [])
                for device in devices:
                    results.append(GeekbenchSearchResult(
                        geekbench_id=device.get("id"),
                        name=device.get("name"),
                        score=device.get("multicore_score"),
                    ))

        return results

    async def _fetch_gpu_list(self) -> list[GeekbenchSearchResult]:
        results = []

        async with self._create_session() as session:
            async with session.get("gpu-benchmarks.json") as response:
                if not response.ok:
                    raise RuntimeError("Unable to retrieve CPU benchmark data from Geekbench.")

                data = await response.json()
                devices = data.get("devices", [])
                for device in devices:
                    results.append(GeekbenchSearchResult(
                        geekbench_id=device.get("id"),
                        name=device.get("name"),
                        score=device.get("vulkan"),
                    ))

        return results

    async def retrieve_cpu_list(self) -> list[GeekbenchSearchResult]:
        if self._cached_cpu_list is None:
            self._cached_cpu_list = await self._fetch_cpu_list()

        return self._cached_cpu_list

    async def retrieve_gpu_list(self) -> list[GeekbenchSearchResult]:
        if self._cached_gpu_list is None:
            self._cached_gpu_list = await self._fetch_gpu_list()

        return self._cached_gpu_list

    async def _search(self, retrieve_callable, query: str = None) -> list[GeekbenchSearchResult]:
        if query is None:
            return await retrieve_callable()
        else:
            return list(filter(lambda i: query.lower() in i.name.lower(), await retrieve_callable()))

    async def _find(self, retrieve_callable, query: str) -> GeekbenchSearchResult:
        res = await self._search(retrieve_callable, query)
        return res[0] if len(res) > 0 else None

    async def search_cpu(self, query: str = None) -> list[GeekbenchSearchResult]:
        return await self._search(self.retrieve_cpu_list, query)

    async def find_cpu(self, query: str) -> GeekbenchSearchResult | None:
        return await self._find(self.retrieve_cpu_list, query)

    async def search_gpu(self, query: str = None) -> list[GeekbenchSearchResult]:
        return await self._search(self.retrieve_gpu_list, query)

    async def find_gpu(self, query: str) -> GeekbenchSearchResult:
        return await self._find(self.retrieve_gpu_list, query)


if __name__ == "__main__":
    gb = GeekbenchDataSource()
    res = asyncio.run(gb.retrieve_gpu_list())
    print(res)