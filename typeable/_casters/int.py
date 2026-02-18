from decimal import Decimal
from numbers import Number

from .._typecast import Typecast, getcontext, typecast


@typecast.register
def int_from_str(typecast: Typecast, cls: type[int], val: str) -> int:
    if not getcontext().parse_number:
        raise TypeError("parse_number is False")
    try:
        v = Decimal(val)
    except Exception:
        raise TypeError(f"invalid literal for int: '{val}'")
    r = int(v)
    if r != v:
        raise TypeError(f"invalid literal for int: '{val}'")
    return r


@typecast.register
def int_from_Number(typecast: Typecast, cls: type[int], val: Number) -> int:
    r = int(val)  # type: ignore
    if r != val:
        raise TypeError(f"invalid number for int: '{val}'")
    return r


@typecast.register
def int_from_complex(typecast: Typecast, cls: type[int], val: complex) -> int:
    r = int(val.real)
    if r != val:
        raise TypeError(f"invalid number for int: '{val}'")
    return r


typecast.forbid(int, bool)
