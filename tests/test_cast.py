# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import sys
import pytest
from typeable.typing import (
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)
from typeable import *


def test_get_origin():
    assert get_origin(Type[int]) == type
    assert get_origin(List[int]) == list
    assert get_origin(List) == list
    assert get_origin(Dict[str, str]) == dict
    assert get_origin(Dict) == dict
    assert get_origin(Union[int, None]) == Union


def test_get_args():
    class X(Object):
        i: int

    assert get_args(Type[int]) == (int,)
    assert get_args(List[int]) == (int,)
    assert get_args(List[X]) == (X,)
    assert get_args(List) == ()
    assert get_args(Dict[str, X]) == (str, X)
    assert get_args(Dict) == ()
    assert get_args(Union[int, None]) == (int, type(None))


def test_register():
    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val, ctx) -> Object:
            return cls(val)


def test_invalid_register():
    with pytest.raises(TypeError):
        @cast.register
        def _():
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls, val, ctx):
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls: Object, val, ctx) -> Object:
            pass


def test_double_dispatch():
    class X:
        pass

    class Y(Object):
        pass

    @cast.register
    def _(cls, val: X, ctx) -> Object:
        return 1

    assert cast(Y, X()) == 1
    assert isinstance(cast(Y, {}), Y)

    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val: X, ctx) -> Object:
            return 1


def test_int():
    assert cast(int, "123") == 123


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


def test_dict():
    class X(Object):
        i: int

    data = {i: {'i': i} for i in range(10)}

    r = cast(Dict, data)
    assert isinstance(r, dict)
    assert r == data

    r = cast(dict, data)
    assert isinstance(r, dict)
    assert r == data

    r = cast(Dict[str, X], data)

    assert isinstance(r, dict)
    assert len(r) == len(data)
    for i, (k, v) in enumerate(r.items()):
        assert k == str(i)
        assert isinstance(v, X)
        assert v.i == i

    if sys.version_info >= (3, 9):
        r = cast(dict[str, X], data)

        assert isinstance(r, dict)
        assert len(r) == len(data)
        for i, (k, v) in enumerate(r.items()):
            assert k == str(i)
            assert isinstance(v, X)
            assert v.i == i


def test_Union():
    data = '123'

    r = cast(Union[str, int], data)
    assert r == '123'

    r = cast(Union[int, str], data)
    assert r == 123


def test_Optional():
    assert cast(Optional[int], 1) == 1
    assert cast(Optional[int], None) == None
