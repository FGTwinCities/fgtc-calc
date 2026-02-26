from litestar.exceptions import ValidationException


class InsufficientResultsException(ValidationException):
    def __init__(self):
        super().__init__("Not enough results were found on eBay to estimate a price")