from collections.abc import Callable
import sys
from typing import Any
import typing

import pytest

from typeable import typecast


class OuterClass:
    class InnerClass:
        pass


class MyClass:
    def method(self): ...


@pytest.mark.parametrize("T", [Callable, typing.Callable])
def test_str(T):
    assert typecast(T, "callable") is callable
    with pytest.raises(TypeError):
        typecast(T[[], Any], "callable")

    assert typecast(T, "sys.exc_info") is sys.exc_info
    with pytest.raises(TypeError):
        typecast(T[[int], Any], "sys.exc_info")

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


@pytest.mark.parametrize("T", [Callable, typing.Callable])
def test_None(T):
    with pytest.raises(TypeError):
        typecast(T, None)
    with pytest.raises(TypeError):
        typecast(T[..., Any], None)
