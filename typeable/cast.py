# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import cmath
import datetime
import math
import weakref
from abc import get_cache_token
from collections.abc import (
    Mapping,
)
from functools import _find_impl
from numbers import Real, Number
from inspect import (
    signature,
)
from .typing import (
    Any,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from .context import Context

__all__ = [
    'cast',
]

_T = TypeVar('_T')

_registry = {}
_dispatch_cache = {}
_cache_token = None


def _register(func):
    global _cache_token
    sig = signature(func)
    if len(sig.parameters) < 3:
        raise TypeError(
            f"{func!r}() takes {len(sig.parameters)} arguments but 3 required")
    it = iter(sig.parameters.items())
    argname, parameter = next(it)
    hints = get_type_hints(func)
    typ = hints.get(argname)
    if typ:
        type_args = get_args(typ)
        if get_origin(typ) is not type or not type_args:
            raise TypeError(
                f"Invalid first argument to `cast.register()`: {typ!r}. "
                f"Use either typing.Type[] annotation or return type annotation."
            )
        cls = type_args[0]
    else:
        cls = hints.get('return')
        if cls is None:
            raise TypeError(
                f"Invalid signature to `cast.register()`. "
                f"Use either typing.Type[] annotation or return type annotation."
            )

    argname, parameter = next(it)
    vcls = hints.get(argname)
    if not vcls:
        vcls = Any
    if vcls == Any:
        vcls = object

    if cls in _registry:
        if vcls in _registry[cls]:
            raise RuntimeError(f"Ambiguous `cast.register()`")
        _registry[cls][vcls] = func
    else:
        _registry[cls] = {vcls: func}

    if _cache_token is None:
        if hasattr(cls, '__abstractmethods__') or hasattr(vcls, '__abstractmethods__'):
            _cache_token = get_cache_token()
    _dispatch_cache.clear()

    return func


def _dispatch(cls, vcls):
    global _cache_token
    if _cache_token is not None:
        current_token = get_cache_token()
        if _cache_token != current_token:
            _dispatch_cache.clear()
            _cache_token = current_token

    try:
        func = _dispatch_cache[(cls, vcls)]
    except KeyError:
        try:
            vreg = _registry[cls]
        except KeyError:
            vreg = _find_impl(cls, _registry)
            if not vreg:
                raise NotImplementedError(
                    f"No implementation found for '{cls.__qualname__}'")

        try:
            return vreg[vcls]
        except KeyError:
            func = _find_impl(vcls, vreg)
            if not func:
                raise TypeError(
                    f"No implementation found for '{cls.__qualname__}' from {vcls.__qualname__}")
        _dispatch_cache[(cls, vcls)] = func

    return func


def cast(cls: Type[_T], val, *, ctx: Context = None) -> _T:
    origin = get_origin(cls) or cls
    func = _dispatch(origin, val.__class__)
    if ctx is None:
        ctx = Context()
    return func(origin, val, ctx, *get_args(cls))


cast.register = _register
cast.dispatch = _dispatch

#
# object (fallback)
#


@cast.register
def _cast_object_object(cls: Type[object], val, ctx, *Ts):
    if cls is object:
        if isinstance(val, object):
            return object()
        raise TypeError
    return cls(val)

#
# None
#


@cast.register
def _cast_None_object(cls: Type[None], val, ctx):
    if val is None:
        return None
    raise TypeError(f"{val!r} is not None")

#
# bool
#


@cast.register
def _cast_bool_int(cls: Type[bool], val: int, ctx):
    if isinstance(val, bool):
        return cls(val)
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    if not ctx.lossy_conversion and not (val == 0 or val == 1):
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return cls(val)


@cast.register
def _cast_bool_str(cls: Type[bool], val: str, ctx):
    if not ctx.bool_strings:
        raise TypeError
    try:
        return cls(ctx.bool_strings[val.lower()])
    except KeyError:
        raise ValueError

#
# int
#


@cast.register
def _cast_int_object(cls: Type[int], val, ctx):
    if ctx.lossy_conversion or isinstance(val, int) or not isinstance(val, Real):
        return cls(val)
    r = cls(val)
    if r != val:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


@cast.register
def _cast_int_bool(cls: Type[int], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)

#
# float
#


@cast.register
def _cast_float_object(cls: Type[float], val, ctx):
    if ctx.accept_nan:
        return cls(val)
    r = cls(val)
    if not math.isfinite(r):
        raise ValueError(f'ctx.accept_nan={ctx.accept_nan}')
    return r


@cast.register
def _cast_float_bool(cls: Type[float], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)

#
# complex
#


@cast.register
def _cast_complex_object(cls: Type[complex], val, ctx):
    if ctx.accept_nan:
        return cls(val)
    r = cls(val)
    if not cmath.isfinite(r):
        raise ValueError(f'ctx.accept_nan={ctx.accept_nan}')
    return r


@cast.register
def _cast_complex_bool(cls: Type[complex], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)

#
# str
#


@cast.register
def _cast_str_object(cls: Type[str], val, ctx):
    if ctx.strict_str:
        if not isinstance(val, (str, Number)):
            raise TypeError(f'ctx.strict_str={ctx.strict_str}')
    else:
        if val is None:
            raise TypeError(f"{cls.__qualname__} is required, but {val!r} is given")
    return cls(val)


@cast.register
def _cast_str_bytes(cls: Type[str], val: bytes, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


@cast.register
def _cast_str_bytearray(cls: Type[str], val: bytearray, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)

#
# bytes
#


@cast.register
def _cast_bytes_object(cls: Type[bytes], val, ctx):
    if isinstance(val, int):
        raise TypeError
    return cls(val)


@cast.register
def _cast_bytes_str(cls: Type[bytes], val: str, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# bytearray
#


@cast.register
def _cast_bytearray_object(cls: Type[bytearray], val, ctx):
    if isinstance(val, int):
        raise TypeError
    return cls(val)


@cast.register
def _cast_bytearray_str(cls: Type[bytearray], val: str, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# list
#


@cast.register
def _cast_list_object(cls: Type[list], val, ctx, T=None):
    if isinstance(val, Mapping):
        val = val.items()
    if T is None:
        return cls(val)
    else:
        r = cls()
        for i, v in enumerate(val):
            with ctx.traverse(i):
                r.append(cast(T, v, ctx=ctx))
        return r

#
# dict
#


@cast.register
def _cast_dict_object(cls: Type[dict], val, ctx, K=None, V=None):
    if K is None:
        return cls(val)
    else:
        if isinstance(val, Mapping):
            val = val.items()
        r = cls()
        for k, v in val:
            with ctx.traverse(k):
                r[cast(K, k, ctx=ctx)] = cast(V, v, ctx=ctx)
        return r

#
# set
#


@cast.register
def _cast_set_object(cls: Type[set], val, ctx, T=None):
    if T is None:
        return cls(val)
    else:
        r = cls()
        for v in val:
            with ctx.traverse(v):
                r.add(cast(T, v, ctx=ctx))
        return r

#
# frozenset
#


@cast.register
def _cast_set_object(cls: Type[frozenset], val, ctx, T=None):
    if T is None:
        return cls(val)
    else:
        r = set()
        for v in val:
            with ctx.traverse(v):
                r.add(cast(T, v, ctx=ctx))
        return cls(r)

#
# tuple
#


@cast.register
def _cast_tuple_object(cls: Type[tuple], val, ctx, *Ts):
    if isinstance(val, Mapping):
        val = val.items()
    if not Ts:
        return cls(val)
    elif Ts[-1] == ...:
        r = []
        for i, v in enumerate(val):
            with ctx.traverse(i):
                r.append(cast(Ts[0], v, ctx=ctx))
        return cls(r)
    else:
        if Ts[0] == ():
            Ts = ()
        r = []
        it = iter(val)
        for i, T in enumerate(Ts):
            with ctx.traverse(i):
                try:
                    v = next(it)
                except StopIteration:
                    raise TypeError('length mismatch')
                r.append(cast(T, v, ctx=ctx))
        try:
            with ctx.traverse(len(Ts)):
                next(it)
                raise TypeError('length mismatch')
        except StopIteration:
            return cls(r)


#
# Union
#


@cast.register
def _cast_Union_object(cls, val, ctx, *Ts) -> Union:
    vcls = val.__class__
    for T in Ts:
        try:
            return cast(T, val)
        except:
            continue
    else:
        raise TypeError("no match")

#
# datetime.datetime
#


@cast.register
def _cast_datetime_object(cls: Type[datetime.datetime], val, ctx):
    if isinstance(val, str):
        return datetime.datetime.fromisoformat(val)
    else:
        return cls(val)
