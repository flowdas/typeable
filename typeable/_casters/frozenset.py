from collections.abc import Iterable

from .._deepcast import DeepCast, deepcast
from .list import sequence_from_Iterable


@deepcast.register
def frozenset_from_Iterable(
    deepcast: DeepCast, cls: type[frozenset], val: Iterable, T=None
) -> frozenset:
    return sequence_from_Iterable(deepcast, cls, val, T)  # type: ignore


deepcast.forbid(frozenset, str, bytes, bytearray)
