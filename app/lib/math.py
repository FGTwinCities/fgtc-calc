""" Mathematics library functions """
import math
from decimal import Decimal


def clamp(x: int, min: int, max: int) -> int:
    if x > max:
        return max
    elif x < min:
        return min
    else:
        return x


def mb2gb(mb: float) -> float:
    return mb / 1000


def gb2mb(gb: float) -> float:
    return gb * 1000

def tb2mb(tb: float) -> float:
    return gb2mb(tb * 1000)

def round_down_exact(num: float, to: float) -> float:
    num, to = Decimal(str(num)), Decimal(str(to))
    return float(math.floor(num / to) * to)