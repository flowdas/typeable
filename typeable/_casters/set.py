from collections.abc import Iterable

from .._typecast import Typecast, typecast
from .list import sequence_from_Iterable


@typecast.register
def set_from_Iterable(deepcast: Typecast, cls: type[set], val: Iterable, T=None) -> set:
    return sequence_from_Iterable(deepcast, cls, val, T)  # type: ignore


typecast.forbid(set, str, bytes, bytearray)
