import datetime

from advanced_alchemy.extensions.litestar.providers import create_service_provider
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from litestar.exceptions import ValidationException
from saq.types import Context

from app.db import model as m
from app.db.model.stored_pricing_model import StoredPricingModel
from app.ebay.memory_marketstudy import run_memory_marketstudy
from app.ebay.processor_marketstudy import run_processor_marketstudy
from app.ebay.storage_marketstudy import run_storage_marketstudy
from app.lib.datetime import now
from app.lib.deps import provide_services
from app.price.model.pricing import PricingModel

MODEL_VALID_LIFESPAN = datetime.timedelta(days=7)

class PricingModelService(SQLAlchemyAsyncRepositoryService[m.StoredPricingModel]):

    class Repository(SQLAlchemyAsyncRepository[m.StoredPricingModel]):
        model_type = m.StoredPricingModel

    repository_type = Repository

    async def generate_model(self):
        model = PricingModel()

        #TODO: Parallelism, as SAQ jobs?
        print("Starting processor marketstudy...")
        model.processor_model = await run_processor_marketstudy()
        print("Starting memory marketstudy...")
        model.memory_model = await run_memory_marketstudy()
        print("Starting storage marketstudy...")
        model.storage_model = await run_storage_marketstudy()

        stored = model.to_stored()

        await self.create(stored, auto_commit=True)


    async def get_model(self) -> PricingModel:
        models = await self.list(
            StoredPricingModel.created_at > (now() - MODEL_VALID_LIFESPAN)
        )

        if len(models) <= 0:
            raise ValidationException("No pricing model is available")

        stored_model = max(models, key=lambda m: m.created_at)

        return PricingModel.from_stored(stored_model)


provide_pricing_model_service = create_service_provider(PricingModelService)

async def generate_pricing_model_job(_: Context) -> None:
    async with provide_services(provide_pricing_model_service) as (pricing_model_service,):
        await pricing_model_service.generate_model()