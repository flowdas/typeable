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
    Any,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Type,
)
from typeable import *


#
# object
#


def test_object():
    # None
    assert cast(object, None) is None

    # object
    assert cast(object, object()).__class__ is object

    # custom class
    class X:
        pass

    x = X()
    assert cast(X, x) is x

    with pytest.raises(TypeError):
        cast(X, '')


#
# None
#


def test_None():
    assert cast(type(None), None) is None
    assert cast(object, None) is None
    assert cast(Any, None) is None
    assert cast(Optional[int], None) is None
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
    assert cast(int, "123", ctx=Context(lossy_conversion=False)) == 123

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

    # bool
    assert cast(complex, True) == 1.0 + 0j
    with pytest.raises(TypeError):
        cast(complex, True, ctx=Context(bool_is_int=False))

    # int
    assert cast(complex, 123) == 123 + 0j

    # float
    assert cast(complex, 123.456) == 123.456 + 0j

    # tuple
    assert cast(complex, [123, 456]) == complex(123, 456)
    assert cast(complex, (123, 456)) == complex(123, 456)

    # complex
    with pytest.raises(TypeError):
        cast(float, complex())

    # complex
    assert cast(complex, complex(123, 456)) == complex(123, 456)


#
# str
#


def test_str():
    from datetime import datetime

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
    cast(str, object(), ctx=Context(strict_str=False))

    # type
    assert cast(str, int) == 'builtins.int'
    assert cast(str, datetime) == 'datetime.datetime'
    assert cast(str, OuterClass) == 'tests.test_builtin_types.OuterClass'
    assert cast(str, OuterClass.InnerClass) == 'tests.test_builtin_types.OuterClass.InnerClass'

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

    # no copy
    data = list(range(10))
    assert cast(list, data) is data
    assert cast(List, data) is data
    assert cast(List[int], data) is data

    # copy
    data = list(range(9))
    data.append('9')
    expected = list(range(10))

    assert cast(list, data) is data
    assert cast(List, data) is data
    assert cast(List[int], data) == expected
    assert cast(List[int], tuple(data)) == expected


#
# dict
#


def test_dict():
    # mapping
    d = {'a': 1, 'b': 2}
    r = cast(dict, collections.OrderedDict(d))
    assert r == {'a': 1, 'b': 2}

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

    # no copy
    data = {str(i): i for i in range(10)}
    assert cast(dict, data) is data
    assert cast(Dict, data) is data
    assert cast(Dict[str, int], data) is data

    # copy
    expected = data.copy()
    data['9'] = '9'

    assert cast(dict, data) is data
    assert cast(Dict, data) is data
    assert cast(Dict[str, int], data) == expected
    assert cast(Dict[str, int], collections.UserDict(data)) == expected


#
# set
#


def test_set():
    # dict
    assert cast(set, {'a': 1, 'b': 2}) == {'a', 'b'}

    # None
    with pytest.raises(TypeError):
        cast(set, None)

    # set
    expected = set(range(10))
    data = set(str(v) for v in expected)

    l = cast(Set, data)
    assert isinstance(l, set)
    assert l == data

    l = cast(set, data)
    assert isinstance(l, set)
    assert l == data

    # generic set
    l = cast(Set[int], data)

    assert isinstance(l, set)
    assert l == expected

    if sys.version_info >= (3, 9):
        l = cast(set[int], data)

        assert isinstance(l, set)
        assert l == expected

    # no copy
    data = set(range(10))
    assert cast(set, data) is data
    assert cast(Set, data) is data
    assert cast(Set[int], data) is data

    # copy
    data = set(range(9))
    data.add('9')
    expected = set(range(10))

    assert cast(set, data) is data
    assert cast(Set, data) is data
    assert cast(Set[int], data) == expected
    assert cast(Set[int], frozenset(data)) == expected


def test_frozenset():
    # dict
    assert cast(frozenset, {'a': 1, 'b': 2}) == frozenset({'a', 'b'})

    # None
    with pytest.raises(TypeError):
        cast(frozenset, None)

    # frozenset
    expected = frozenset(range(10))
    data = frozenset(str(v) for v in expected)

    l = cast(FrozenSet, data)
    assert isinstance(l, frozenset)
    assert l == data

    l = cast(frozenset, data)
    assert isinstance(l, frozenset)
    assert l == data

    # generic set
    l = cast(FrozenSet[int], data)

    assert isinstance(l, frozenset)
    assert l == expected

    if sys.version_info >= (3, 9):
        l = cast(frozenset[int], data)

        assert isinstance(l, frozenset)
        assert l == expected

    # no copy
    data = frozenset(range(10))
    assert cast(frozenset, data) is data
    assert cast(FrozenSet, data) is data
    assert cast(FrozenSet[int], data) is data

    # copy
    data = set(range(9))
    data.add('9')
    data = frozenset(data)
    expected = frozenset(range(10))

    assert cast(frozenset, data) is data
    assert cast(FrozenSet, data) is data
    assert cast(FrozenSet[int], data) == expected
    assert cast(FrozenSet[int], set(data)) == expected


#
# tuple
#


def test_tuple():
    # dict
    assert cast(tuple, {'a': 1, 'b': 2}) == (('a', 1), ('b', 2))

    # None
    with pytest.raises(TypeError):
        cast(tuple, None)

    # homogeneous tuple
    expected = tuple(range(10))
    data = tuple(str(i) for i in range(10))

    l = cast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = cast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # homogeneous generic tuple
    l = cast(Tuple[int, ...], data)

    assert isinstance(l, tuple)
    assert l == expected

    if sys.version_info >= (3, 9):
        l = cast(tuple[int, ...], data)

        assert isinstance(l, tuple)
        assert l == expected

    # homogeneous no copy
    data = tuple(range(10))
    assert cast(tuple, data) is data
    assert cast(Tuple, data) is data
    assert cast(Tuple[int, ...], data) is data

    # homogeneous copy
    data = tuple(range(9)) + ('9',)
    expected = tuple(range(10))
    assert cast(tuple, data) is data
    assert cast(Tuple, data) is data
    assert cast(Tuple[int, ...], data) == expected
    assert cast(Tuple[int, ...], list(range(9)) + ['9']) == expected

    # heterogeneous tuple
    data = (1, "2", "3")
    expected = ("1", 2, "3")

    l = cast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = cast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # heterogeneous generic tuple
    l = cast(Tuple[str, int, str], data)

    assert isinstance(l, tuple)
    assert l == expected

    l = cast(Tuple[str, int, str], list(data))

    assert isinstance(l, tuple)
    assert l == expected

    assert cast(Tuple[int, int, int], data) == (1, 2, 3)
    assert cast(Tuple[int, int, int], list(data)) == (1, 2, 3)

    if sys.version_info >= (3, 9):
        l = cast(tuple[str, int, str], data)

        assert isinstance(l, tuple)
        assert l == expected

    # empty tuple
    data = ()

    l = cast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = cast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # empty generic tuple
    l = cast(Tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data

    if sys.version_info >= (3, 9):
        l = cast(tuple[()], data)

        assert isinstance(l, tuple)
        assert l == data

    # length mismatch
    with pytest.raises(TypeError):
        cast(Tuple[()], (1,))

    with pytest.raises(TypeError):
        cast(Tuple[int], (1, 2))

    with pytest.raises(TypeError):
        cast(Tuple[int], [1, 2])

    with pytest.raises(TypeError):
        cast(Tuple[int], ())

    with pytest.raises(TypeError):
        cast(Tuple[int], [])

    # complex
    assert cast(tuple, complex(1, 2)) == (1, 2)
    assert cast(Tuple[float, float], complex(1, 2)) == (1, 2)


#
# type
#

class OuterClass:
    class InnerClass:
        pass


def test_type():
    from datetime import datetime
    from collections.abc import Iterable

    # str
    assert cast(type, 'int') == int
    assert cast(Type, 'int') == int
    assert cast(Type[Any], 'int') == int
    assert cast(Type[object], 'int') == int
    assert cast(type, 'datetime.datetime') == datetime
    assert cast(type, 'collections.abc.Iterable') == Iterable
    assert cast(Type[int], 'int') == int
    assert cast(Type[int], 'bool') == bool
    assert cast(type, 'tests.test_builtin_types.OuterClass') is OuterClass
    assert cast(type, 'tests.test_builtin_types.OuterClass.InnerClass') is OuterClass.InnerClass

    with pytest.raises(TypeError):
        cast(type, '')
    with pytest.raises(AttributeError):
        cast(type, 'collections.abc.UNKNOWN_TYPE_NAME')
    with pytest.raises(AttributeError):
        cast(type, 'collections.UNKNOWN_MODULE.Iterable')
    with pytest.raises(TypeError):
        cast(type, 'collections.abc')
    with pytest.raises(TypeError):
        cast(type, 'dataclasses.MISSING')
    with pytest.raises(ModuleNotFoundError):
        cast(type, 'buintins.str')  # mis-spelling
    with pytest.raises(TypeError):
        cast(Type[int], 'str')

    # None
    with pytest.raises(TypeError):
        cast(type, None)
    with pytest.raises(TypeError):
        cast(Type, None)
    with pytest.raises(TypeError):
        cast(Type[Any], None)
    with pytest.raises(TypeError):
        cast(Type[object], None)

    # type
    assert cast(type, int) == int
    assert cast(Type, int) == int
    assert cast(Type[Any], int) == int
    assert cast(Type[object], int) == int
    with pytest.raises(TypeError):
        cast(Type[None], object)
