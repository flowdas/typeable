from .._typecast import DeepCast, deepcast, getcontext


@deepcast.register
def bool_from_int(deepcast: DeepCast, cls: type[bool], val: int) -> bool:
    if not getcontext().bool_from_01:
        raise TypeError("bool_from_01 is False")
    if val != 0 and val != 1:
        raise ValueError(f"invalid int value for bool: {val}")
    return cls(val)


@deepcast.register
def bool_from_str(deepcast: DeepCast, cls: type[bool], val: str) -> bool:
    mapping = getcontext().bool_strings or {}
    try:
        return cls(mapping[val.lower()])
    except KeyError:
        raise TypeError(f"invalid literal for bool: '{val}'")
