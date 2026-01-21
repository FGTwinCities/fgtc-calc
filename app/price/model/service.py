import datetime

from litestar.exceptions import ValidationException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.stored_pricing_model import StoredPricingModel
from app.db.repository import PricingModelRepository, provide_pricing_model_repo
from app.ebay.memory_marketstudy import run_memory_marketstudy
from app.lib.datetime import now
from app.price.model.pricing import PricingModel

MODEL_VALID_LIFESPAN = datetime.timedelta(days=7)


class PricingModelService:
    _repo: PricingModelRepository

    def __init__(self, repo: PricingModelRepository):
        self._repo = repo


    async def generate_model(self):
        model = PricingModel()
        model.memory_model = await run_memory_marketstudy()

        stored = model.to_stored()

        await self._repo.add(stored, auto_commit=True)


    async def get_model(self) -> PricingModel:
        models = await self._repo.list(
            StoredPricingModel.created_at > (now() - MODEL_VALID_LIFESPAN)
        )

        stored_model = max(models, key=lambda m: m.created_at)

        if not stored_model:
            raise ValidationException("No pricing model is available")

        return PricingModel.from_stored(stored_model)


async def provide_pricing_model_service(db_session: AsyncSession) -> PricingModelService:
    return PricingModelService(await provide_pricing_model_repo(db_session))