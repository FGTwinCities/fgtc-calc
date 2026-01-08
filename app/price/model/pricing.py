from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.build import Build
from app.price.dto import BuildPrice, MemoryModulePrice, StorageDiskPrice, DisplayPrice, BatteryPrice, PriceAdjustment
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

    async def compute(self, build: Build) -> BuildPrice:
        debug = []
        price = 0

        for processor in build.processors:
            if processor.price:
                price += processor.price
                debug.append({"price": processor.price, "processor": processor})

        for gpu in build.graphics:
            if gpu.price:
                price += gpu.price
                debug.append({"price": gpu.price, "graphics": gpu})


        submodule_prices = []
        for mem in build.memory:
            submodule_prices.append(MemoryModulePrice(module=mem, price=self.memory_model.compute(mem)))

        for disk in build.storage:
            submodule_prices.append(StorageDiskPrice(disk=disk, price=self.storage_model.compute(disk)))

        for display in build.display:
            submodule_prices.append(DisplayPrice(display=display, price=self.display_model.compute(display)))

        for battery in build.batteries:
            submodule_prices.append(BatteryPrice(battery=battery, price=self.battery_model.compute(battery)))

        for submodule in submodule_prices:
            price += submodule.price
            debug.append(submodule)

        adjusted = self.compute_adjustment(price)
        debug.append(PriceAdjustment(price=adjusted-price, comment="Store Adjustment"))
        price = adjusted

        return BuildPrice(
            price=price,
            component_pricing=debug,
        )


async def provide_default_pricing_model(db_session: AsyncSession) -> PricingModel:
    model = PricingModel()
    model.adjustment = Polynomial([0, 0.5, 0])
    model.memory_model = await provide_memory_pricing_model(db_session)
    model.storage_model = await provide_storage_pricing_model(db_session)
    model.display_model = await provide_display_pricing_model(db_session)
    model.battery_model = await provide_battery_pricing_model(db_session)
    return model
