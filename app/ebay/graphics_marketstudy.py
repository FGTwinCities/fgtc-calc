import random
from typing import AsyncGenerator

import numpy as np
from aiostream import stream
from scipy.optimize import curve_fit

from app.ebay.ebay_connection import EbayConnection
from app.ebay.util import item_has_category
from app.passmark.passmark_scraper import PassmarkScraper
from app.price.model.graphics import GraphicsProcessorPricingModel, graphics_model_func

GPU_SAMPLE_SIZE = 25
SAMPLE_SIZE_PER_GPU = 50


async def _fetch_graphics_marketdata_query(conn, query_obj, limit) -> AsyncGenerator[dict]:
    query = query_obj["name"]
    results = await conn.fetch_query_results(query, limit)
    for result in results:
        if not item_has_category(result, 27386):
            continue

        if result.get("price", {}).get("currency") != "USD":
            continue

        yield {
            "price": float(result.get("price", {}).get("value")),
            "score": query_obj["score"],
        }


async def run_graphics_marketstudy() -> GraphicsProcessorPricingModel:
    conn = EbayConnection()
    pm = PassmarkScraper()

    queries = [
        "GeForce GTX",
        "GeForce RTX",
        "Intel Arc",
        "Radeon RX",
    ]

    query_candidates = []
    for query in queries:
        gpu_result = await pm.search_gpu(query)
        query_candidates.extend(gpu_result)

    query_objects = []
    random.shuffle(query_candidates)
    for result in query_candidates:
        result = await pm.retrieve_gpu(result)
        if result.gpu_category:
            if result.gpu_category.lower() in ["desktop", "server", "workstation"]:
                query_objects.append({"name": result.name, "score": result.score})

        if len(query_objects) >= GPU_SAMPLE_SIZE:
            break

    prices = []
    scores = []

    combine = stream.merge(*[_fetch_graphics_marketdata_query(conn, q, SAMPLE_SIZE_PER_GPU) for q in query_objects])
    async with combine.stream() as streamer:
        async for data in streamer:
            prices.append(data.get("price"))
            scores.append(data.get("score"))

    prices = np.array(prices)
    scores = np.array(scores)

    popt, pcov = curve_fit(graphics_model_func, scores, prices)

    model = GraphicsProcessorPricingModel()
    model.passmark_parameters = popt
    return model