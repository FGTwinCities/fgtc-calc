from typing import List

from litestar import get
from litestar.controller import Controller

from app.db.service.pricing import PricingModelService, PricingModelUnavailableException
from app.status.schema import StatusMessage


class StatusController(Controller):
    path = "status"

    @get("/messages")
    async def get_status_messages(self, pricing_model_service: PricingModelService) -> List[StatusMessage]:
        messages: List[StatusMessage] = []

        try:
            await pricing_model_service.get_model()
        except PricingModelUnavailableException:
            messages.append(StatusMessage(
                "No valid pricing model is available! Automatic pricing will not work until one is generated.",
            ))

        if await pricing_model_service.is_model_generating():
            messages.append(StatusMessage(
                "A new pricing model is currently being generated. For best results, please wait to generate build prices.",
            ))

        return messages
