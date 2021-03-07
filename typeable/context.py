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
from .typing import get_type_hints

__all__ = [
    'Context',
]

_nulltraverse = nullcontext()


class Error:
    exc_info = None
    location = None


class Context:
    # default policies
    type_is_default_factory: bool = False
    null_is_missing: bool = False
    missing_is_null: bool = False
    null_is_empty: bool = False
    empty_is_null: bool = False
    default_encoding: str = 'utf-8'
    bool_is_int: bool = True
    accept_nan: bool = True
    js_safe_integer: bool = False

    def __init__(self, **policies):
        self._stack = None
        if policies:
            from .cast import cast  # avoid partial import
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
        finally:
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
