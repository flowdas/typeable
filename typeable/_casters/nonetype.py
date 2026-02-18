from types import NoneType

from .._typecast import Typecast, typecast


@typecast.register
def NoneType_from_object(typecast: Typecast, cls: type[NoneType], val: object) -> None:
    if val is not None:
        raise TypeError(f"{val!r} is not None")
    return None
