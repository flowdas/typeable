from dataclasses import dataclass
from typing import Union

import pytest

from typeable import declare, typecast


@pytest.mark.parametrize(
    "T",
    [
        Union[bool, int, float, str, list, dict, tuple, None],
        bool | int | float | str | list | dict | tuple | None,
    ],
)
@pytest.mark.parametrize(
    "v",
    [
        True,
        123,
        123.456,
        "hello",
        [123],
        {"hello": 123},
        (123, 456),
        None,
    ],
)
def test_builtins(T, v):
    assert typecast(T, v) is v


def test_recursive_Union():
    with declare("Json") as _Json:
        Json = Union[
            float,
            bool,
            int,
            str,
            None,
            dict[str, _Json],
            list[_Json],
            tuple[_Json, ...],
        ]

    assert typecast(Json, 1) == 1
    assert typecast(Json, 1.0) == 1.0
    assert typecast(Json, "1") == "1"
    assert typecast(Json, True) is True
    assert typecast(Json, None) is None
    assert typecast(Json, {}) == {}
    assert typecast(Json, []) == []
    assert typecast(Json, ()) == ()
    assert typecast(Json, {"k1": 1}) == {"k1": 1}


def test_dataclass():
    @dataclass
    class X:
        i: int

    @dataclass
    class Y:
        j: str

    assert isinstance(typecast(X | Y, {"i": 0}), X)
    assert isinstance(typecast(Y | X, {"i": 0}), X)
    assert isinstance(typecast(X | Y, {"j": "j"}), Y)
    assert isinstance(typecast(Y | X, {"j": "j"}), Y)
