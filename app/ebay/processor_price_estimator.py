import os

import numpy as np
from dotenv import load_dotenv
from ebay_rest import API, Error

from app.db.model import Processor


def create_ebay_api() -> API:
    load_dotenv(override=True)

    try:
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
        return api


def removeOutliers(x, outlierConstant):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)

    result = a[np.where((a >= quartileSet[0]) & (a <= quartileSet[1]))]

    return result.tolist()


class ProcessorPriceEstimator:
    def estimate_price(self, processor: Processor) -> float:
        api = create_ebay_api()

        listed_prices = []
        for record in api.buy_browse_search(q=f'{processor.model} Processor', limit=25):
            if 'record' not in record:
                continue

            item = record['record']
            if item['price']['currency'] != 'USD':
                continue

            price_usd = item['price']['value']
            print(f'{item['title']} ({price_usd}): {item['item_web_url']}')
            listed_prices.append(float(price_usd))

        print(listed_prices)
        listed_prices = removeOutliers(listed_prices, 0.1)
        print(listed_prices)
        print(f'Average price: {np.mean(listed_prices)}')


if __name__ == "__main__":
    estimator = ProcessorPriceEstimator()
    estimator.estimate_price(Processor(
        model="Intel Core i9-14900K",
    ))