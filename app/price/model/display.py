from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.display import Display


class DisplayPricingModel:
    resolution_func: Polynomial = Polynomial([-2.0736, 0.001, 0])
    size_func: Polynomial = Polynomial([0, 1, 0])
    refreshrate_func: Polynomial = Polynomial([-19.8, 0.33, 0])
    touchscreen_value: float = 15

    def compute(self, display: Display) -> float:
        megapixels = (display.resolution.x * display.resolution.y) / 1000
        resolution_price = self.resolution_func(megapixels)
        refreshrate_price = self.refreshrate_func(display.refresh_rate)
        size_price = self.size_func(display.size)
        touch_price = self.touchscreen_value if display.touchscreen else 0
        return resolution_price + refreshrate_price + size_price + touch_price
