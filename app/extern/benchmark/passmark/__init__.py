from app.extern.benchmark.passmark.schema import PassmarkSearchResult, PassmarkCpuDetails, PassmarkStandardCpuDetails, \
    PassmarkPECoreCpuDetails, PassmarkGpuDetails
from app.extern.benchmark.passmark.passmark_scraper import PassmarkScraper

__all__ = [
    "PassmarkScraper",
    "PassmarkSearchResult",
    "PassmarkCpuDetails",
    "PassmarkStandardCpuDetails",
    "PassmarkPECoreCpuDetails",
    "PassmarkGpuDetails",
]
