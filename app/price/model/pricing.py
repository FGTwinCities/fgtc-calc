from numpy.polynomial.polynomial import Polynomial

from app.db.model.build import Build
from app.db.model.stored_pricing_model import StoredPricingModel
from app.price.dto import BuildPrice, PriceAdjustment, WithPrice
from app.price.model.battery import BatteryPricingModel
from app.price.model.display import DisplayPricingModel
from app.price.model.graphics import GraphicsProcessorPricingModel
from app.price.model.memory import MemoryPricingModel
from app.price.model.processor import ProcessorPricingModel
from app.price.model.storage import StoragePricingModel


class PricingModel:
    adjustment: Polynomial = Polynomial([0, 0.75, 0])

    def compute_adjustment(self, price: float) -> float:
        return self.adjustment(price)

    processor_model: ProcessorPricingModel = ProcessorPricingModel()
    graphics_model: GraphicsProcessorPricingModel = GraphicsProcessorPricingModel()
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

        for submodule in submodule_prices:
            price += submodule.price
            debug.append(submodule)

        adjusted = self.compute_adjustment(price)
        debug.append(PriceAdjustment(price=adjusted - price, comment="Store Adjustment"))
        price = adjusted

        submodule_prices = []
        for display in build.display:
            submodule_prices.append(WithPrice(item=display, price=self.display_model.compute(display)))

        for battery in build.batteries:
            submodule_prices.append(WithPrice(item=battery, price=self.battery_model.compute(battery)))

        for submodule in submodule_prices:
            price += submodule.price
            debug.append(submodule)

        return BuildPrice(
            price=round(price, 2),
            component_pricing=debug,
        )

    @classmethod
    def from_stored(cls, stored_model: StoredPricingModel):
        model = PricingModel()

        model.processor_model = ProcessorPricingModel()
        model.processor_model.passmark_parameters = (
            stored_model.processor_param_a,
            stored_model.processor_param_b,
        )

        model.graphics_model = GraphicsProcessorPricingModel()
        model.graphics_model.passmark_parameters = (
            stored_model.graphics_param_a,
            stored_model.graphics_param_b,
        )

        model.memory_model = MemoryPricingModel()
        model.memory_model.parameters = (
            stored_model.memory_param_a,
            stored_model.memory_param_b,
            stored_model.memory_param_c,
            stored_model.memory_param_d,
            stored_model.memory_param_e,
        )

        model.storage_model = StoragePricingModel()
        model.storage_model.hdd_parameters = (
            stored_model.storage_hdd_param_a,
            stored_model.storage_hdd_param_b,
            stored_model.storage_hdd_param_c,
        )
        model.storage_model.sata_ssd_parameters = (
            stored_model.storage_sata_ssd_param_a,
            stored_model.storage_sata_ssd_param_b,
            stored_model.storage_sata_ssd_param_c,
        )
        model.storage_model.nvme_ssd_parameters = (
            stored_model.storage_nvme_ssd_param_a,
            stored_model.storage_nvme_ssd_param_b,
            stored_model.storage_nvme_ssd_param_c,
        )

        return model

    def to_stored(self) -> StoredPricingModel:
        stored = StoredPricingModel()

        stored.processor_param_a = self.processor_model.passmark_parameters[0]
        stored.processor_param_b = self.processor_model.passmark_parameters[1]

        stored.graphics_param_a = self.graphics_model.passmark_parameters[0]
        stored.graphics_param_b = self.graphics_model.passmark_parameters[1]

        stored.memory_param_a = self.memory_model.parameters[0]
        stored.memory_param_b = self.memory_model.parameters[1]
        stored.memory_param_c = self.memory_model.parameters[2]
        stored.memory_param_d = self.memory_model.parameters[3]
        stored.memory_param_e = self.memory_model.parameters[4]

        stored.storage_hdd_param_a = self.storage_model.hdd_parameters[0]
        stored.storage_hdd_param_b = self.storage_model.hdd_parameters[1]
        stored.storage_hdd_param_c = self.storage_model.hdd_parameters[2]
        stored.storage_sata_ssd_param_a = self.storage_model.sata_ssd_parameters[0]
        stored.storage_sata_ssd_param_b = self.storage_model.sata_ssd_parameters[1]
        stored.storage_sata_ssd_param_c = self.storage_model.sata_ssd_parameters[2]
        stored.storage_nvme_ssd_param_a = self.storage_model.nvme_ssd_parameters[0]
        stored.storage_nvme_ssd_param_b = self.storage_model.nvme_ssd_parameters[1]
        stored.storage_nvme_ssd_param_c = self.storage_model.nvme_ssd_parameters[2]

        return stored
