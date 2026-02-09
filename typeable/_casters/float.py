import math
from numbers import Number

from .._deepcast import DeepCast, deepcast, getcontext


@deepcast.register
def float_from_str(deepcast: DeepCast, cls: type[float], val: str) -> float:
    if not getcontext().parse_number:
        raise TypeError("parse_number is False")
    try:
        r = float(val)
    except Exception:
        raise TypeError(f"invalid literal for float: '{val}'")
    return r


@deepcast.register
def float_from_Number(deepcast: DeepCast, cls: type[float], val: Number) -> float:
    r = float(val)  # type: ignore
    if not math.isnan(r) and r != val:
        raise TypeError(f"invalid number for float: '{val}'")
    return r


@deepcast.register
def float_from_complex(deepcast: DeepCast, cls: type[float], val: complex) -> float:
    if val.imag != 0:
        raise TypeError(f"invalid number for float: '{val}'")
    return val.real


deepcast.forbid(float, bool)
