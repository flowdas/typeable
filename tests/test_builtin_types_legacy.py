import cmath
from typing import Any, FrozenSet, Optional, Set, Type

from typeable import deepcast, localcontext

import pytest


#
# None
#


def test_None():
    assert deepcast(Any, None) is None
    assert deepcast(Optional[int], None) is None


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
    assert deepcast(complex, complex(123, 456)) == complex(123, 456)


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
# frozenset
#


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
