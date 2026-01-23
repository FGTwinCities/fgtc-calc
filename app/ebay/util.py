import re

import numpy as np

from app.lib.math import gb2mb, tb2mb
from app.lib.util import try_int


def parse_capacity(capacity_string: str) -> int | None:
    res = re.search(r'(\d+)\s*([MmGgTt][Bb])', capacity_string)

    if not res:
        return None

    value = try_int(res.group(1))
    unit = res.group(2).lower()

    if 'm' in unit:
        pass
    elif 'g' in unit:
        value = gb2mb(value)
    elif 't' in unit:
        value = tb2mb(value)
    else:
        return None

    return round(value)


def cull_outliers(x, outlierConstant):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)

    result = a[np.where((a >= quartileSet[0]) & (a <= quartileSet[1]))]

    return result.tolist()


def item_has_category(item: dict, category_id: int) -> bool:
    if "category_id_path" in item:
        categories = map(lambda c: int(c), item['category_id_path'].split('|'))
        if category_id in categories:
            return True
    elif "categories" in item:
        for category in item['categories']:
            if try_int(category['category_id']) == category_id:
                return True

    return False

