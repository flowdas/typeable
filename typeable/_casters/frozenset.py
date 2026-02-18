from collections.abc import Iterable

from .._typecast import Typecast, typecast
from .list import sequence_from_Iterable


@typecast.register
def frozenset_from_Iterable(
    typecast: Typecast, cls: type[frozenset], val: Iterable, T=None
) -> frozenset:
    return sequence_from_Iterable(typecast, cls, val, T)  # type: ignore


typecast.forbid(frozenset, str, bytes, bytearray)
