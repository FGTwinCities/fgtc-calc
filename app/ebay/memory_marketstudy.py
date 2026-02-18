import asyncio
import re
from typing import AsyncGenerator

import numpy as np
from aiostream import stream
from scipy.optimize import curve_fit

from app.db.enum import MemoryType
from app.db.model import MemoryModule
from app.ebay.ebay_connection import EbayConnection
from app.ebay.storage_marketstudy import item_has_category
from app.ebay.util import parse_capacity
from app.price.model.memory import MemoryPricingModel, memory_model_func

MAX_MEMORY_PRICE_PER_MB = 0.08


def parse_memory_speed(speed_string: str) -> int | None:
	res = re.search(r'[Pp][Cc]\d-(\d+)', speed_string)

	if not res:
		return None

	return round(int(res.group(1)) / 8)


def parse_memory_aspects(aspects: list) -> dict:
	result = {}
	for aspect in aspects:
		key = aspect.get("name").lower()
		val = aspect.get("value")
		if key == "capacity per module":
			result["module_capacity"] = parse_capacity(val)

		if key == "total capacity":
			result["total_capacity"] = parse_capacity(val)

		if key == "number of modules":
			result["module_count"] = int(val)

		if key == "bus speed":
			result["speed"] = parse_memory_speed(val)

	return result


async def fetch_memory_marketdata_query(conn: EbayConnection, query: str, limit: int) -> AsyncGenerator[dict]:
	results = await conn.fetch_query_results(query, limit)
	for item in asyncio.as_completed([conn.fetch_item_or_none(r) for r in results]):
		item = await item

		if item is None:
			continue

		if not item_has_category(item, 170083):
			continue

		try:
			aspects = parse_memory_aspects(item.get("localized_aspects"))
		except ValueError:
			continue

		# Remove any items that dont have required specs listed in aspects
		if None in [aspects.get("module_capacity"), aspects.get("speed")]:
			continue

		# Remove any items that are not priced in USD
		if item.get("price", {}).get("currency") != "USD":
			continue

		try:
			module_price = float(item.get("price", {}).get("value"))
			module_price /= aspects.get("module_count", 1)

			if module_price / aspects.get("module_capacity") > MAX_MEMORY_PRICE_PER_MB:
				continue
		except ZeroDivisionError:
			continue

		yield {
			# "listing": itm,
			"price": module_price,
			"capacity": aspects.get("module_capacity"),
			"speed": aspects.get("speed"),
		}


async def run_memory_marketstudy() -> MemoryPricingModel:
	conn = EbayConnection()

	queries = [
		"DDR3",
		"DDR4",
		"DDR5",
	]

	capacities = []
	speeds = []
	prices = []

	combine = stream.merge(*[fetch_memory_marketdata_query(conn, query, 50) for query in queries])
	async with combine.stream() as streamer:
		async for data in streamer:
			capacities.append(data.get("capacity"))
			speeds.append(data.get("speed"))
			prices.append(data.get("price"))

	capacities = np.array(capacities)
	speeds = np.array(speeds)
	prices = np.array(prices)

	popt, pcov = curve_fit(memory_model_func, (capacities, speeds), prices)

	model = MemoryPricingModel()
	model.parameters = popt
	return model


if __name__ == "__main__":
	model = asyncio.run(run_memory_marketstudy())

	price = model.compute(MemoryModule(
		type=MemoryType.DDR4,
		clock=3600,
		size=16000,
	))

	print(f'Price for 16GB of DDR4@3600: {price}')