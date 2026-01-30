from abc import ABC, abstractmethod

from app.db.model import Processor, GraphicsProcessor
from app.extern.benchmark.schema import BenchmarkComponentResult


class BenchmarkDataSource(ABC):
    @abstractmethod
    async def retrieve_cpu_list(self) -> list[BenchmarkComponentResult]:
        raise NotImplemented

    @abstractmethod
    async def retrieve_gpu_list(self) -> list[BenchmarkComponentResult]:
        raise NotImplemented

    @abstractmethod
    async def search_cpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        raise NotImplemented

    @abstractmethod
    async def find_cpu(self, query: str) -> BenchmarkComponentResult | None:
        raise NotImplemented

    @abstractmethod
    async def search_gpu(self, query: str = None) -> list[BenchmarkComponentResult]:
        raise NotImplemented

    @abstractmethod
    async def find_gpu(self, query: str) -> BenchmarkComponentResult | None:
        raise NotImplemented

    @abstractmethod
    async def update_cpu(self, processor: Processor, rebind: bool = False) -> None:
        raise NotImplemented

    @abstractmethod
    async def update_gpu(self, gpu: GraphicsProcessor, rebind: bool = False) -> None:
        raise NotImplemented