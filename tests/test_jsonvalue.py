from dataclasses import dataclass
from typeable import deepcast, JsonValue


def test_embedded():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    expected = {"a": ["0", True, 2, 3.14], "b": [0, 1, 2, 3]}
    assert deepcast(JsonValue, data) == expected


def test_simple():
    assert deepcast(JsonValue, None) is None
    assert deepcast(JsonValue, True) is True
    assert deepcast(JsonValue, False) is False
    assert deepcast(JsonValue, 123) == 123
    assert deepcast(JsonValue, 123.456) == 123.456
    assert deepcast(JsonValue, "hello") == "hello"
    assert deepcast(JsonValue, "") == ""
    assert deepcast(JsonValue, []) == []
    assert deepcast(JsonValue, {}) == {}
    assert deepcast(JsonValue, ()) == ()


def test_Iterable():
    assert deepcast(JsonValue, range(4)) == [0, 1, 2, 3]


def test_dataclass():
    @dataclass
    class X:
        i: int

    x = X(i=3)
    v = [x]
    assert deepcast(JsonValue, x) == {"i": 3}
    assert deepcast(JsonValue, v) == [{"i": 3}]
