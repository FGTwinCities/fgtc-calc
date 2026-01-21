from numpy.polynomial.polynomial import Polynomial

from app.db.model.build import Build
from app.db.model.stored_pricing_model import StoredPricingModel
from app.price.dto import BuildPrice, PriceAdjustment, WithPrice
from app.price.model.battery import BatteryPricingModel, provide_battery_pricing_model
from app.price.model.display import DisplayPricingModel, provide_display_pricing_model
from app.price.model.memory import MemoryPricingModel
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
                debug.append(WithPrice(item=processor, price=processor.price))

        for gpu in build.graphics:
            if gpu.price:
                price += gpu.price
                debug.append(WithPrice(item=gpu, price=gpu.price))


        submodule_prices = []
        for mem in build.memory:
            submodule_prices.append(WithPrice(item=mem, price=self.memory_model.compute(mem)))

        for disk in build.storage:
            submodule_prices.append(WithPrice(item=disk, price=self.storage_model.compute(disk)))

        for display in build.display:
            submodule_prices.append(WithPrice(item=display, price=self.display_model.compute(display)))

        for battery in build.batteries:
            submodule_prices.append(WithPrice(item=battery, price=self.battery_model.compute(battery)))

        for submodule in submodule_prices:
            price += submodule.price
            debug.append(submodule)

        adjusted = self.compute_adjustment(price)
        debug.append(PriceAdjustment(price=adjusted-price, comment="Store Adjustment"))
        price = round(adjusted, 2)

        return BuildPrice(
            price=price,
            component_pricing=debug,
        )

    @classmethod
    async def from_stored(cls, stored_model: StoredPricingModel):
        model = PricingModel()

        model.memory_model = MemoryPricingModel()
        model.memory_model.parameters = (
            stored_model.memory_param_a,
            stored_model.memory_param_b,
            stored_model.memory_param_c,
            stored_model.memory_param_d,
            stored_model.memory_param_e,
        )

        model.storage_model = await provide_storage_pricing_model(None)
        model.display_model = await provide_display_pricing_model(None)
        model.battery_model = await provide_battery_pricing_model(None)

        return model
