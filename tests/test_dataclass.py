from dataclasses import dataclass
from typing import Literal

import pytest

from typeable import deepcast, capture


def test_cast():
    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = deepcast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]


def test_required():
    @dataclass
    class X:
        a: int
        b: int = 2

    data = {"a": 1}
    x = deepcast(X, data)
    assert x.a == 1
    assert x.b == 2

    data = {"b": 1}
    with pytest.raises(TypeError):
        deepcast(X, data)


def test_dict():
    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = deepcast(X, data)
    assert deepcast(dict, x) == data


@pytest.mark.skip(reason="JsonValue 제거")
def test_JsonValue():
    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = deepcast(X, data)
    assert deepcast(JsonValue, x) == data  # type: ignore  # noqa: F821

    assert deepcast(JsonValue, {"result": X(**data)}) == {"result": data}  # type: ignore  # noqa: F821


def test_Literal():
    @dataclass
    class X:
        i: Literal[1, 2, 3]

    data = {"i": 1}

    x = deepcast(X, data)
    assert deepcast(dict, x) == data

    data = {"i": 0}
    with pytest.raises(TypeError):
        deepcast(X, data)


def test_capture_with_type_mismatch():
    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {"i": 0})
    assert error.location == ("i",)


def test_capture_with_missing_field():
    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {})
    assert error.location == ("i",)

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {"i": 1, "j": 0})
    assert error.location == ("j",)


def test_capture_with_extra_field():
    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {"i": 1, "j": 0})
    assert error.location == ("j",)
