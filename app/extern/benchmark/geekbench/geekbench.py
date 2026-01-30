from dataclasses import dataclass

from aiohttp import ClientSession

from app.db.model import Processor, GraphicsProcessor
from app.extern.benchmark.benchmark_data_source import BenchmarkDataSource
from app.extern.benchmark.schema import BenchmarkComponentResult


@dataclass
class GeekbenchComponentResult(BenchmarkComponentResult):
    geekbench_id: int = None


@dataclass
class GeekbenchCpuResult(GeekbenchComponentResult):
    single_thread_score: int = None


class GeekbenchDataSource(BenchmarkDataSource):
    _cached_cpu_list: list[GeekbenchCpuResult] | None = None
    _cached_gpu_list: list[GeekbenchComponentResult] | None = None

    def _create_session(self) -> ClientSession:
        return ClientSession(
            base_url="https://browser.geekbench.com",
            trust_env=True,
        )

    async def _fetch_cpu_list(self) -> list[GeekbenchCpuResult]:
        results = []

        async with self._create_session() as session:
            async with session.get("processor-benchmarks.json") as response:
                if not response.ok:
                    raise RuntimeError("Unable to retrieve CPU benchmark data from Geekbench.")

                data = await response.json()
                devices = data.get("devices", [])
                for device in devices:
                    results.append(GeekbenchCpuResult(
                        geekbench_id=device.get("id"),
                        name=device.get("name"),
                        score=device.get("multicore_score"),
                        single_thread_score=device.get("score"),
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

    async def retrieve_cpu_list(self) -> list[GeekbenchCpuResult]:
        if self._cached_cpu_list is None:
            self._cached_cpu_list = await self._fetch_cpu_list()

        return self._cached_cpu_list

    async def retrieve_gpu_list(self) -> list[GeekbenchComponentResult]:
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

    async def search_cpu(self, query: str = None) -> list[GeekbenchCpuResult]:
        return await self._search(self.retrieve_cpu_list, query)

    async def find_cpu(self, query: str) -> GeekbenchCpuResult | None:
        return await self._find(self.retrieve_cpu_list, query)

    async def search_gpu(self, query: str = None) -> list[GeekbenchComponentResult]:
        return await self._search(self.retrieve_gpu_list, query)

    async def find_gpu(self, query: str) -> GeekbenchComponentResult:
        return await self._find(self.retrieve_gpu_list, query)

    async def retrieve_cpu_by_id(self, id: int) -> GeekbenchCpuResult | None:
        for cpu in await self.retrieve_cpu_list():
            if not isinstance(cpu, GeekbenchComponentResult):
                raise RuntimeError

            if cpu.geekbench_id == id:
                return cpu

        return None

    async def retrieve_gpu_by_id(self, id: int) -> GeekbenchComponentResult | None:
        for gpu in await self.retrieve_gpu_list():
            if not isinstance(gpu, GeekbenchComponentResult):
                raise RuntimeError

            if gpu.geekbench_id == id:
                return gpu

        return None

    async def update_cpu(self, processor: Processor, rebind: bool = False) -> None:
        result: GeekbenchCpuResult
        if not processor.geekbench_id or rebind:
            result = await self.find_cpu(processor.model)
            if result is None:
                raise RuntimeError("CPU was not found on Geekbench")
        else:
            result = await self.retrieve_cpu_by_id(processor.geekbench_id)

        processor.model = result.name
        processor.geekbench_id = result.geekbench_id
        processor.geekbench_multithread_score = result.score
        processor.geekbench_single_thread_score = result.single_thread_score

    async def update_gpu(self, gpu: GraphicsProcessor, rebind: bool = False) -> None:
        result: GeekbenchComponentResult
        if not gpu.geekbench_id or rebind:
            result = await self.find_gpu(gpu.model)
            if result is None:
                raise RuntimeError("GPU was not found on Geekbench")
        else:
            result = await self.retrieve_gpu_by_id(gpu.geekbench_id)

        gpu.model = result.name
        gpu.geekbench_id = result.geekbench_id
        gpu.geekbench_score = result.score