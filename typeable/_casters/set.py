from collections.abc import Iterable

from .._deepcast import DeepCast, deepcast
from .list import sequence_from_Iterable


@deepcast.register
def set_from_Iterable(deepcast: DeepCast, cls: type[set], val: Iterable, T=None) -> set:
    return sequence_from_Iterable(deepcast, cls, val, T)  # type: ignore


deepcast.forbid(set, str, bytes, bytearray)
