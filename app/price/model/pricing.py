from numpy.polynomial.polynomial import Polynomial

from app.db.model.build import Build
from app.db.model.stored_pricing_model import StoredPricingModel
from app.price.dto import BuildPrice, PriceAdjustment, WithPrice
from app.price.model.battery import BatteryPricingModel
from app.price.model.display import DisplayPricingModel
from app.price.model.memory import MemoryPricingModel
from app.price.model.storage import StoragePricingModel


class PricingModel:
    adjustment: Polynomial = Polynomial([0, 1, 0])

    def compute_adjustment(self, price: float) -> float:
        return self.adjustment(price)

    memory_model: MemoryPricingModel = MemoryPricingModel()
    storage_model: StoragePricingModel = StoragePricingModel()
    display_model: DisplayPricingModel = DisplayPricingModel()
    battery_model: BatteryPricingModel = BatteryPricingModel()

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
    def from_stored(cls, stored_model: StoredPricingModel):
        model = PricingModel()

        model.memory_model = MemoryPricingModel()
        model.memory_model.parameters = (
            stored_model.memory_param_a,
            stored_model.memory_param_b,
            stored_model.memory_param_c,
            stored_model.memory_param_d,
            stored_model.memory_param_e,
        )

        return model

    def to_stored(self) -> StoredPricingModel:
        stored = StoredPricingModel()

        stored.memory_param_a = self.memory_model.parameters[0]
        stored.memory_param_b = self.memory_model.parameters[1]
        stored.memory_param_c = self.memory_model.parameters[2]
        stored.memory_param_d = self.memory_model.parameters[3]
        stored.memory_param_e = self.memory_model.parameters[4]

        return stored
