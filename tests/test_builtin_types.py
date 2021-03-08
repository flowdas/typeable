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
)
from typeable import *

#
# None
#


def test_None():
    assert cast(type(None), None) is None
    with pytest.raises(TypeError):
        cast(type(None), object())

#
# bool
#


def test_bool():
    # str
    assert cast(bool, 'false') is False
    assert cast(bool, 'true') is True
    assert cast(bool, 'fAlSe') is False
    assert cast(bool, 'tRuE') is True
    with pytest.raises(ValueError):
        cast(bool, 'SUCCESS')
    ctx = Context(bool_strings={})
    with pytest.raises(TypeError):
        cast(bool, 'SUCCESS', ctx=ctx)

    # int
    assert cast(bool, 0) is False
    assert cast(bool, 1) is True
    assert cast(bool, 2) is True
    with pytest.raises(ValueError):
        cast(bool, 2, ctx=Context(lossy_conversion=False))
    with pytest.raises(TypeError):
        cast(bool, 0, ctx=Context(bool_is_int=False))

    # bool
    assert cast(bool, False) is False
    assert cast(bool, True) is True

    # float
    with pytest.raises(TypeError):
        cast(bool, 0.0)
    with pytest.raises(TypeError):
        cast(bool, 1.0)

#
# int
#


def test_int():
    # str
    assert cast(int, "123") == 123

    # bool
    assert cast(int, True) == 1
    with pytest.raises(TypeError):
        cast(int, True, ctx=Context(bool_is_int=False))

    # float
    assert cast(int, 123.456) == 123
    with pytest.raises(ValueError):
        cast(int, 123.456, ctx=Context(lossy_conversion=False))

    # complex
    with pytest.raises(TypeError):
        cast(int, complex())

    # int
    assert cast(int, 123) == 123


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
