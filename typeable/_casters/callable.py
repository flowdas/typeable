from collections.abc import Callable
from inspect import signature

from .._typecast import Typecast, typecast

from .type import import_fqn


@typecast.register
def Callable_from_str(
    typecast: Typecast,
    cls: type[Callable],  # type: ignore
    val: str,
    PT=None,
    RT=None,
):
    f = import_fqn(val)
    if not callable(f):
        raise TypeError
    if isinstance(PT, list):
        # check only structural compatibility of arguments
        sig = signature(f)
        args = [None] * len(PT)
        sig.bind(*args)  # may raise TypeError
    return f
