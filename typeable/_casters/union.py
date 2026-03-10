import sys
from types import UnionType
from typing import Union

from .._error import capture, traverse
from .._typecast import Typecast, typecast


@typecast.register
def UnionType_from_object(typecast: Typecast, cls: type[UnionType], val: object, *Ts):
    uc = typecast.get_unioncast(Ts)
    history = []
    for T in uc.dispatch(val.__class__):
        try:
            with capture() as error:
                return typecast(T, val)
        except Exception as e:
            history.append((T, error.location, e))
            continue
    else:
        with traverse(history):
            raise TypeError("no match")


if sys.version_info < (3, 14):

    @typecast.register
    def Union_from_object(typecast: Typecast, cls: type[Union], val: object, *Ts):
        return UnionType_from_object(typecast, cls, val, *Ts)
