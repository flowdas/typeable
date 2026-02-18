import cmath
from collections.abc import Iterable
from numbers import Number

from .._typecast import Typecast, getcontext, typecast


@typecast.register
def complex_from_str(typecast: Typecast, cls: type[complex], val: str) -> complex:
    if not getcontext().parse_number:
        raise TypeError("parse_number is False")
    try:
        r = complex(val)
    except Exception:
        raise TypeError(f"invalid literal for complex: '{val}'")
    return r


@typecast.register
def complex_from_Iterable(
    typecast: Typecast, cls: type[complex], val: Iterable
) -> complex:
    cv = typecast(tuple[float, float], val)
    return cls(*cv)


@typecast.register
def complex_from_Number(typecast: Typecast, cls: type[complex], val: Number) -> complex:
    r = complex(val)  # type: ignore
    if not cmath.isnan(r) and r != val:
        raise TypeError(f"invalid number for complex: '{val}'")
    return r


typecast.forbid(complex, bool)
