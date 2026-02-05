import numpy as np

from app.db.model import Processor, GraphicsProcessor
from app.ebay.ebay_connection import EbayConnection
from app.ebay.util import cull_outliers, item_has_category


class EbayPriceEstimator:
    connection: EbayConnection = EbayConnection()


    async def estimate_processor(self, processor: Processor) -> float:
        results = await self.connection.fetch_query_results(f'{processor.model} processor')

        results = filter(lambda i: item_has_category(i, 164), results)

        prices = [float(r['price']['value']) for r in results]
        #TODO: Better outlier culling
        price = np.mean(prices)

        return round(price, 2)


    async def estimate_graphics(self, graphics: GraphicsProcessor) -> float:
        results = await self.connection.fetch_query_results(f'{graphics.model} gpu')

        results = filter(lambda i: item_has_category(i, 27386), results)

        prices = [float(r['price']['value']) for r in results]
        #TODO: Better outlier culling
        price = np.mean(prices)

        return round(price, 2)