# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# typing polyfill
#
from typing import *

import sys
import typing

if sys.version_info < (3, 9):  # pragma: no cover
    from typing_extensions import Annotated, _AnnotatedAlias

if sys.version_info < (3, 8):  # pragma: no cover
    import collections.abc


    def get_origin(tp):
        if isinstance(tp, _AnnotatedAlias):
            return Annotated
        if isinstance(tp, typing._GenericAlias):
            return tp.__origin__
        if tp is Generic:
            return tp
        return None


    def get_args(tp):
        if isinstance(tp, _AnnotatedAlias):
            return (tp.__origin__,) + tp.__metadata__
        if isinstance(tp, typing._GenericAlias):
            res = tp.__args__
            if get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
                res = (list(res[:-1]), res[-1])
            if res and isinstance(res[0], TypeVar):
                res = ()
            return res or ()
        return ()


    from typing_extensions import Literal
elif sys.version_info < (3, 9):  # pragma: no cover
    _get_origin = get_origin
    _get_args = get_args


    def get_origin(tp):
        if isinstance(tp, _AnnotatedAlias):
            return Annotated
        return _get_origin(tp)


    def get_args(tp):
        if isinstance(tp, _AnnotatedAlias):
            return (tp.__origin__,) + tp.__metadata__
        return _get_args(tp)

if sys.version_info < (3, 9):  # pragma: no cover
    _RECURSIVE_GUARD = False
else:
    _RECURSIVE_GUARD = True

_GenericBases = []
for _name in (
        'GenericAlias',
        '_GenericAlias',
        '_SpecialForm',
):
    if hasattr(typing, _name):  # pragma: no cover
        _GenericBases.append(getattr(typing, _name))
_GenericBases = tuple(_GenericBases)
