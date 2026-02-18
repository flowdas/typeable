from dataclasses import dataclass, field
from typing import Literal

import pytest

from typeable import capture, localcontext, typecast


def test_cast():
    """dict 를 dataclass 로 변환할 수 있다."""

    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = typecast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]


def test_required():
    """기본값이 있는 필드는 생략할 수 있고, 없는 필드는 필수다."""

    @dataclass
    class X:
        a: int
        b: int = 2

    data = {"a": 1}
    x = typecast(X, data)
    assert x.a == 1
    assert x.b == 2

    data = {"b": 1}
    with pytest.raises(TypeError):
        typecast(X, data)


def test_dict():
    """dataclass 는 dict 와 상호 변환되고, 그 과정에서 데이터 소실이 없다."""

    @dataclass
    class X:
        i: int

    data = {"i": 0}

    x = typecast(X, data)
    assert typecast(dict, x) == data


@pytest.mark.parametrize(
    "frozen",
    [False, True],
)
def test_validate_default(frozen):
    """잘못된 기본값에 대한 처리를 확인한다."""

    @dataclass(frozen=frozen)
    class X:
        i: int = None  # type: ignore
        j: int = field(default_factory=lambda: None)  # type: ignore

    x = typecast(X, dict(i=0, j=0))
    assert x.i == 0
    assert x.j == 0

    with localcontext() as ctx:
        ctx.validate_default = False
        x = typecast(X, {})
        assert isinstance(x, X)
        assert x.i is None
        assert x.j is None

        ctx.validate_default = True
        with pytest.raises(TypeError):
            with capture() as error:
                typecast(X, {})
        assert error.location in {("i",), ("j",)}

        with pytest.raises(TypeError):
            with capture() as error:
                typecast(X, dict(i=0))
        assert error.location == ("j",)

        with pytest.raises(TypeError):
            with capture() as error:
                typecast(X, dict(j=0))
        assert error.location == ("i",)


def test_Literal():
    """dataclass 는 Literal 을 필드로 가질 수 있다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    data = {"i": 1}

    x = typecast(X, data)
    assert typecast(dict, x) == data

    data = {"i": 0}
    with pytest.raises(TypeError):
        typecast(X, data)


def test_capture_with_type_mismatch():
    """dict -> dataclass 변환은 형 불일치 위치를 보고한다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            typecast(X, {"i": 0})
    assert error.location == ("i",)


def test_capture_with_missing_field():
    """dict -> dataclass 변환은 누락 위치를 보고한다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with pytest.raises(TypeError):
        with capture() as error:
            typecast(X, {})
    assert error.location == ("i",)

    with localcontext(allow_extra_items=False):
        with pytest.raises(TypeError):
            with capture() as error:
                typecast(X, {"i": 1, "j": 0})
        assert error.location == ("j",)


def test_capture_with_extra_field():
    """dict -> dataclass 변환은 잉여 필드 위치를 보고한다."""

    @dataclass
    class X:
        i: Literal[1, 2, 3]

    with localcontext(allow_extra_items=False):
        with pytest.raises(TypeError):
            with capture() as error:
                typecast(X, {"i": 1, "j": 0})
        assert error.location == ("j",)


def test_alias():
    """필드에 alias 를 지정하면 dict 로 표현될 때는 필드면 대신 alias 를 사용해야 한다."""

    @dataclass
    class X:
        _schema: str = typecast.field(alias="$schema")

    data = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    x = typecast(X, data)
    assert x._schema == data["$schema"]
    assert typecast(dict, x) == data


def test_hide():
    """필드에 hide=True 를 지정하면 dict 로 표현될 때 생략된다."""

    @dataclass
    class X:
        id: str
        password: str = typecast.field(hide=True)

    data = {"id": "id", "password": "password"}
    x = typecast(X, data)
    assert x.password == "password"
    assert typecast(dict, x) == {"id": "id"}


def test_hide_default_none():
    """hide_default_none 이 참이면 dict 로 표현될 때 기본값으로 사용 중인 None 은 생략된다."""

    @dataclass
    class X:
        mandatory: str
        mandatory2: str | None
        optional: str | None = None
        optional2: str | None = None

    x = X(mandatory="hello", mandatory2=None, optional2="world")

    with localcontext(hide_default_none=False):
        assert typecast(dict, x) == {
            "mandatory": "hello",
            "mandatory2": None,
            "optional": None,
            "optional2": "world",
        }

    with localcontext(hide_default_none=True):
        assert typecast(dict, x) == {
            "mandatory": "hello",
            "mandatory2": None,
            "optional2": "world",
        }


def test_allow_extra_items():
    @dataclass
    class X:
        i: int

    data = {"i": 0, "j": 1}

    with localcontext(allow_extra_items=False):
        with pytest.raises(TypeError):
            typecast(X, data)

    with localcontext(allow_extra_items=True):
        x = typecast(X, data)
        assert x.i == 0
