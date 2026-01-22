from litestar.exceptions import ValidationException

from app.db.model import Processor


def processor_model_func(x: float, a: float, b: float, c: float) -> float:
    return (a * x ** 2) + (b * x) + c


class ProcessorPricingModel:
    passmark_parameters = (0, 1, 0)

    def compute(self, processor: Processor) -> float:
        if not processor.multithread_score:
            raise ValidationException("Processor does not have a passmark score, cannot evaluate price.")

        return processor_model_func(processor.multithread_score, *self.passmark_parameters)
