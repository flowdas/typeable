import cmath
import collections
from dataclasses import dataclass
import math
from typing import (
    Any,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Type,
)

import pytest

from typeable import (
    deepcast,
    localcontext,
)


#
# object
#


def test_object():
    # None
    assert deepcast(object, None) is None

    # object
    assert deepcast(object, object()).__class__ is object

    # custom class
    class X:
        pass

    x = X()
    assert deepcast(X, x) is x

    with pytest.raises(TypeError):
        deepcast(X, "")


#
# None
#


def test_None():
    assert deepcast(type(None), None) is None
    assert deepcast(object, None) is None
    assert deepcast(Any, None) is None
    assert deepcast(Optional[int], None) is None
    with pytest.raises(TypeError):
        deepcast(type(None), object())


#
# bool
#


def test_bool():
    # str
    assert deepcast(bool, "false") is False
    assert deepcast(bool, "true") is True
    assert deepcast(bool, "fAlSe") is False
    assert deepcast(bool, "tRuE") is True
    with pytest.raises(ValueError):
        deepcast(bool, "SUCCESS")
    with localcontext(bool_strings={}):
        with pytest.raises(TypeError):
            deepcast(bool, "SUCCESS")

    # int
    assert deepcast(bool, 0) is False
    assert deepcast(bool, 1) is True
    assert deepcast(bool, 2) is True
    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            deepcast(bool, 2)
    with localcontext(bool_is_int=False):
        with pytest.raises(TypeError):
            deepcast(bool, 0)

    # bool
    assert deepcast(bool, False) is False
    assert deepcast(bool, True) is True

    # float
    with pytest.raises(TypeError):
        deepcast(bool, 0.0)
    with pytest.raises(TypeError):
        deepcast(bool, 1.0)


#
# int
#


def test_int():
    # str
    assert deepcast(int, "123") == 123
    with localcontext(lossy_conversion=False):
        assert deepcast(int, "123") == 123

    # bool
    assert deepcast(int, True) == 1
    with localcontext(bool_is_int=False):
        with pytest.raises(TypeError):
            deepcast(int, True)

    # float
    assert deepcast(int, 123.456) == 123
    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            deepcast(int, 123.456)

    # complex
    with pytest.raises(TypeError):
        deepcast(int, complex())

    # int
    assert deepcast(int, 123) == 123


#
# float
#


def test_float():
    # str
    assert deepcast(float, "123.456") == 123.456
    assert math.isnan(deepcast(float, "nan"))

    # bool
    assert deepcast(float, True) == 1.0
    with localcontext(bool_is_int=False):
        with pytest.raises(TypeError):
            deepcast(float, True)

    # int
    assert deepcast(float, 123) == 123

    # complex
    with pytest.raises(TypeError):
        deepcast(float, complex())

    # float
    assert deepcast(float, 123.456) == 123.456


#
# complex
#


def test_complex():
    # str
    assert deepcast(complex, "123+456j") == complex(123, 456)
    assert cmath.isnan(deepcast(complex, "nan+nanj"))

    # bool
    assert deepcast(complex, True) == 1.0 + 0j
    with localcontext(bool_is_int=False):
        with pytest.raises(TypeError):
            deepcast(complex, True)

    # int
    assert deepcast(complex, 123) == 123 + 0j

    # float
    assert deepcast(complex, 123.456) == 123.456 + 0j

    # tuple
    assert deepcast(complex, [123, 456]) == complex(123, 456)
    assert deepcast(complex, (123, 456)) == complex(123, 456)

    # complex
    with pytest.raises(TypeError):
        deepcast(float, complex())

    # complex
    assert deepcast(complex, complex(123, 456)) == complex(123, 456)


#
# str
#


def test_str():
    from datetime import datetime

    # bool
    assert deepcast(str, True) == "True"

    # int
    assert deepcast(str, 123) == "123"

    # float
    assert deepcast(str, 123.456) == str(123.456)

    # complex
    assert deepcast(str, complex(1, 2)) == "(1+2j)"

    # bytes
    assert deepcast(str, b"hello") == "hello"

    # bytearray
    assert deepcast(str, bytearray(b"hello")) == "hello"

    # object
    with pytest.raises(TypeError):
        deepcast(str, object())
    with localcontext(strict_str=False):
        deepcast(str, object())

    # type
    assert deepcast(str, int) == "builtins.int"
    assert deepcast(str, datetime) == "datetime.datetime"
    assert deepcast(str, OuterClass) == "tests.test_builtin_types_legacy.OuterClass"
    assert (
        deepcast(str, OuterClass.InnerClass)
        == "tests.test_builtin_types_legacy.OuterClass.InnerClass"
    )

    # None
    with pytest.raises(TypeError):
        deepcast(str, None)
    with localcontext(strict_str=False):
        with pytest.raises(TypeError):
            deepcast(str, None)

    # str
    assert deepcast(str, "hello") == "hello"


#
# bytes
#


def test_bytes():
    # str
    assert deepcast(bytes, "hello") == b"hello"

    # list[int]
    assert deepcast(bytes, [0, 1, 2, 3, 4]) == b"\x00\x01\x02\x03\x04"

    # int
    with pytest.raises(TypeError):
        deepcast(bytes, 5)

    # None
    with pytest.raises(TypeError):
        deepcast(bytes, None)

    # bytearray
    assert deepcast(bytes, bytearray(b"hello")) == b"hello"

    # bytes
    assert deepcast(bytes, b"hello") == b"hello"


#
# bytearray
#


def test_bytearray():
    # str
    assert deepcast(bytearray, "hello") == bytearray(b"hello")

    # list[int]
    assert deepcast(bytearray, [0, 1, 2, 3, 4]) == bytearray(b"\x00\x01\x02\x03\x04")

    # int
    with pytest.raises(TypeError):
        deepcast(bytearray, 5)

    # None
    with pytest.raises(TypeError):
        deepcast(bytearray, None)

    # bytes
    assert deepcast(bytearray, b"hello") == bytearray(b"hello")

    # bytearray
    assert deepcast(bytearray, bytearray(b"hello")) == bytearray(b"hello")


#
# list
#


def test_list():
    # dict
    assert deepcast(list, {"a": 1, "b": 2}) == [("a", 1), ("b", 2)]

    # None
    with pytest.raises(TypeError):
        deepcast(list, None)

    # list
    @dataclass
    class X:
        i: int

    data = [{"i": i} for i in range(10)]

    l = deepcast(List, data)
    assert isinstance(l, list)
    assert l == data

    l = deepcast(list, data)
    assert isinstance(l, list)
    assert l == data

    # generic list
    l = deepcast(List[X], data)

    assert isinstance(l, list)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i

    l = deepcast(list[X], data)

    assert isinstance(l, list)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i

    # no copy
    data = list(range(10))
    assert deepcast(list, data) is data
    assert deepcast(List, data) is data
    assert deepcast(List[int], data) is data

    # copy
    data = list(range(9))
    data.append("9")
    expected = list(range(10))

    assert deepcast(list, data) is data
    assert deepcast(List, data) is data
    assert deepcast(List[int], data) == expected
    assert deepcast(List[int], tuple(data)) == expected


#
# dict
#


def test_dict():
    # mapping
    d = {"a": 1, "b": 2}
    r = deepcast(dict, collections.OrderedDict(d))
    assert r == {"a": 1, "b": 2}

    # list
    assert deepcast(dict, [("a", 1), ("b", 2)]) == {"a": 1, "b": 2}

    # None
    with pytest.raises(TypeError):
        deepcast(dict, None)

    # dict
    @dataclass
    class X:
        i: int

    data = {i: {"i": i} for i in range(10)}

    r = deepcast(Dict, data)
    assert isinstance(r, dict)
    assert r == data

    r = deepcast(dict, data)
    assert isinstance(r, dict)
    assert r == data

    # generic dict
    r = deepcast(Dict[str, X], data)

    assert isinstance(r, dict)
    assert len(r) == len(data)
    for i, (k, v) in enumerate(r.items()):
        assert k == str(i)
        assert isinstance(v, X)
        assert v.i == i

    assert deepcast(Dict[str, int], [("a", 1), ("b", 2)]) == {"a": 1, "b": 2}

    r = deepcast(dict[str, X], data)

    assert isinstance(r, dict)
    assert len(r) == len(data)
    for i, (k, v) in enumerate(r.items()):
        assert k == str(i)
        assert isinstance(v, X)
        assert v.i == i

    # no copy
    data = {str(i): i for i in range(10)}
    assert deepcast(dict, data) is data
    assert deepcast(Dict, data) is data
    assert deepcast(Dict[str, int], data) is data

    # copy
    expected = data.copy()
    data["9"] = "9"

    assert deepcast(dict, data) is data
    assert deepcast(Dict, data) is data
    assert deepcast(Dict[str, int], data) == expected
    assert deepcast(Dict[str, int], collections.UserDict(data)) == expected


#
# set
#


def test_set():
    # dict
    assert deepcast(set, {"a": 1, "b": 2}) == {"a", "b"}

    # None
    with pytest.raises(TypeError):
        deepcast(set, None)

    # set
    expected = set(range(10))
    data = set(str(v) for v in expected)

    l = deepcast(Set, data)
    assert isinstance(l, set)
    assert l == data

    l = deepcast(set, data)
    assert isinstance(l, set)
    assert l == data

    # generic set
    l = deepcast(Set[int], data)

    assert isinstance(l, set)
    assert l == expected

    l = deepcast(set[int], data)

    assert isinstance(l, set)
    assert l == expected

    # no copy
    data = set(range(10))
    assert deepcast(set, data) is data
    assert deepcast(Set, data) is data
    assert deepcast(Set[int], data) is data

    # copy
    data = set(range(9))
    data.add("9")
    expected = set(range(10))

    assert deepcast(set, data) is data
    assert deepcast(Set, data) is data
    assert deepcast(Set[int], data) == expected
    assert deepcast(Set[int], frozenset(data)) == expected


def test_frozenset():
    # dict
    assert deepcast(frozenset, {"a": 1, "b": 2}) == frozenset({"a", "b"})

    # None
    with pytest.raises(TypeError):
        deepcast(frozenset, None)

    # frozenset
    expected = frozenset(range(10))
    data = frozenset(str(v) for v in expected)

    l = deepcast(FrozenSet, data)
    assert isinstance(l, frozenset)
    assert l == data

    l = deepcast(frozenset, data)
    assert isinstance(l, frozenset)
    assert l == data

    # generic set
    l = deepcast(FrozenSet[int], data)

    assert isinstance(l, frozenset)
    assert l == expected

    l = deepcast(frozenset[int], data)

    assert isinstance(l, frozenset)
    assert l == expected

    # no copy
    data = frozenset(range(10))
    assert deepcast(frozenset, data) is data
    assert deepcast(FrozenSet, data) is data
    assert deepcast(FrozenSet[int], data) is data

    # copy
    data = set(range(9))
    data.add("9")
    data = frozenset(data)
    expected = frozenset(range(10))

    assert deepcast(frozenset, data) is data
    assert deepcast(FrozenSet, data) is data
    assert deepcast(FrozenSet[int], data) == expected
    assert deepcast(FrozenSet[int], set(data)) == expected


#
# tuple
#


def test_tuple():
    # dict
    assert deepcast(tuple, {"a": 1, "b": 2}) == (("a", 1), ("b", 2))

    # None
    with pytest.raises(TypeError):
        deepcast(tuple, None)

    # homogeneous tuple
    expected = tuple(range(10))
    data = tuple(str(i) for i in range(10))

    l = deepcast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # homogeneous generic tuple
    l = deepcast(Tuple[int, ...], data)

    assert isinstance(l, tuple)
    assert l == expected

    l = deepcast(tuple[int, ...], data)

    assert isinstance(l, tuple)
    assert l == expected

    # homogeneous no copy
    data = tuple(range(10))
    assert deepcast(tuple, data) is data
    assert deepcast(Tuple, data) is data
    assert deepcast(Tuple[int, ...], data) is data

    # homogeneous copy
    data = tuple(range(9)) + ("9",)
    expected = tuple(range(10))
    assert deepcast(tuple, data) is data
    assert deepcast(Tuple, data) is data
    assert deepcast(Tuple[int, ...], data) == expected
    assert deepcast(Tuple[int, ...], list(range(9)) + ["9"]) == expected

    # heterogeneous tuple
    data = (1, "2", "3")
    expected = ("1", 2, "3")

    l = deepcast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # heterogeneous generic tuple
    l = deepcast(Tuple[str, int, str], data)

    assert isinstance(l, tuple)
    assert l == expected

    l = deepcast(Tuple[str, int, str], list(data))

    assert isinstance(l, tuple)
    assert l == expected

    assert deepcast(Tuple[int, int, int], data) == (1, 2, 3)
    assert deepcast(Tuple[int, int, int], list(data)) == (1, 2, 3)

    l = deepcast(tuple[str, int, str], data)

    assert isinstance(l, tuple)
    assert l == expected

    # empty tuple
    data = ()

    l = deepcast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # empty generic tuple
    l = deepcast(Tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data

    # length mismatch
    with pytest.raises(TypeError):
        deepcast(Tuple[()], (1,))

    with pytest.raises(TypeError):
        deepcast(Tuple[int], (1, 2))

    with pytest.raises(TypeError):
        deepcast(Tuple[int], [1, 2])

    with pytest.raises(TypeError):
        deepcast(Tuple[int], ())

    with pytest.raises(TypeError):
        deepcast(Tuple[int], [])

    # complex
    assert deepcast(tuple, complex(1, 2)) == (1, 2)
    assert deepcast(Tuple[float, float], complex(1, 2)) == (1, 2)


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
    assert deepcast(type, "int") == int
    assert deepcast(Type, "int") == int
    assert deepcast(Type[Any], "int") == int
    assert deepcast(Type[object], "int") == int
    assert deepcast(type, "datetime.datetime") == datetime
    assert deepcast(type, "collections.abc.Iterable") == Iterable
    assert deepcast(Type[int], "int") == int
    assert deepcast(Type[int], "bool") == bool
    assert deepcast(type, "tests.test_builtin_types_legacy.OuterClass") is OuterClass
    assert (
        deepcast(type, "tests.test_builtin_types_legacy.OuterClass.InnerClass")
        is OuterClass.InnerClass
    )

    with pytest.raises(TypeError):
        deepcast(type, "")
    with pytest.raises(AttributeError):
        deepcast(type, "collections.abc.UNKNOWN_TYPE_NAME")
    with pytest.raises(AttributeError):
        deepcast(type, "collections.UNKNOWN_MODULE.Iterable")
    with pytest.raises(TypeError):
        deepcast(type, "collections.abc")
    with pytest.raises(TypeError):
        deepcast(type, "dataclasses.MISSING")
    with pytest.raises(ModuleNotFoundError):
        deepcast(type, "buintins.str")  # mis-spelling
    with pytest.raises(TypeError):
        deepcast(Type[int], "str")

    # None
    with pytest.raises(TypeError):
        deepcast(type, None)
    with pytest.raises(TypeError):
        deepcast(Type, None)
    with pytest.raises(TypeError):
        deepcast(Type[Any], None)
    with pytest.raises(TypeError):
        deepcast(Type[object], None)

    # type
    assert deepcast(type, int) == int
    assert deepcast(Type, int) == int
    assert deepcast(Type[Any], int) == int
    assert deepcast(Type[object], int) == int
    with pytest.raises(TypeError):
        deepcast(Type[None], object)
