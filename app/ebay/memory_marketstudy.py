import asyncio
import re

from app.ebay.ebay_connection import EbayConnection
from app.lib.math import gb2mb, tb2mb
from app.price.model.memory import MemoryPricingModel


def parse_memory_speed(speed_string: str) -> int | None:
	res = re.search(r'[Pp][Cc]\d-(\d+)', speed_string)
	return round(int(res.group(1)) / 8)


def parse_capacity(capacity_string: str) -> int | None:
	res = re.search(r'(\d+)\s*([MmGgTt][Bb])', capacity_string)
	value = int(res.group(1))
	unit = res.group(2).lower()

	if 'm' in unit:
		pass
	elif 'g' in unit:
		value = gb2mb(value)
	elif 't' in unit:
		value = tb2mb(value)
	else:
		return None

	return round(value)

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


async def run_memory_marketstudy() -> MemoryPricingModel:
	conn = EbayConnection()
	
	results = await conn.fetch_query_results("DDR4", 10)
	for item in asyncio.as_completed([conn.fetch_item(r) for r in results]):
		print(parse_memory_aspects((await item).get("localized_aspects")))


if __name__ == "__main__":
	asyncio.run(run_memory_marketstudy())