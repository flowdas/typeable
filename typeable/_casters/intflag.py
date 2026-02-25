from enum import IntFlag
from .._typecast import Typecast, typecast


@typecast.register
def IntFlag_from_int(typecast: Typecast, cls: type[IntFlag], val: int) -> IntFlag:
    try:
        return cls(val)
    except ValueError as e:
        raise TypeError from e
