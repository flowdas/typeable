from collections.abc import Iterable, Sequence

from .._typecast import (
    Typecast,
    traverse,
    typecast,
)


def sequence_from_Iterable(typecast: Typecast, cls: type[Sequence], val: Iterable, T):
    if T is not None:
        patch = {}
        for i, v in enumerate(val):
            with traverse(i):
                cv = typecast(T, v)
                if cv is not v:
                    patch[i] = cv
        if patch:
            val = cls(patch.get(i, v) for i, v in enumerate(val))  # type: ignore

    if not isinstance(val, cls):
        val = cls(val)  # type: ignore
    return val


@typecast.register
def list_from_Iterable(
    typecast: Typecast, cls: type[list], val: Iterable, T=None
) -> list:
    return sequence_from_Iterable(typecast, cls, val, T)


typecast.forbid(list, str, bytes, bytearray)
