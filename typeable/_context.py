# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys
from contextlib import contextmanager

try:
    from contextlib import nullcontext  # since 3.7
except ImportError:  # pragma: no cover
    class nullcontext:
        def __enter__(self):
            pass

        def __exit__(self, *excinfo):
            pass
from .typing import (
    Dict,
    get_type_hints,
)

_nulltraverse = nullcontext()


class Error:
    exc_info = None
    location = None


class Context:
    # default policies
    bool_is_int: bool = True
    bool_strings: Dict[str, bool] = {
        '0': False, '1': True, 'f': False, 'false': False,
        'n': False, 'no': False, 'off': False, 'on': True,
        't': True, 'true': True, 'y': True, 'yes': True,
    }
    bytes_encoding: str = 'utf-8'
    date_format: str = 'iso'
    datetime_format: str = 'iso'
    encoding_errors: str = 'strict'
    lossy_conversion: bool = True
    naive_timestamp: bool = False
    strict_str: bool = True
    time_format: str = 'iso'
    union_prefers_same_type: bool = True
    union_prefers_base_type: bool = True
    union_prefers_super_type: bool = True
    union_prefers_nearest_type: bool = True

    def __init__(self, **policies):
        self._stack = None
        if policies:
            from ._cast import cast  # avoid partial import
            hints = get_type_hints(self.__class__)
            ctx = Context()
            for key, val in policies.items():
                try:
                    cls = hints[key]
                except KeyError:
                    raise TypeError(
                        f"{self.__class__.__qualname__}() got an unexpected keyword argument '{key}'")
                setattr(self, key, cast(cls, val, ctx=ctx))

    @contextmanager
    def capture(self):
        self._stack = []
        error = Error()
        try:
            yield error
        except:
            error.exc_info = sys.exc_info()
            error.location = tuple(self._stack)
            raise
        finally:  # pragma: no cover ; TODO: coverage's bug?
            self._stack = None

    @contextmanager
    def _traverse(self, key):
        self._stack.append(key)
        yield None
        self._stack.pop()

    def traverse(self, key):
        if self._stack is None:
            return _nulltraverse
        else:
            return self._traverse(key)
