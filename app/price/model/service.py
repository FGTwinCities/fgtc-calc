from advanced_alchemy.filters import OrderBy
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.stored_pricing_model import StoredPricingModel
from app.db.repository import PricingModelRepository, provide_pricing_model_repo
from app.ebay.memory_marketstudy import run_memory_marketstudy
from app.price.model.pricing import PricingModel


class PricingModelService:
    _repo: PricingModelRepository

    def __init__(self, repo: PricingModelRepository):
        self._repo = repo


    async def generate_model(self):
        memory = await run_memory_marketstudy()

        stored = StoredPricingModel()
        stored.memory_param_a = memory.parameters[0]
        stored.memory_param_b = memory.parameters[1]
        stored.memory_param_c = memory.parameters[2]
        stored.memory_param_d = memory.parameters[3]
        stored.memory_param_e = memory.parameters[4]

        await self._repo.add(stored, auto_commit=True)


    async def get_model(self) -> PricingModel:
        stored_model = await self._repo.get_one(
            OrderBy(StoredPricingModel.created_at),
        )

        return await PricingModel.from_stored(stored_model)


async def provide_pricing_model_service(db_session: AsyncSession) -> PricingModelService:
    return PricingModelService(await provide_pricing_model_repo(db_session))