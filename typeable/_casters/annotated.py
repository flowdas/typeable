from typing import Annotated

from .._typecast import DeepCast, typecast


@typecast.register
def Annotated_from_object(
    deepcast: DeepCast, cls: type[Annotated], val: object, T: type, *args
):
    return deepcast(T, val)
