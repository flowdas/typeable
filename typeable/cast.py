# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
from functools import _find_impl

__all__ = [
    'cast',
]

_T = TypeVar('_T')

_registry = {}


def _register(func):
    sig = signature(func)
    if len(sig.parameters) < 2:
        raise TypeError(
            f"{func!r}() takes {len(sig.parameters)} arguments but 2 required")
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


def cast(cls: Type[_T], val) -> _T:
    origin = get_origin(cls) or cls
    func = _dispatch(origin)
    args = get_args(cls) or ()
    return func(origin, val, *args)


cast.register = _register
cast.dispatch = _dispatch
