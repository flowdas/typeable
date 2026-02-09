from types import NoneType

from .._deepcast import DeepCast, deepcast


@deepcast.register
def NoneType_from_object(deepcast: DeepCast, cls: type[NoneType], val: object) -> None:
    if val is not None:
        raise TypeError(f"{val!r} is not None")
    return None
