""" Mathematics library functions """


def clamp(x: int, min: int, max: int) -> int:
    if x > max:
        return max
    elif x < min:
        return min
    else:
        return x