from collections.abc import Iterable, Sequence

from .._typecast import (
    DeepCast,
    deepcast,
    traverse,
)


def sequence_from_Iterable(deepcast: DeepCast, cls: type[Sequence], val: Iterable, T):
    if T is not None:
        patch = {}
        for i, v in enumerate(val):
            with traverse(i):
                cv = deepcast(T, v)
                if cv is not v:
                    patch[i] = cv
        if patch:
            val = cls(patch.get(i, v) for i, v in enumerate(val))  # type: ignore

    if not isinstance(val, cls):
        val = cls(val)  # type: ignore
    return val


@deepcast.register
def list_from_Iterable(
    deepcast: DeepCast, cls: type[list], val: Iterable, T=None
) -> list:
    return sequence_from_Iterable(deepcast, cls, val, T)


deepcast.forbid(list, str, bytes, bytearray)
