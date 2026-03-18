import re

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split

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


def cull_outliers_1d(data):
    data = data.reshape(-1, 1)
    data_train, data_test = train_test_split(data)
    clf = IsolationForest(max_samples=min(100, len(data_train)))
    clf.fit(data_train)
    return data[clf.predict(data) == 1]

def cull_outliers_2d(data, filter_data):
    X_train, X_test = train_test_split(data)

    clf = IsolationForest()
    clf.fit(X_train)

    return filter_data[clf.predict(data) == 1]
