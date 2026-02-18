from dataclasses import dataclass

from typeable import JsonValue, typecast


def test_embedded():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    expected = {"a": ["0", True, 2, 3.14], "b": [0, 1, 2, 3]}
    assert typecast(JsonValue, data) == expected


def test_simple():
    assert typecast(JsonValue, None) is None
    assert typecast(JsonValue, True) is True
    assert typecast(JsonValue, False) is False
    assert typecast(JsonValue, 123) == 123
    assert typecast(JsonValue, 123.456) == 123.456
    assert typecast(JsonValue, "hello") == "hello"
    assert typecast(JsonValue, "") == ""
    assert typecast(JsonValue, []) == []
    assert typecast(JsonValue, {}) == {}
    assert typecast(JsonValue, ()) == ()


def test_Iterable():
    assert typecast(JsonValue, range(4)) == [0, 1, 2, 3]


def test_dataclass():
    @dataclass
    class X:
        i: int

    x = X(i=3)
    v = [x]
    assert typecast(JsonValue, x) == {"i": 3}
    assert typecast(JsonValue, v) == [{"i": 3}]
