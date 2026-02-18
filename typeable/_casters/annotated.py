from typing import Annotated

from .._typecast import Typecast, typecast


@typecast.register
def Annotated_from_object(
    deepcast: Typecast, cls: type[Annotated], val: object, T: type, *args
):
    return deepcast(T, val)
