from enum import IntEnum
from .._typecast import Typecast, typecast


@typecast.register
def IntEnum_from_int(typecast: Typecast, cls: type[IntEnum], val: int) -> IntEnum:
    try:
        return cls(val)
    except ValueError as e:
        raise TypeError from e
