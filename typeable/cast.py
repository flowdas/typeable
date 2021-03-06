# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import datetime
from functools import _find_impl
from inspect import (
    signature,
)
from .typing import (
    Type,
    TypeVar,
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


def _register(func):
    sig = signature(func)
    if len(sig.parameters) < 3:
        raise TypeError(
            f"{func!r}() takes {len(sig.parameters)} arguments but 3 required")
    argname, parameter = next(iter(sig.parameters.items()))
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
    if cls in _registry:
        raise RuntimeError(f"Ambiguous `cast.register()`")

    _registry[cls] = func
    return func


def _dispatch(cls):
    try:
        return _registry[cls]
    except KeyError:
        func = _find_impl(cls, _registry)
        if not func:
            raise NotImplementedError(
                f"No implementation found for '{cls.__qualname__}'")
        return func


def cast(cls: Type[_T], val, *, ctx: Context = None) -> _T:
    origin = get_origin(cls) or cls
    func = _dispatch(origin)
    if ctx is None:
        ctx = Context()
    return func(origin, val, ctx, *get_args(cls))


cast.register = _register
cast.dispatch = _dispatch


@cast.register
def _(cls: Type[int], val, ctx):
    return cls(val)


@cast.register
def _(cls: Type[bool], val, ctx):
    return cls(val)


@cast.register
def _(cls: Type[float], val, ctx):
    return cls(val)


@cast.register
def _(cls: Type[str], val, ctx):
    return cls(val)


@cast.register
def _(cls: Type[datetime.datetime], val, ctx):
    if isinstance(val, str):
        return datetime.datetime.fromisoformat(val)
    else:
        return cls(val)


@cast.register
def _(cls: Type[list], val, ctx, T=None):
    if T is None:
        return cls(val)
    else:
        r = cls()
        for i, v in enumerate(val):
            if v is None:
                r.append(v)
            else:
                with ctx.traverse(i):
                    r.append(cast(T, v, ctx=ctx))
        return r


@cast.register
def _(cls: Type[dict], val, ctx, K=None, V=None):
    if K is None:
        return cls(val)
    else:
        r = cls()
        for k, v in val.items():
            with ctx.traverse(k):
                if k is not None:
                    k = cast(K, k, ctx=ctx)
                if v is not None:
                    v = cast(V, v, ctx=ctx)
                r[k] = v
        return r
