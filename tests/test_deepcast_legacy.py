from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    FrozenSet,
    List,
    Literal,
    Set,
    Union,
    get_args,
    get_origin,
)

from typeable import declare, deepcast


def test_get_origin():
    assert get_origin(Set[int]) == set
    assert get_origin(Set) == set
    assert get_origin(FrozenSet[int]) == frozenset
    assert get_origin(FrozenSet) == frozenset
    assert get_origin(Union[int, None]) == Union
    assert get_origin(Any) is None
    assert get_origin(Literal) is None
    assert get_origin(Annotated) is None
    assert get_origin(Annotated[int, lambda: True]) is Annotated


def test_get_args():
    @dataclass
    class X:
        i: int

    assert get_args(Set[int]) == (int,)
    assert get_args(Set) == ()
    assert get_args(FrozenSet[int]) == (int,)
    assert get_args(FrozenSet) == ()
    assert get_args(Union[int, None]) == (int, type(None))
    assert get_args(Any) == ()
    assert get_args(Literal) == ()
    assert get_args(Literal["2.0"]) == ("2.0",)
    assert get_args(Annotated) == ()
    assert get_args(Annotated[int, True, False]) == (int, True, False)


Integer = int


def test_declare():
    with declare("Integer") as Ref:
        T = List[Ref]

    assert deepcast(T, [2]) == [2]
    assert deepcast(T, ["2"]) == [2]
