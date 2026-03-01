from enum import Enum
from .._typecast import Typecast, typecast


@typecast.register
def Enum_from_object(typecast: Typecast, cls: type[Enum], val: object) -> Enum:
    try:
        return cls(val)
    except ValueError as e:
        raise TypeError from e
