import os

import numpy as np
from dotenv import load_dotenv
from ebay_rest import API, Error

from app.db.model import Processor, GraphicsProcessor
from app.ebay.ebay_connection import EbayConnection
from app.price.model.pricing import PricingModel


def cull_outliers(x, outlierConstant):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)

    result = a[np.where((a >= quartileSet[0]) & (a <= quartileSet[1]))]

    return result.tolist()


def item_has_category(item, category_id) -> bool:
    for category in item['categories']:
        if category['category_id'] == str(category_id):
            return True

    return False


class EbayPriceEstimator:
    connection: EbayConnection = EbayConnection()


    async def estimate_processor(self, processor: Processor) -> float:
        results = await self.connection.fetch_query_results(f'{processor.model} processor')

        results = filter(lambda i: item_has_category(i, 164), results)

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers(prices, 0.1)
        price = np.mean(prices)

        return round(price, 2)


    async def estimate_graphics(self, graphics: GraphicsProcessor) -> float:
        results = await self.connection.fetch_query_results(f'{graphics.model} gpu')

        results = filter(lambda i: item_has_category(i, 27386), results)

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers(prices, 0.1)
        price = np.mean(prices)

        return round(price, 2)