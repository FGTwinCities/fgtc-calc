from litestar.exceptions import ValidationException

from app.db.model import GraphicsProcessor
from app.lib.util import getenv_bool


def graphics_model_func(x: float, a: float, b: float) -> float:
    return (a * x) + b

class GraphicsProcessorPricingModel:
    passmark_parameters = (1, 0)

    def compute(self, gpu: GraphicsProcessor) -> float:
        score: int
        if getenv_bool("USE_PASSMARK_PRICINGMODEL", True):
            score = gpu.passmark_score
        else:
            score = gpu.geekbench_score

        if not score:
            raise ValidationException("GPU does not have a passmark score, cannot evaluate price.")

        return graphics_model_func(score, *self.passmark_parameters)