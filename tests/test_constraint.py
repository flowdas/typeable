from datetime import datetime, timezone
import operator
from typing import Annotated

import pytest

from typeable import typecast
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
