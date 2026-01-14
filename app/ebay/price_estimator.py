import os

import numpy as np
from dotenv import load_dotenv
from ebay_rest import API, Error
from litestar.di import Provide

from app.db.model import Processor, GraphicsProcessor
from app.price.model.pricing import PricingModel, provide_default_pricing_model


def create_ebay_api() -> API:
    load_dotenv(override=True)


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
    _api: API = None
    _pricing_model: PricingModel = None

    def __init__(self, pricing_model: PricingModel):
        self._pricing_model = pricing_model


    def _get_api(self):
        if not self._api:
            try:
                load_dotenv()

                api = API(application={
                    "app_id": os.getenv("EBAY_APP_ID"),
                    "dev_id": os.getenv("EBAY_DEV_ID"),
                    "cert_id": os.getenv("EBAY_SECRET"),
                    "redirect_uri": os.getenv("EBAY_REDIRECT"),
                }, user={
                    "email_or_username": os.getenv("EBAY_USERNAME"),
                    "password": os.getenv("EBAY_PASSWORD"),
                    "scopes": [
                        "https://api.ebay.com/oauth/api_scope",
                        "https://api.ebay.com/oauth/api_scope/sell.inventory"
                    ],
                    "refresh_token": "",
                    "refresh_token_expiry": ""
                }, header={
                    "accept_language": "en-US",
                    "affiliate_campaign_id": "",
                    "affiliate_reference_id": "",
                    "content_language": "en-US",
                    "country": "US",
                    "currency": "USD",
                    "device_id": "",
                    "marketplace_id": "EBAY_US",
                    "zip": "20500"
                })
            except Error as e:
                print(f'Error {e.number} is {e.reason}  {e.detail}.\n')
                raise RuntimeError("Failed to authenticate with eBay API")
            else:
                self._api = api
                return api
        else:
            return self._api


    async def estimate_processor(self, processor: Processor) -> float:
        results = await self.fetch_query_results(f'{processor.model} processor')

        results = filter(lambda i: item_has_category(i, 164), results)

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers(prices, 0.1)
        price = round(np.mean(prices), 2)

        price = self._pricing_model.compute_adjustment(price)

        return price


    async def estimate_graphics(self, graphics: GraphicsProcessor) -> float:
        results = await self.fetch_query_results(f'{graphics.model} gpu')

        results = filter(lambda i: item_has_category(i, 27386), results)

        prices = [float(r['price']['value']) for r in results]
        prices = cull_outliers(prices, 0.1)
        price = round(np.mean(prices), 2)

        price = self._pricing_model.compute_adjustment(price)

        return price


    async def fetch_query_results(self, query: str, limit: int = 25) -> list:
        api = self._get_api()

        filters = []
        buying_option = "FIXED_PRICE"
        filters.append("buyingOptions:{" + buying_option + "}")
        currency = "USD"
        filters.append(f"priceCurrency:{currency}")
        filter_ = ",".join(filters)

        items = []
        for record in api.buy_browse_search(q=query, limit=limit, filter=filter_):
            if 'record' not in record:
                continue

            item = record['record']
            if item['price']['currency'] != 'USD':
                continue

            items.append(item)

        return items