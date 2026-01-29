import asyncio
import random
from typing import AsyncGenerator

import numpy as np
from aiostream import stream
from scipy.optimize import curve_fit

from app.db.model import Processor
from app.ebay.ebay_connection import EbayConnection
from app.ebay.util import item_has_category
from app.passmark.passmark_scraper import PassmarkScraper
from app.price.model.processor import ProcessorPricingModel, processor_model_func

PROCESSOR_SAMPLE_SIZE = 25
SAMPLE_SIZE_PER_PROCESSOR = 50


async def fetch_processor_marketdata_query(conn, query_obj, limit) -> AsyncGenerator[dict]:
    query = query_obj["name"]
    results = await conn.fetch_query_results(query, limit)
    for result in results:
        if not item_has_category(result, 164):
            continue

        if result.get("price", {}).get("currency") != "USD":
            continue

        yield {
            "price": float(result.get("price", {}).get("value")),
            "score": query_obj["score"],
        }


async def run_processor_marketstudy() -> ProcessorPricingModel:
    conn = EbayConnection()
    pm = PassmarkScraper()

    queries = [
        "Intel Core i",
        "Intel Core Ultra",
        "AMD Ryzen",
    ]

    cpu_query_candidates = []
    for query in queries:
        cpu_results = await pm.search_cpu(query)
        cpu_query_candidates.extend(cpu_results)

    query_objects = []
    random.shuffle(cpu_query_candidates)
    for cpu_result in cpu_query_candidates:
        query_objects.append({"name": cpu_result.name, "score": cpu_result.score})

        if len(query_objects) >= PROCESSOR_SAMPLE_SIZE:
            break

    prices = []
    scores = []

    combine = stream.merge(*[fetch_processor_marketdata_query(conn, q, SAMPLE_SIZE_PER_PROCESSOR) for q in query_objects])
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
