from dataclasses import dataclass, field
from datetime import datetime, timezone
import operator
from typing import Annotated

import pytest

from typeable import Metadata, enforce_constraints, typecast
from typeable._constraint import (
    ExclusiveMaximum,
    ExclusiveMinimum,
    Maximum,
    Minimum,
    V,
)


def test_quiet():
    def func(val, before):
        return None

    assert typecast(Annotated[str, V.validate(func, quiet=True)], "hello") == "hello"

    with pytest.raises(TypeError):
        typecast(Annotated[str, V.validate(func)], "hello")


def test_enforce_constraints():
    @dataclass
    class X:
        i: int = 0

    @dataclass
    class Y:
        i: int = 0

        def __post_init__(self):
            enforce_constraints(self, V.minProperties(1))

    assert typecast(X, {"i": 1}) == X(i=1)
    assert typecast(X, {"i": 0}) == X(i=0)
    assert typecast(X, {}) == X(i=0)

    assert typecast(Y, {"i": 1}) == Y(i=1)
    assert typecast(Y, {"i": 0}) == Y(i=0)
    with pytest.raises(ValueError):
        typecast(Y, {})


@pytest.mark.parametrize(
    "op, Class, RClass",
    [
        (operator.__gt__, ExclusiveMinimum, ExclusiveMaximum),
        (operator.__ge__, Minimum, Maximum),
        (operator.__lt__, ExclusiveMaximum, ExclusiveMinimum),
        (operator.__le__, Maximum, Minimum),
    ],
)
def test_comparison(op, Class, RClass):
    c = op(V, 3)
    assert isinstance(c, Class)

    c = op(3, V)
    assert isinstance(c, RClass)


def test_Minimum():
    assert typecast(Annotated[int, V >= 1], 1) == 1
    assert typecast(Annotated[int, 1 <= V], 1) == 1

    with pytest.raises(ValueError):
        typecast(Annotated[int, V >= 1], 0)

    with pytest.raises(ValueError):
        typecast(Annotated[int, 1 <= V], 0)


def test_Maximum():
    assert typecast(Annotated[int, V <= 1], 1) == 1
    assert typecast(Annotated[int, 1 >= V], 1) == 1

    with pytest.raises(ValueError):
        typecast(Annotated[int, V <= 1], 2)

    with pytest.raises(ValueError):
        typecast(Annotated[int, 1 >= V], 2)


def test_ExclusiveMinimum():
    assert typecast(Annotated[int, V > 1], 2) == 2
    assert typecast(Annotated[int, 1 < V], 2) == 2

    with pytest.raises(ValueError):
        typecast(Annotated[int, V > 1], 1)

    with pytest.raises(ValueError):
        typecast(Annotated[int, 1 < V], 1)


def test_ExclusiveMaximum():
    assert typecast(Annotated[int, V < 1], 0) == 0
    assert typecast(Annotated[int, 1 > V], 0) == 0

    with pytest.raises(ValueError):
        typecast(Annotated[int, V < 1], 1)

    with pytest.raises(ValueError):
        typecast(Annotated[int, 1 > V], 1)


@pytest.mark.parametrize(
    "T, val, empty",
    [
        (list, list("hello"), []),
        (tuple, tuple("hello"), ()),
    ],
)
def test_MinItems(T, val, empty):
    assert typecast(Annotated[T, V.minItems(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minItems(1)], empty)


@pytest.mark.parametrize(
    "T, val",
    [
        (list, list("hello")),
        (tuple, tuple("hello")),
    ],
)
def test_MaxItems(T, val):
    assert typecast(Annotated[T, V.maxItems(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.maxItems(4)], val)


@pytest.mark.parametrize(
    "T, val, empty",
    [
        (bytes, b"hello", b""),
        (str, "hello", ""),
    ],
)
def test_MinLength(T, val, empty):
    assert typecast(Annotated[T, V.minLength(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minLength(1)], empty)


@pytest.mark.parametrize(
    "T, val",
    [
        (bytes, b"hello"),
        (str, "hello"),
    ],
)
def test_MaxLength(T, val):
    assert typecast(Annotated[T, V.maxLength(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.maxLength(4)], val)


@pytest.mark.parametrize(
    "T, val, empty",
    [
        (dict, dict(zip("abcde", "hello")), {}),
    ],
)
def test_MinProperties(T, val, empty):
    assert typecast(Annotated[T, V.minProperties(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minProperties(1)], empty)


@pytest.mark.parametrize(
    "T, val",
    [
        (dict, dict(zip("abcde", "hello"))),
    ],
)
def test_MaxProperties(T, val):
    assert typecast(Annotated[T, V.maxProperties(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.maxProperties(4)], val)


def test_HasAny():
    assert typecast(Annotated[dict, V.hasAny("i", "j")], {"i": 0, "j": 0}) == {
        "i": 0,
        "j": 0,
    }
    assert typecast(Annotated[dict, V.hasAny("i", "j")], {"i": 0}) == {"i": 0}
    assert typecast(Annotated[dict, V.hasAny("i", "j")], {"j": 0}) == {"j": 0}
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasAny("i", "j")], {})

    @dataclass
    class X:
        i: int = 0
        j: int = 0

    assert typecast(Annotated[X, V.hasAny("i", "j")], {"i": 0, "j": 0}) == X()
    assert typecast(Annotated[X, V.hasAny("i", "j")], {"i": 0}) == X()
    assert typecast(Annotated[X, V.hasAny("i", "j")], {"j": 0}) == X()
    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasAny("i", "j")], {})


def test_HasAny_alias():
    @dataclass
    class X:
        i: int = field(default=0, metadata=Metadata(alias="$i"))
        j: int = 0

    assert typecast(Annotated[X, V.hasAny("i", "j")], {"$i": 0, "j": 0}) == X()
    assert typecast(Annotated[X, V.hasAny("i", "j")], {"$i": 0}) == X()
    assert typecast(Annotated[X, V.hasAny("i", "j")], {"j": 0}) == X()
    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasAny("i", "j")], {})


def test_HasOne():
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasOne("i", "j")], {"i": 0, "j": 0})
    assert typecast(Annotated[dict, V.hasOne("i", "j")], {"i": 0}) == {"i": 0}
    assert typecast(Annotated[dict, V.hasOne("i", "j")], {"j": 0}) == {"j": 0}
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasOne("i", "j")], {})

    @dataclass
    class X:
        i: int = 0
        j: int = 0

    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasOne("i", "j")], {"i": 0, "j": 0})
    assert typecast(Annotated[X, V.hasOne("i", "j")], {"i": 0}) == X()
    assert typecast(Annotated[X, V.hasOne("i", "j")], {"j": 0}) == X()
    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasOne("i", "j")], {})


def test_HasOne_alias():
    @dataclass
    class X:
        i: int = field(default=0, metadata=Metadata(alias="$i"))
        j: int = 0

    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasOne("i", "j")], {"$i": 0, "j": 0})
    assert typecast(Annotated[X, V.hasOne("i", "j")], {"$i": 0}) == X()
    assert typecast(Annotated[X, V.hasOne("i", "j")], {"j": 0}) == X()
    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasOne("i", "j")], {})


def test_HasNotAll():
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasNotAll("i", "j")], {"i": 0, "j": 0})
    assert typecast(Annotated[dict, V.hasNotAll("i", "j")], {"i": 0}) == {"i": 0}
    assert typecast(Annotated[dict, V.hasNotAll("i", "j")], {"j": 0}) == {"j": 0}
    assert typecast(Annotated[dict, V.hasNotAll("i", "j")], {}) == {}

    @dataclass
    class X:
        i: int = 0
        j: int = 0

    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasNotAll("i", "j")], {"i": 0, "j": 0})
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {"i": 0}) == X()
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {"j": 0}) == X()
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {}) == X()


def test_HasNotAll_alias():
    @dataclass
    class X:
        i: int = field(default=0, metadata=Metadata(alias="$i"))
        j: int = 0

    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasNotAll("i", "j")], {"$i": 0, "j": 0})
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {"$i": 0}) == X()
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {"j": 0}) == X()
    assert typecast(Annotated[X, V.hasNotAll("i", "j")], {}) == X()


def test_HasConst():
    assert typecast(Annotated[dict, V.hasConst("i", 0)], {"i": 0}) == {
        "i": 0,
    }
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasConst("i", 0)], {})
    with pytest.raises(ValueError):
        typecast(Annotated[dict, V.hasConst("i", 0)], {"i": ""})

    @dataclass
    class X:
        i: int = 0

    assert typecast(Annotated[X, V.hasConst("i", 0)], {"i": 0}) == X()
    assert typecast(Annotated[X, V.hasConst("i", 0)], {}) == X()
    with pytest.raises(ValueError):
        typecast(Annotated[X, V.hasConst("i", 0)], {"i": 1})


@pytest.mark.parametrize(
    "T, val",
    [
        (list, list("hello")),
        (tuple, tuple("hello")),
    ],
)
def test_fixed_items(T, val):
    assert typecast(Annotated[T, V.minItems(5), V.maxItems(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minItems(4), V.maxItems(4)], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minItems(6), V.maxItems(6)], val)


@pytest.mark.parametrize(
    "T, val",
    [
        (bytes, b"hello"),
        (str, "hello"),
    ],
)
def test_fixed_length(T, val):
    assert typecast(Annotated[T, V.minLength(5), V.maxLength(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minLength(4), V.maxLength(4)], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minLength(6), V.maxLength(6)], val)


@pytest.mark.parametrize(
    "T, val",
    [
        (dict, dict(zip("abcde", "hello"))),
    ],
)
def test_fixed_properties(T, val):
    assert typecast(Annotated[T, V.minProperties(5), V.maxProperties(5)], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minProperties(4), V.maxProperties(4)], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.minProperties(6), V.maxProperties(6)], val)


def test_MultipleOf():
    assert typecast(Annotated[int, V.multipleOf(2)], 36) == 36

    with pytest.raises(ValueError):
        typecast(Annotated[int, V.multipleOf(2)], 35)


def test_Pattern():
    P = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    s = "john.doe@example.com"
    assert typecast(Annotated[str, V.pattern(P)], s) == s

    with pytest.raises(ValueError):
        typecast(Annotated[str, V.pattern(P)], "foo")


@pytest.mark.parametrize(
    "v",
    [
        [1, 2, 3],  # hashable
        [[1], [2], [3]],  # unhashable
    ],
)
def test_Unique(v):
    assert typecast(Annotated[list, V.uniqueItems()], v) is v

    with pytest.raises(ValueError):
        typecast(Annotated[list, V.uniqueItems()], v + [v[0]])


def test_Validator():
    assert (
        typecast(Annotated[str, V.validate(lambda s, _: s.startswith("h"))], "hello")
        == "hello"
    )

    with pytest.raises(ValueError):
        typecast(Annotated[str, V.validate(lambda s, _: s.startswith("w"))], "hello")


@pytest.mark.parametrize(
    "format, val",
    [
        ("email", "random+test@gmail.com"),
        ("media-range", "text/*;q=0.3"),
        ("regex", "^x-"),
        ("uri", "https://json-schema.org/draft/2020-12/schema"),
        ("uri-reference", "https://json-schema.org/draft/2020-12/meta/core"),
        ("uri-reference", "#meta"),
        ("uri-reference", "#/$defs/anchorString"),
    ],
)
def test_Format_valid(format, val):
    assert typecast(Annotated[str, V.format(format)], val) == val


@pytest.mark.parametrize(
    "format, val",
    [
        ("email", "@gmail.com"),
        ("media-range", "*"),
        ("regex", "([a-z]+$"),
        ("uri", "https//json-schema.org/draft/2020-12/schema"),
        ("uri-reference", "https //json-schema.org/draft/2020-12/meta/core"),
        ("uri-reference", "http://example.com/file[/].html"),
        ("uri-reference", "$defs\\anchorString"),
    ],
)
def test_Format_invalid(format, val):
    with pytest.raises(ValueError):
        typecast(Annotated[str, V.format(format)], val)


def test_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    DT = "1970-01-01T00:00:00.000"

    assert typecast(datetime, DT) == naive_epoch
    assert typecast(datetime, DT + "Z") == aware_epoch
    assert typecast(Annotated[datetime, V.localTime()], DT) == naive_epoch
    assert typecast(Annotated[datetime, V.zonedTime()], DT + "Z") == aware_epoch

    with pytest.raises(ValueError):
        typecast(Annotated[datetime, V.localTime()], DT + "Z")
    with pytest.raises(ValueError):
        typecast(Annotated[datetime, V.zonedTime()], DT)
