import os

from dotenv import load_dotenv
from ebay_rest import API, Error
from ebay_rest.api.buy_browse.rest import ApiException


class EbayConnection:
	_api: API = None

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


	async def fetch_item(self, item: dict | str) -> dict:
		item_id = None
		if isinstance(item, str):
			item_id = item
		else:
			item_id = item.get("item_id", None)

		if item_id is None:
			raise AttributeError("provided item does not contain item_id")

		api = self._get_api()
		return api.buy_browse_get_item(item_id)

	async def fetch_item_or_none(self, item: dict | str) -> dict | None:
		try:
			return await self.fetch_item(item)
		except ApiException:
			return None