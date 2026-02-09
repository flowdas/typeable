from typing import Annotated

from .._deepcast import DeepCast, deepcast


@deepcast.register
def Annotated_from_object(
    deepcast: DeepCast, cls: type[Annotated], val: object, T: type, *args
):
    return deepcast(T, val)
