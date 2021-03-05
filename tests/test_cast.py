# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import sys
import pytest
from typeable.typing import (
    List,
    get_args,
)
from typeable import *


def test_get_args():
    class X(Object):
        i: int

    assert get_args(List[int])[0] == int
    assert get_args(List[X])[0] == X


def test_register():
    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val) -> Object:
            return cls(val)


def test_invalid_register():
    with pytest.raises(TypeError):
        @cast.register
        def _():
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls, val):
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls: Object, val) -> Object:
            pass


def test_Object():
    class X(Object):
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert x.i == data['i']


def test_list():
    class X(Object):
        i: int

    data = [{'i': i} for i in range(10)]

    l = cast(List, data)
    assert isinstance(l, list)
    assert l == data

    l = cast(list, data)
    assert isinstance(l, list)
    assert l == data

    l = cast(List[X], data)

    assert isinstance(l, list)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i

    if sys.version_info >= (3, 9):
        l = cast(list[X], data)

        assert isinstance(l, list)
        for i in range(len(data)):
            assert isinstance(l[i], X)
            assert l[i].i == i


def test_int():
    assert cast(int, "123") == 123
