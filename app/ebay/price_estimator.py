import numpy as np

from app.db.model import Processor, GraphicsProcessor
from app.ebay.ebay_connection import EbayConnection
from app.ebay.exception import InsufficientResultsException
from app.ebay.util import item_has_category

MINIMUM_RESULT_COUNT = 10


class EbayPriceEstimator:
    connection: EbayConnection = EbayConnection()


    async def estimate_processor(self, processor: Processor) -> float:
        results = await self.connection.fetch_query_results(f'{processor.model} processor')

        results = list(filter(lambda i: item_has_category(i, 164), results))

        if len(results) < MINIMUM_RESULT_COUNT:
            raise InsufficientResultsException()

        prices = [float(r['price']['value']) for r in results]
        #TODO: Better outlier culling
        price = np.mean(prices)

        return round(price, 2)


    async def estimate_graphics(self, graphics: GraphicsProcessor) -> float:
        results = await self.connection.fetch_query_results(f'{graphics.model} gpu')

        results = list(filter(lambda i: item_has_category(i, 27386), results))

        if len(results) < MINIMUM_RESULT_COUNT:
            raise InsufficientResultsException()

        prices = [float(r['price']['value']) for r in results]
        #TODO: Better outlier culling
        price = np.mean(prices)

        return round(price, 2)