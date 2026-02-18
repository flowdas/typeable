from collections import defaultdict
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import is_typeddict

from .._context import getcontext
from .._typecast import _META_ALIAS, _META_HIDE, Typecast, traverse, typecast


@typecast.register
def dict_from_Mapping(
    typecast: Typecast,
    cls: type[dict],
    val: Mapping,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    if K is not None:
        kpatch = {}
        vpatch = {}
        for k in val:
            with traverse(k):
                ck = typecast(K, k)
                if ck is not k:
                    kpatch[k] = ck
                v = val[k]
                if V is not None:  # Counter 에서 V 만 None 일 수 있다.
                    cv = typecast(V, v)
                    if cv is not v:
                        vpatch[k] = cv
        if kpatch or vpatch:
            val = {kpatch.get(k, k): vpatch.get(k, val[k]) for k in val}
    elif is_typeddict(cls):
        annotations: dict[str, type] = cls.__annotations__
        required = set(cls.__required_keys__)  # type: ignore
        kpatch = {}
        vpatch = {}
        for k in val:
            with traverse(k):
                ck = typecast(str, k)
                if ck is not k:
                    kpatch[k] = ck
                v = val[k]
                if ck not in annotations:
                    raise TypeError(f"got an unexpected key '{k}'")
                cv = typecast(annotations[ck], v)
                if cv is not v:
                    vpatch[k] = cv
            required.discard(k)
        if required:
            k = list(required)[0]
            with traverse(k):
                raise TypeError(f"missing required key: '{k}'")
        if kpatch or vpatch:
            val = {kpatch.get(k, k): vpatch.get(k, val[k]) for k in val}
        # TypedDict 는 isinstance 에 사용될 수 없고,
        # 이제 타입 정보를 다 활용했으니 dict 로 취급해도 좋다.
        cls = dict
    if not isinstance(val, cls):
        if cls is defaultdict:
            val = defaultdict(None, val)
        else:
            val = cls(val)
    return val


@typecast.register
def dict_from_NamedTuple(
    typecast: Typecast,
    cls: type[dict],
    val: tuple,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    try:
        d = val._asdict()
    except Exception:
        raise TypeError(f"dict from {type(val)!r} not supported")
    return dict_from_Mapping(typecast, cls, d, K, V)


@typecast.register
def dict_from_object(
    typecast: Typecast,
    cls: type[dict],
    val: object,
    K: type | None = None,
    V: type | None = None,
) -> dict:
    d: dict | None = None
    if is_dataclass(val):
        # 여기에서는 shallow copy 만 수행한다.
        # 나머지는 dict_from_Mapping 에 위임한다.
        d = {}
        hide_default_none = None
        for f in fields(val):
            m = f.metadata or {}
            if not m.get(_META_HIDE):
                value = getattr(val, f.name)
                include = True
                if value is None:
                    if hide_default_none is None:
                        hide_default_none = getcontext().hide_default_none
                    include = not hide_default_none or f.default is not None
                if include:
                    d[m.get(_META_ALIAS, f.name)] = value
    else:
        try:
            d = val.__typecast__()  # type: ignore
        except AttributeError:
            pass
    if d is None:
        raise TypeError(f"dict from {type(val)!r} not supported")
    return dict_from_Mapping(typecast, cls, d, K, V)


typecast.forbid(dict, str, bytes, bytearray)
