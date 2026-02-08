from dataclasses import dataclass
from typing import Annotated, Union, get_args, get_origin

from typeable import declare, deepcast


def test_get_origin():
    assert get_origin(Union[int, None]) == Union
    assert get_origin(Annotated) is None
    assert get_origin(Annotated[int, lambda: True]) is Annotated


def test_get_args():
    @dataclass
    class X:
        i: int

    assert get_args(Union[int, None]) == (int, type(None))
    assert get_args(Annotated) == ()
    assert get_args(Annotated[int, True, False]) == (int, True, False)


Integer = int


def test_declare():
    with declare("Integer") as Ref:
        T = list[Ref]

    assert deepcast(T, [2]) == [2]
    assert deepcast(T, ["2"]) == [2]
