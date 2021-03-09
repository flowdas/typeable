# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import cmath
import collections
import math
import sys
import pytest

from typeable.typing import (
    Dict,
    FrozenSet,
    List,
    Set,
)
from typeable import *

#
# object
#


def test_object():
    # None
    cast(object, None).__class__ is object

    # object
    assert cast(object, object()).__class__ is object

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

#
# float
#


def test_float():
    # str
    assert cast(float, "123.456") == 123.456
    assert math.isnan(cast(float, "nan"))
    with pytest.raises(ValueError):
        cast(float, "nan", ctx=Context(accept_nan=False))
    with pytest.raises(ValueError):
        cast(float, "inf", ctx=Context(accept_nan=False))

    # bool
    assert cast(float, True) == 1.0
    with pytest.raises(TypeError):
        cast(float, True, ctx=Context(bool_is_int=False))

    # int
    assert cast(float, 123) == 123

    # complex
    with pytest.raises(TypeError):
        cast(float, complex())

    # float
    assert cast(float, 123.456) == 123.456

#
# complex
#


def test_complex():
    # str
    assert cast(complex, "123+456j") == complex(123, 456)
    assert cmath.isnan(cast(complex, "nan+nanj"))
    with pytest.raises(ValueError):
        cast(complex, "nan+nanj", ctx=Context(accept_nan=False))
    with pytest.raises(ValueError):
        cast(complex, "inf", ctx=Context(accept_nan=False))

    # bool
    assert cast(complex, True) == 1.0+0j
    with pytest.raises(TypeError):
        cast(complex, True, ctx=Context(bool_is_int=False))

    # int
    assert cast(complex, 123) == 123+0j

    # float
    assert cast(complex, 123.456) == 123.456+0j

    # complex
    with pytest.raises(TypeError):
        cast(float, complex())

    # complex
    assert cast(complex, complex(123, 456)) == complex(123, 456)

#
# str
#


def test_str():
    # bool
    assert cast(str, True) == 'True'

    # int
    assert cast(str, 123) == '123'

    # float
    assert cast(str, 123.456) == str(123.456)

    # complex
    assert cast(str, complex(1, 2)) == '(1+2j)'

    # bytes
    assert cast(str, b'hello') == 'hello'

    # bytearray
    assert cast(str, bytearray(b'hello')) == 'hello'

    # object
    with pytest.raises(TypeError):
        cast(str, object())
    print(object)
    cast(str, object(), ctx=Context(strict_str=False))

    # None
    with pytest.raises(TypeError):
        cast(str, None)
    with pytest.raises(TypeError):
        cast(str, None, ctx=Context(strict_str=False))

    # str
    assert cast(str, 'hello') == 'hello'

#
# bytes
#


def test_bytes():
    # str
    assert cast(bytes, 'hello') == b'hello'

    # list[int]
    assert cast(bytes, [0, 1, 2, 3, 4]) == b'\x00\x01\x02\x03\x04'

    # int
    with pytest.raises(TypeError):
        cast(bytes, 5)

    # None
    with pytest.raises(TypeError):
        cast(bytes, None)

    # bytearray
    assert cast(bytes, bytearray(b'hello')) == b'hello'

    # bytes
    assert cast(bytes, b'hello') == b'hello'

#
# bytearray
#


def test_bytearray():
    # str
    assert cast(bytearray, 'hello') == bytearray(b'hello')

    # list[int]
    assert cast(bytearray, [0, 1, 2, 3, 4]) == bytearray(
        b'\x00\x01\x02\x03\x04')

    # int
    with pytest.raises(TypeError):
        cast(bytearray, 5)

    # None
    with pytest.raises(TypeError):
        cast(bytearray, None)

    # bytes
    assert cast(bytearray, b'hello') == bytearray(b'hello')

    # bytearray
    assert cast(bytearray, bytearray(b'hello')) == bytearray(b'hello')

#
# list
#


def test_list():
    # dict
    assert cast(list, {'a': 1, 'b': 2}) == [('a', 1), ('b', 2)]

    # None
    with pytest.raises(TypeError):
        cast(list, None)

    # list
    class X(Object):
        i: int

    data = [{'i': i} for i in range(10)]

    l = cast(List, data)
    assert isinstance(l, list)
    assert l == data

    l = cast(list, data)
    assert isinstance(l, list)
    assert l == data

    # generic list
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

#
# dict
#


def test_dict():
    # mapping
    d = {'a': 1, 'b': 2}
    r = cast(dict, collections.OrderedDict(d))
    assert r == {'a': 1, 'b': 2}
    assert r.__class__ is dict

    # list
    assert cast(dict, [('a', 1), ('b', 2)]) == {'a': 1, 'b': 2}

    # None
    with pytest.raises(TypeError):
        cast(dict, None)

    # dict
    class X(Object):
        i: int

    data = {i: {'i': i} for i in range(10)}

    r = cast(Dict, data)
    assert isinstance(r, dict)
    assert r == data

    r = cast(dict, data)
    assert isinstance(r, dict)
    assert r == data

    # generic dict
    r = cast(Dict[str, X], data)

    assert isinstance(r, dict)
    assert len(r) == len(data)
    for i, (k, v) in enumerate(r.items()):
        assert k == str(i)
        assert isinstance(v, X)
        assert v.i == i

    assert cast(Dict[str, int], [('a', 1), ('b', 2)]) == {'a': 1, 'b': 2}

    if sys.version_info >= (3, 9):
        r = cast(dict[str, X], data)

        assert isinstance(r, dict)
        assert len(r) == len(data)
        for i, (k, v) in enumerate(r.items()):
            assert k == str(i)
            assert isinstance(v, X)
            assert v.i == i

#
# set
#


@pytest.mark.parametrize('T,GT', [(set, Set), (frozenset, FrozenSet)])
def test_set(T, GT):
    # dict
    assert cast(T, {'a': 1, 'b': 2}) == {'a', 'b'}

    # None
    with pytest.raises(TypeError):
        cast(T, None)

    # set
    expected = {i for i in range(10)}
    data = {str(v) for v in expected}

    l = cast(GT, data)
    assert isinstance(l, T)
    assert l == data

    l = cast(T, data)
    assert isinstance(l, T)
    assert l == data

    # generic set
    l = cast(GT[int], data)

    assert isinstance(l, T)
    assert l == expected

    if sys.version_info >= (3, 9):
        l = cast(T[int], data)

        assert isinstance(l, T)
        assert l == expected
