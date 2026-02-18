import sys
from contextlib import ExitStack
from types import UnionType
from typing import Union

from .._error import capture, traverse
from .._typecast import DeepCast, typecast


@typecast.register
def UnionType_from_object(deepcast: DeepCast, cls: type[UnionType], val: object, *Ts):
    uc = deepcast.get_unioncast(Ts)
    deepest = ()
    for T in uc.dispatch(val.__class__):
        try:
            with capture() as error:
                return deepcast(T, val)
        except Exception:
            if error.location and len(error.location) > len(deepest):
                deepest = error.location
            continue
    else:
        with ExitStack() as stack:
            for loc in deepest:
                stack.enter_context(traverse(loc))
            raise TypeError("no match")


if sys.version_info < (3, 14):

    @typecast.register
    def Union_from_object(deepcast: DeepCast, cls: type[Union], val: object, *Ts):
        return UnionType_from_object(deepcast, cls, val, *Ts)
