from typing import Any, Type

import pytest

from typeable import typecast

#
# type
#


class OuterClass:
    class InnerClass:
        pass


def test_type():
    from collections.abc import Iterable
    from datetime import datetime

    # str
    assert typecast(type, "int") == int
    assert typecast(Type, "int") == int
    assert typecast(Type[Any], "int") == int
    assert typecast(Type[object], "int") == int
    assert typecast(type, "datetime.datetime") == datetime
    assert typecast(type, "collections.abc.Iterable") == Iterable
    assert typecast(Type[int], "int") == int
    assert typecast(Type[int], "bool") == bool
    assert typecast(type, "tests.test_builtin_types_legacy.OuterClass") is OuterClass
    assert (
        typecast(type, "tests.test_builtin_types_legacy.OuterClass.InnerClass")
        is OuterClass.InnerClass
    )

    with pytest.raises(TypeError):
        typecast(type, "")
    with pytest.raises(AttributeError):
        typecast(type, "collections.abc.UNKNOWN_TYPE_NAME")
    with pytest.raises(AttributeError):
        typecast(type, "collections.UNKNOWN_MODULE.Iterable")
    with pytest.raises(TypeError):
        typecast(type, "collections.abc")
    with pytest.raises(TypeError):
        typecast(type, "dataclasses.MISSING")
    with pytest.raises(ModuleNotFoundError):
        typecast(type, "buintins.str")  # mis-spelling
    with pytest.raises(TypeError):
        typecast(Type[int], "str")

    # None
    with pytest.raises(TypeError):
        typecast(type, None)
    with pytest.raises(TypeError):
        typecast(Type, None)
    with pytest.raises(TypeError):
        typecast(Type[Any], None)
    with pytest.raises(TypeError):
        typecast(Type[object], None)

    # type
    assert typecast(type, int) == int
    assert typecast(Type, int) == int
    assert typecast(Type[Any], int) == int
    assert typecast(Type[object], int) == int
    with pytest.raises(TypeError):
        typecast(Type[None], object)
