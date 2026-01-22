import asyncio
from typing import AsyncGenerator

import numpy as np
from aiostream import stream
from scipy.optimize import curve_fit

from app.ebay.ebay_connection import EbayConnection
from app.ebay.util import parse_capacity
from app.lib.util import try_int
from app.price.model.storage import StoragePricingModel, storage_model_func

MAX_STORAGE_PRICE_PER_MB: float = 0.0005


def parse_disk_aspects(aspects: list) -> dict:
    result = {}
    if not aspects:
        return result

    for aspect in aspects:
        key = aspect.get("name", "").lower()
        val = aspect.get("value")
        if key == "storage capacity":
            result["capacity"] = parse_capacity(val)

        if key == "unit quantity":
            result["disk_count "] = try_int(val)

    return result


async def fetch_disk_marketdata_query(conn: EbayConnection, query: str, limit: int, filter_func) -> AsyncGenerator[dict]:
    results = await conn.fetch_query_results(query, limit)
    for item in asyncio.as_completed([conn.fetch_item_or_none(r) for r in results]):
        item = await item

        if item is None:
            continue

        if not filter_func(item):
            continue

        try:
            aspects = parse_disk_aspects(item.get("localized_aspects"))
        except ValueError:
            continue

        if None in [aspects.get("capacity")]:
            continue

        # Remove any items that are not priced in USD
        if item.get("price", {}).get("currency") != "USD":
            continue

        disk_price = float(item.get("price", {}).get("value"))
        disk_price /= aspects.get("disk_count", 1)

        if disk_price / aspects.get("capacity") > MAX_STORAGE_PRICE_PER_MB:
            continue

        yield {
            "price": disk_price,
            "capacity": aspects.get("capacity"),
        }


async def disk_marketstudy(conn: EbayConnection, queries: list, limit: int, filter_func) -> tuple[float, float, float]:
    capacities = []
    prices = []

    combine = stream.merge(*[fetch_disk_marketdata_query(conn, q, limit, filter_func) for q in queries])
    async with combine.stream() as streamer:
        async for data in streamer:
            capacities.append(data.get("capacity"))
            prices.append(data.get("price"))

    capacities = np.array(capacities)
    prices = np.array(prices)

    popt, pcov = curve_fit(storage_model_func, capacities, prices)

    return popt

def category_filter(item: dict, category_id: int) -> bool:
    return int(item.get("category_id")) == category_id


def interface_filter(item: dict, interface: str) -> bool:
    for aspect in item.get("localized_aspects", []):
        if aspect.get("name", "").lower() == "interface":
            if interface.lower() in aspect.get("value", "").lower():
                return True
    return False


def filter_hard_dries(item: dict) -> bool:
    return category_filter(item, 56083)


def filter_sata_ssd(item: dict) -> bool:
    return category_filter(item, 175669) and interface_filter(item, "sata")


def filter_nvme_ssd(item: dict) -> bool:
    return category_filter(item, 175669) and interface_filter(item, "nvme")


async def run_storage_marketstudy() -> StoragePricingModel:
    conn = EbayConnection()

    model = StoragePricingModel()
    model.hdd_parameters = await disk_marketstudy(conn, ["4TB Hard Drive", "1TB Hard Drive", "512GB Hard Drive"], 25, filter_hard_dries)
    model.sata_ssd_parameters = await disk_marketstudy(conn, ["1TB SATA SSD", "512GB SATA SSD", "128GB SATA SSD"], 25, filter_sata_ssd)
    model.nvme_ssd_parameters = await disk_marketstudy(conn, ["1TB NVMe SSD", "512GB NVMe SSD", "128GB NVMe SSD"], 25, filter_nvme_ssd)

    return model


if __name__ == "__main__":
    model = asyncio.run(run_storage_marketstudy())
    print("done")