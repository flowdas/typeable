from dataclasses import dataclass
from typing import Literal

import pytest

from typeable import deepcast, capture


def test_cast():
    """dict 를 dataclass 로 변환할 수 있다."""

    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = deepcast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]


def test_required():
    """기본값이 있는 필드는 생략할 수 있고, 없는 필드는 필수다."""

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
    """dataclass 는 dict 와 상호 변환되고, 그 과정에서 데이터 소실이 없다."""

    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = deepcast(X, data)
    assert deepcast(dict, x) == data


def test_Literal():
    """dataclass 는 Literal 을 필드로 가질 수 있다."""

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
    """dict -> dataclass 변환은 형 불일치 위치를 보고한다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {"i": 0})
    assert error.location == ("i",)


def test_capture_with_missing_field():
    """dict -> dataclass 변환은 누락 위치를 보고한다."""

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
    """dict -> dataclass 변환은 잉여 필드 위치를 보고한다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(X, {"i": 1, "j": 0})
    assert error.location == ("j",)
