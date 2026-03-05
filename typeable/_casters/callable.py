from collections.abc import Callable

from .._constraint import _Callable_from_object, _Callable_from_str
from .._typecast import Typecast, typecast


@typecast.register
def Callable_from_str(
    typecast: Typecast,
    cls: type[Callable],  # type: ignore
    val: str,
    PT=None,
    RT=None,
):
    return _Callable_from_str(val, PT, RT)


@typecast.register
def Callable_from_object(
    typecast: Typecast,
    cls: type[Callable],  # type: ignore
    val: object,
    PT=None,
    RT=None,
):
    return _Callable_from_object(val, PT, RT)
