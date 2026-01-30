from litestar.exceptions import ValidationException

from app.db.model import Processor
from app.lib.util import getenv_bool


def processor_model_func(x: float, a: float, b: float) -> float:
    return (a * x) + b


class ProcessorPricingModel:
    passmark_parameters = (1, 0)

    def compute(self, processor: Processor) -> float:
        score: int
        if getenv_bool("USE_PASSMARK_PRICINGMODEL", True):
            score = processor.passmark_multithread_score
        else:
            score = processor.geekbench_multithread_score

        if not score:
            raise ValidationException("Processor does not have a passmark score, cannot evaluate price.")

        return processor_model_func(score, *self.passmark_parameters)
