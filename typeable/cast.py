# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import datetime
import weakref
from abc import get_cache_token
from functools import _find_impl
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
                raise NotImplementedError(
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
def _(cls: Type[object], val, ctx):
    return cls(val)

#
# None
#


@cast.register
def _(cls: Type[None], val, ctx):
    if val is None:
        return None
    raise TypeError(f"{val!r} is not None")

#
# datetime.datetime
#


@cast.register
def _(cls: Type[datetime.datetime], val, ctx):
    if isinstance(val, str):
        return datetime.datetime.fromisoformat(val)
    else:
        return cls(val)

#
# list
#


@cast.register
def _(cls: Type[list], val, ctx, T=None):
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
def _(cls: Type[dict], val, ctx, K=None, V=None):
    if K is None:
        return cls(val)
    else:
        r = cls()
        for k, v in val.items():
            with ctx.traverse(k):
                r[cast(K, k, ctx=ctx)] = cast(V, v, ctx=ctx)
        return r

#
# Union
#


@cast.register
def _(cls, val, ctx, *Ts) -> Union:
    vcls = val.__class__
    for T in Ts:
        try:
            return cast(T, val)
        except:
            continue
    else:
        raise TypeError("no match")
