from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.battery import Battery


class BatteryPricingModel:
    capacity_ratio_func: Polynomial

    def compute(self, battery: Battery) -> float:
        return self.capacity_ratio_func(battery.remaining_capacity / battery.design_capacity)


async def provide_battery_pricing_model(db_session: AsyncSession) -> BatteryPricingModel:
    model = BatteryPricingModel()
    model.capacity_ratio_func = Polynomial([0, -30, 0])
    return model