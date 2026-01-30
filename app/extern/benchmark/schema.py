from dataclasses import dataclass


@dataclass
class BenchmarkComponentResult:
    name: str = None
    score: int = None