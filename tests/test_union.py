from dataclasses import dataclass
from typing import Union

from typeable import declare, deepcast

import pytest


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
    assert deepcast(T, v) is v


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

    assert deepcast(Json, 1) == 1
    assert deepcast(Json, 1.0) == 1.0
    assert deepcast(Json, "1") == "1"
    assert deepcast(Json, True) is True
    assert deepcast(Json, None) is None
    assert deepcast(Json, {}) == {}
    assert deepcast(Json, []) == []
    assert deepcast(Json, ()) == ()
    assert deepcast(Json, {"k1": 1}) == {"k1": 1}


def test_dataclass():
    @dataclass
    class X:
        i: int

    @dataclass
    class Y:
        j: str

    assert isinstance(deepcast(X | Y, {"i": 0}), X)
    assert isinstance(deepcast(Y | X, {"i": 0}), X)
    assert isinstance(deepcast(X | Y, {"j": "j"}), Y)
    assert isinstance(deepcast(Y | X, {"j": "j"}), Y)
