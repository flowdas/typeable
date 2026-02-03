from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import fields, is_dataclass

from .._deepcast import Context, DeepCast, deepcast, getcontext, traverse


@deepcast.register
def dict_from_Mapping(
    deepcast: DeepCast,
    cls: type[dict],
    val: Mapping,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    if K is not None:
        ctx: Context | None = None
        kpatch = {}
        vpatch = {}
        for k in val:
            with traverse(k):
                ck = deepcast(K, k)
                if ck is not k:
                    if ck != k and ck in val:
                        if ctx is None:
                            ctx = getcontext()
                        if not ctx.lossy_conversion:
                            raise TypeError("lossy_conversion is False: key collision")
                    kpatch[k] = ck
                v = val[k]
                if V is not None:  # Counter 에서 V 만 None 일 수 있다.
                    cv = deepcast(V, v)
                    if cv is not v:
                        vpatch[k] = cv
        if kpatch or vpatch:
            val = {kpatch.get(k, k): vpatch.get(k, val[k]) for k in val}
    if not isinstance(val, cls):
        if cls is defaultdict:
            val = defaultdict(None, val)
        else:
            val = cls(val)
    return val


@deepcast.register
def dict_from_Iterable(
    deepcast: DeepCast,
    cls: type[dict],
    val: Iterable,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    kpatch = {}
    vpatch = {}
    if K is not None:
        for k, v in val:
            with traverse(k):
                ck = deepcast(K, k)
                if ck is not k:
                    kpatch[k] = ck
                if V is not None:  # Counter 에서 V 만 None 일 수 있다.
                    cv = deepcast(V, v)
                    if cv is not v:
                        vpatch[k] = cv
    val = {kpatch.get(k, k): vpatch.get(k, v) for k, v in val}
    if not val and not getcontext().dict_from_empty_iterable:
        raise TypeError("dict_from_empty_iterable is False")

    if not isinstance(val, cls):
        if cls is defaultdict:
            val = defaultdict(None, val)
        else:
            val = cls(val)
    return val


@deepcast.register
def dict_from_NamedTuple(
    deepcast: DeepCast,
    cls: type[dict],
    val: tuple,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    try:
        d = val._asdict()
    except Exception:
        return dict_from_Iterable(deepcast, cls, val, K, V)
    return dict_from_Mapping(deepcast, cls, d, K, V)


@deepcast.register
def dict_from_object(
    deepcast: DeepCast,
    cls: type[dict],
    val: object,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    d: dict | None = None
    if is_dataclass(val):
        d = {field.name: getattr(val, field.name) for field in fields(val)}
    else:
        try:
            d = val.__deepcast__()  # type: ignore
        except AttributeError:
            pass
    if d is None:
        raise TypeError(f"dict from {type(val)!r} not supported")
    return dict_from_Mapping(deepcast, cls, d, K, V)


deepcast.forbid(dict, str, bytes, bytearray)
