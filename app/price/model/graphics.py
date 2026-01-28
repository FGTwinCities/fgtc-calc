from litestar.exceptions import ValidationException

from app.db.model import GraphicsProcessor


def graphics_model_func(x: float, a: float, b: float) -> float:
    return (a * x) + b

class GraphicsProcessorPricingModel:
    passmark_parameters = (1, 0)

    def compute(self, gpu: GraphicsProcessor) -> float:
        if not gpu.score:
            raise ValidationException("GPU does not have a passmark score, cannot evaluate price.")

        return graphics_model_func(gpu.score, *self.passmark_parameters)