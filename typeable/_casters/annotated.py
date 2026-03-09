from typing import Annotated

from .._constraint import Constraint
from .._typecast import Typecast, typecast


@typecast.register
def Annotated_from_object(
    typecast: Typecast, cls: type[Annotated], val: object, T: type, *args
):
    r = typecast(T, val)
    for arg in args:
        if isinstance(arg, Constraint):
            if not arg(r, val):
                raise ValueError(f"Constraint {arg!r} failed")
    return r
