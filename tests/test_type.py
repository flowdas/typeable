from typing import Any, Type

import pytest

from typeable import typecast


class OuterClass:
    class InnerClass:
        pass


@pytest.mark.parametrize("T", [type, Type])
def test_str(T):
    assert typecast(T, "int") is int
    assert typecast(T[Any], "int") is int
    assert typecast(T[object], "int") is int
    _datetime = typecast(T, "datetime.datetime")
    from datetime import datetime

    assert _datetime is datetime

    _Iterable = typecast(T, "collections.abc.Iterable")
    from collections.abc import Iterable

    assert _Iterable is Iterable

    assert typecast(T[int], "int") is int
    assert typecast(T[int], "bool") is bool
    assert typecast(T, "tests.test_type.OuterClass") is OuterClass
    assert typecast(T, "tests.test_type.OuterClass.InnerClass") is OuterClass.InnerClass

    with pytest.raises(TypeError):
        typecast(T, "")
    with pytest.raises(AttributeError):
        typecast(T, "collections.abc.UNKNOWN_TYPE_NAME")
    with pytest.raises(AttributeError):
        typecast(T, "collections.UNKNOWN_MODULE.Iterable")
    with pytest.raises(TypeError):
        typecast(T, "collections.abc")
    with pytest.raises(TypeError):
        typecast(T, "dataclasses.MISSING")
    with pytest.raises(ModuleNotFoundError):
        typecast(T, "buintins.str")  # mis-spelling
    with pytest.raises(TypeError):
        typecast(T[int], "str")


@pytest.mark.parametrize("T", [type, Type])
def test_None(T):
    with pytest.raises(TypeError):
        typecast(T, None)
    with pytest.raises(TypeError):
        typecast(T[Any], None)
    with pytest.raises(TypeError):
        typecast(T[object], None)
