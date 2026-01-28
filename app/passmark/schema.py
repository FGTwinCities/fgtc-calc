from dataclasses import dataclass


@dataclass
class PassmarkSearchResult:
    name: str = None
    passmark_id: int = None
    multithread_score: int = None


@dataclass
class PassmarkCpuDetails(PassmarkSearchResult):
    cpu_class: str = None
    socket: str = None
    single_thread_score: int = None


@dataclass
class PassmarkCoreDetails:
    cores: int = None
    threads: int = None
    clock: float = None
    turbo_clock: float = None


@dataclass
class PassmarkStandardCpuDetails(PassmarkCoreDetails, PassmarkCpuDetails):
    pass


@dataclass
class PassmarkPECoreCpuDetails(PassmarkCpuDetails):
    performance_cores: PassmarkCoreDetails = None
    efficient_cores: PassmarkCoreDetails = None