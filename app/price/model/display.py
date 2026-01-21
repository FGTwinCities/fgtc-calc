from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.display import Display


class DisplayPricingModel:
    resolution_func: Polynomial
    size_func: Polynomial
    refreshrate_func: Polynomial
    touchscreen_value: float

    def compute(self, display: Display) -> float:
        megapixels = (display.resolution.x * display.resolution.y) / 1000
        resolution_price = self.resolution_func(megapixels)
        refreshrate_price = self.refreshrate_func(display.refresh_rate)
        size_price = self.size_func(display.size)
        touch_price = self.touchscreen_value if display.touchscreen else 0
        return resolution_price + refreshrate_price + size_price + touch_price
