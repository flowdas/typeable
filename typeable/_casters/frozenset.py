from collections.abc import Iterable

from .._typecast import DeepCast, typecast
from .list import sequence_from_Iterable


@typecast.register
def frozenset_from_Iterable(
    deepcast: DeepCast, cls: type[frozenset], val: Iterable, T=None
) -> frozenset:
    return sequence_from_Iterable(deepcast, cls, val, T)  # type: ignore


typecast.forbid(frozenset, str, bytes, bytearray)
