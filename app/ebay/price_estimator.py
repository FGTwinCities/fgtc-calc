import re

import numpy as np

from app.db.enum import BuildType
from app.db.model import Processor, GraphicsProcessor, MacBuild
from app.ebay.ebay_connection import EbayConnection
from app.ebay.exception import InsufficientResultsException
from app.ebay.util import item_has_category, cull_outliers_1d
from app.lib.math import mb2gb

MINIMUM_RESULT_COUNT = 10


class EbayPriceEstimator:
    connection: EbayConnection = EbayConnection()


    async def estimate_processor(self, processor: Processor) -> float:
        results = await self.connection.fetch_query_results(f'{processor.model} processor')

        results = list(filter(lambda i: item_has_category(i, 164), results))

        if len(results) < MINIMUM_RESULT_COUNT:
            raise InsufficientResultsException()

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers_1d(np.array(prices))
        price = np.mean(prices)

        return round(price, 2)


    async def estimate_graphics(self, graphics: GraphicsProcessor) -> float:
        results = await self.connection.fetch_query_results(f'{graphics.model} gpu')

        results = list(filter(lambda i: item_has_category(i, 27386), results))

        if len(results) < MINIMUM_RESULT_COUNT:
            raise InsufficientResultsException()

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers_1d(np.array(prices))
        price = np.mean(prices)

        return round(price, 2)

    async def estimate_mac_build(self, mac: MacBuild) -> float:
        # Get and convert the processor model to "Core i5" or "M3 Max" form
        assert len(mac.processors) >= 1
        processor = mac.processors[0].model
        if m := re.search(r'(i\d)[-_\s]*(\d+)(\w*)', processor):
            processor = f"Core {m.group(1)}"
        elif m := re.search(r'm(\d+)[-_\s]*([mpu][arl][xot]r?a?)?', processor):
            processor = f"M{m.group(1).upper()} {(m.group(2) or "").title()}"

        processor = re.sub(r'\s{2,}', ' ', processor)

        # Get the total system memory in GB
        assert len(mac.memory) >= 1
        total_memory = sum([m.size for m in mac.memory])
        memory_gb = mb2gb(total_memory)

        # Get boot disk size in GB
        assert len(mac.storage) >= 1
        storage_gb = mb2gb(mac.storage[0].size)

        # Format eBay query string
        query_str: str
        match mac.type:
            case BuildType.LAPTOP:
                query_str = f"{mac.year} {mac.mac_type} {mac.display[0].size:g} {processor} {memory_gb:.0f}GB {storage_gb:.0f}GB"
            case _:
                query_str = f"{mac.year} {mac.mac_type} {processor} {memory_gb}GB {storage_gb}GB"

        results = await self.connection.fetch_query_results(query_str, limit=100)
        results = list(filter(lambda i: item_has_category(i, 111422), results))

        if len(results) < MINIMUM_RESULT_COUNT:
            raise InsufficientResultsException()

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers_1d(np.array(prices))
        price = np.mean(prices)

        return round(price, 2)
