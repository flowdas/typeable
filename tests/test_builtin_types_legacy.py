from typing import Any, Type

from typeable import deepcast

import pytest


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
