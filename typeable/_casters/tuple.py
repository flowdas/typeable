from collections.abc import Iterable, Mapping
from typing import Any

from .._deepcast import (
    DeepCast,
    deepcast,
    traverse,
)
from .list import sequence_from_Iterable


@deepcast.register
def tuple_from_Iterable(
    deepcast: DeepCast, cls: type[tuple], val: Iterable, *Ts
) -> tuple:
    if not Ts:
        if hasattr(cls, "_fields"):
            # namedtuple
            return deepcast.apply(cls, {cls._fields[i]: v for i, v in enumerate(val)})  # type: ignore
        else:
            return sequence_from_Iterable(deepcast, cls, val, None)
    elif len(Ts) == 2 and Ts[1] == ...:
        return sequence_from_Iterable(
            deepcast, cls, val, None if Ts[0] is Any else Ts[0]
        )
    if Ts == ((),):
        # empty tuple
        Ts = ()
    n = len(Ts)
    patch = {}
    i = -1
    for i, v in enumerate(val):
        if i >= n:
            raise TypeError("length mismatch")
        with traverse(i):
            cv = deepcast(Ts[i], v)
            if cv is not v:
                patch[i] = cv
    if i < n - 1:
        raise TypeError("length mismatch")
    if patch:
        val = cls(patch.get(i, v) for i, v in enumerate(val))

    if not isinstance(val, cls):
        val = cls(val)
    return val


@deepcast.register
def namedtuple_from_Mapping(
    deepcast: DeepCast, cls: type[tuple], val: Mapping, *Ts
) -> tuple:
    # Mapping 을 구체적으로 선언하지 않고 object 에 맡기면, Iterable 로 떨어진다.
    return namedtuple_from_object(deepcast, cls, val, *Ts)


@deepcast.register
def namedtuple_from_object(
    deepcast: DeepCast, cls: type[tuple], val: object, *Ts
) -> tuple:
    if Ts or not hasattr(cls, "_fields"):
        raise TypeError(f"dict from {type(val)!r} not supported")
    return deepcast.apply(cls, val)


deepcast.forbid(tuple, str, bytes, bytearray)
