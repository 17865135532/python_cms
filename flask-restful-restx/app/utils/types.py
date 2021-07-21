from functools import lru_cache


def ensure_int(o):
    if isinstance(o, int):
        return o
    elif isinstance(o, float):
        return int(o)
    elif isinstance(o, str):
        if o.isdigit():
            return int(o)
        return int(float(o))
    raise TypeError(type(o))


@lru_cache(maxsize=None)
def enum_val2item(enum_item, val):
    for item in enum_item.__members__.values():
        if item.value == val:
            return item


@lru_cache(maxsize=None)
def enum_item2val(enum_item, name):
    for item, val in enum_item.__members__.items():
        if item == name:
            return val.value
