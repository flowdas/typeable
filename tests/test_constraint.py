import operator
from typing import Annotated

import pytest

from typeable import typecast
from typeable._constraint import (
    ExclusiveMaximum,
    ExclusiveMinimum,
    MaxLength,
    Maximum,
    MinLength,
    Minimum,
    V,
)


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
    "op, Class, RClass",
    [
        (operator.__gt__, MinLength, MaxLength),
        (operator.__ge__, MinLength, MaxLength),
        (operator.__lt__, MaxLength, MinLength),
        (operator.__le__, MaxLength, MinLength),
    ],
)
def test_length(op, Class, RClass):
    c = op(V.length, 3)
    assert isinstance(c, Class)

    c = op(3, V.length)
    assert isinstance(c, RClass)


@pytest.mark.parametrize(
    "T, val, empty",
    [
        (bytes, b"hello", b""),
        (dict, dict(zip("abcde", "hello")), {}),
        (list, list("hello"), []),
        (str, "hello", ""),
        (tuple, tuple("hello"), ()),
    ],
)
def test_MinLength(T, val, empty):
    assert typecast(Annotated[T, V.length >= 5], val) == val
    assert typecast(Annotated[T, 5 <= V.length], val) == val
    assert typecast(Annotated[T, V.length > 4], val) == val
    assert typecast(Annotated[T, 4 < V.length], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length >= 1], empty)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 1 <= V.length], empty)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length > 0], empty)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 0 < V.length], empty)


@pytest.mark.parametrize(
    "T, val",
    [
        (bytes, b"hello"),
        (dict, dict(zip("abcde", "hello"))),
        (list, list("hello")),
        (str, "hello"),
        (tuple, tuple("hello")),
    ],
)
def test_MaxLength(T, val):
    assert typecast(Annotated[T, V.length <= 5], val) == val
    assert typecast(Annotated[T, 5 >= V.length], val) == val
    assert typecast(Annotated[T, V.length < 6], val) == val
    assert typecast(Annotated[T, 6 > V.length], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length <= 4], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 4 >= V.length], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length < 5], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 5 > V.length], val)


@pytest.mark.parametrize(
    "T, val",
    [
        (bytes, b"hello"),
        (dict, dict(zip("abcde", "hello"))),
        (list, list("hello")),
        (str, "hello"),
        (tuple, tuple("hello")),
    ],
)
def test_fixed_length(T, val):
    assert typecast(Annotated[T, V.length == 5], val) == val
    assert typecast(Annotated[T, 5 == V.length], val) == val

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length == 4], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 4 == V.length], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, V.length == 6], val)

    with pytest.raises(ValueError):
        typecast(Annotated[T, 6 == V.length], val)


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


def test_Unique():
    v = [1, 2, 3]
    assert typecast(Annotated[list, V.unique()], v) is v

    with pytest.raises(ValueError):
        typecast(Annotated[list, V.unique()], v + [v[0]])


def test_Validator():
    assert (
        typecast(Annotated[str, V.validate(lambda s: s.startswith("h"))], "hello")
        == "hello"
    )

    with pytest.raises(ValueError):
        typecast(Annotated[str, V.validate(lambda s: s.startswith("w"))], "hello")


@pytest.mark.parametrize(
    "format, val",
    [
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
