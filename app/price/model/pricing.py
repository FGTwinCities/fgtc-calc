from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.price.model.battery import BatteryPricingModel, provide_battery_pricing_model
from app.price.model.display import DisplayPricingModel, provide_display_pricing_model
from app.price.model.memory import MemoryPricingModel, provide_memory_pricing_model
from app.price.model.storage import StoragePricingModel, provide_storage_pricing_model


class PricingModel:
    adjustment: Polynomial = Polynomial([0, 1, 0])

    def compute_adjustment(self, price: float) -> float:
        return self.adjustment(price)

    memory_model: MemoryPricingModel
    storage_model: StoragePricingModel
    display_model: DisplayPricingModel
    battery_model: BatteryPricingModel


async def provide_default_pricing_model(db_session: AsyncSession) -> PricingModel:
    model = PricingModel()
    model.adjustment = Polynomial([0, 0.5, 0])
    model.memory_model = await provide_memory_pricing_model(db_session)
    model.storage_model = await provide_storage_pricing_model(db_session)
    model.display_model = await provide_display_pricing_model(db_session)
    model.battery_model = await provide_battery_pricing_model(db_session)
    return model
