import asyncio
import random
from typing import AsyncGenerator

import numpy as np
from aiostream import stream
from scipy.optimize import curve_fit

from app.ebay.ebay_connection import EbayConnection
from app.ebay.storage_marketstudy import category_filter
from app.passmark.passmark_scraper import PassmarkScraper
from app.price.model.processor import ProcessorPricingModel, processor_model_func

SAMPLE_SIZE = 10


async def fetch_processor_marketdata_query(conn, query_obj, limit) -> AsyncGenerator[dict]:
    query = query_obj["name"]
    results = await conn.fetch_query_results(query, limit)
    for result in results:
        if not category_filter(result, 0):
            continue

        if result.get("price", {}).get("currency") != "USD":
            continue

        yield {
            "price": float(result.get("price", {}).get("value")),
            "score": query_obj["score"],
        }


async def run_processor_marketstudy() -> ProcessorPricingModel:
    conn = EbayConnection()

    queries = []

    # Pick SAMPLE_SIZE number of random CPUs from passmark that are socketable desktop/server CPUs
    pm = PassmarkScraper()
    full_cpu_list = await pm.search_cpu()
    for i in range(len(full_cpu_list) * 2):
        cpu = random.choice(full_cpu_list)

        details = await pm.retrieve_cpu(cpu)
        if details.cpu_class and details.socket:
            if details.cpu_class.lower() in ["desktop", "server"]:
                queries.append({"name": cpu.name, "score": details.multithread_score})

        if len(queries) > SAMPLE_SIZE:
            break

    prices = []
    scores = []

    combine = stream.merge(*[fetch_processor_marketdata_query(conn, q, 25) for q in queries])
    async with combine.stream() as streamer:
        async for data in streamer:
            prices.append(data.get("price"))
            scores.append(data.get("score"))

    prices = np.array(prices)
    scores = np.array(scores)

    popt, pcov = curve_fit(processor_model_func, scores, prices)

    model = ProcessorPricingModel()
    model.passmark_parameters = popt
    return model


if __name__ == "__main__":
    model = asyncio.run(run_processor_marketstudy())
    print("Complete")
