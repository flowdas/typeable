from collections import Counter, OrderedDict, defaultdict, namedtuple
import sys
from types import NoneType, UnionType
from typing import (
    Any,
    DefaultDict,
    Dict,
    FrozenSet,
    List,
    Literal,
    NamedTuple,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)
import typing

import pytest


@pytest.mark.parametrize(
    "T, GT",
    [
        (frozenset, FrozenSet),
        (list, List),
        (set, Set),
        (tuple, Tuple),
        (type, Type),
        (Counter, typing.Counter),
    ],
)
def test_builtin_generics_single(T, GT):
    """하나의 파라미터를 받는 제네릭 타입들에 대한 typing 호환성 테스트."""
    assert get_origin(GT[int]) is T
    assert get_origin(GT) is T
    assert get_args(GT[int]) == (int,)
    assert get_args(GT) == ()

    assert get_origin(T[int]) is T
    assert get_origin(T) is None
    assert get_args(T[int]) == (int,)
    assert get_args(T) == ()


@pytest.mark.parametrize(
    "T, GT",
    [
        (defaultdict, DefaultDict),
        (dict, Dict),
        (OrderedDict, typing.OrderedDict),
        (tuple, Tuple),
    ],
)
def test_builtin_generics_double(T, GT):
    """두개의 파라미터를 받는 제네릭 타입들에 대한 typing 호환성 테스트."""
    assert get_origin(GT[str, int]) is T
    assert get_origin(GT) is T
    assert get_args(GT[str, int]) == (str, int)
    assert get_args(GT) == ()

    assert get_origin(T[str, int]) is T
    assert get_origin(T) is None
    assert get_args(T[str, int]) == (str, int)
    assert get_args(T) == ()


@pytest.mark.parametrize(
    "T",
    [
        Any,
        Literal,
    ],
)
def test_special(T):
    assert get_origin(T) is None
    assert get_args(T) == ()


@pytest.mark.parametrize(
    "T",
    [
        bool,
        bytearray,
        bytes,
        complex,
        dict,
        float,
        frozenset,
        int,
        list,
        set,
        str,
        tuple,
        Counter,
        defaultdict,
        namedtuple,
        OrderedDict,
        NoneType,
        Any,
        typing.Counter,
        Dict,
        DefaultDict,
        FrozenSet,
        List,
        NamedTuple,
        typing.OrderedDict,
        Set,
        Tuple,
    ],
)
def test_valid_type_parameters(T):
    """Type[] 이나 type[] 에 사용할 수 있는 타입들에 대한 호환성 테스트."""
    assert get_origin(Type[T]) is type
    assert get_origin(type[T]) is type
    assert get_args(Type[T]) == (T,)
    assert get_args(type[T]) == (T,)


@pytest.mark.parametrize(
    "T",
    [
        Literal,
    ],
)
def test_partially_valid_type_parameters(T):
    """type[] 에는 사용할 수 있으나 Type[] 에서는 사용할 수 없는 타입들에 대한 호환성 테스트."""
    assert get_origin(type[T]) is type
    assert get_args(type[T]) == (T,)
    with pytest.raises(TypeError):
        get_origin(Type[T])


@pytest.mark.parametrize(
    "T, CT",
    [
        (None, NoneType),
    ],
)
def test_partially_converted_type_parameters(T, CT):
    """Type[] 을 사용할 때는 자동 변환되지만, type[] 을 사용할 때는 그렇지 않은 타입들에 대한 호환성 테스트."""
    assert get_origin(Type[T]) is type
    assert get_origin(type[T]) is type
    assert get_args(Type[T]) == (CT,)
    assert get_args(type[T]) == (T,)


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_tuple(T):
    assert get_origin(T[int]) is tuple
    assert get_origin(T[int, str]) is tuple
    assert get_origin(T[int, ...]) is tuple
    assert get_origin(T[()]) is tuple

    assert get_args(T[int]) == (int,)
    assert get_args(T[int, str]) == (int, str)
    assert get_args(T[int, ...]) == (int, ...)
    assert get_args(T) == ()


def test_empty_tuple_args():
    assert get_args(tuple[()]) == ()

    if sys.version_info < (3, 11):
        assert get_args(Tuple[()]) == ((),)
    else:
        assert get_args(Tuple[()]) == ()


def test_Union():
    assert get_origin(type[Union]) is type
    assert get_args(type[Union]) == (Union,)

    assert get_origin(Union[str, None]) is Union
    assert get_args(Union[str, None]) == (str, NoneType)

    assert get_origin(str | None) is UnionType
    assert get_args(str | None) == (str, NoneType)

    assert type(str | int) is UnionType

    if sys.version_info < (3, 14):
        with pytest.raises(TypeError):
            Type[Union]
        assert Union is not UnionType
        assert type(Union[str, int]) is not UnionType
    else:
        assert get_origin(Type[Union]) is type
        assert get_args(Type[Union]) == (Union,)
        assert Union is UnionType
        assert type(Union[str, int]) is UnionType
