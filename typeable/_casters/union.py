import sys
from types import UnionType
from typing import Union

from .._deepcast import DeepCast, deepcast


@deepcast.register
def UnionType_from_object(deepcast: DeepCast, cls: type[UnionType], val: object, *Ts):
    uc = deepcast.get_unioncast(Ts)
    for T in uc.dispatch(val.__class__):
        try:
            return deepcast(T, val)
        except Exception:
            continue
    else:
        raise TypeError("no match")


if sys.version_info < (3, 14):

    @deepcast.register
    def Union_from_object(deepcast: DeepCast, cls: type[Union], val: object, *Ts):
        return UnionType_from_object(deepcast, cls, val, *Ts)
