from collections import Counter, OrderedDict, defaultdict
from types import NoneType
from typing import DefaultDict, Dict, Type, get_args, get_origin
import typing

import pytest


@pytest.mark.parametrize(
    "T, GT",
    [
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
        NoneType,
        dict,
        Dict,
        Counter,
        typing.Counter,
        OrderedDict,
        typing.OrderedDict,
        defaultdict,
        DefaultDict,
    ],
)
def test_valid_type_parameters(T):
    """Type[] 이나 type[] 에 사용할 수 있는 타입들에 대한 호환성 테스트."""
    assert get_origin(Type[T]) is type
    assert get_origin(type[T]) is type
    assert get_args(Type[T]) == (T,)
    assert get_args(type[T]) == (T,)


@pytest.mark.parametrize(
    "T, CT",
    [
        (None, NoneType),
    ],
)
def test_partially_valid_type_parameters(T, CT):
    """Type[] 을 사용할 때는 자동 변환되지만, type[] 을 사용할 때는 그렇지 않은 타입들에 대한 호환성 테스트."""
    assert get_origin(Type[T]) is type
    assert get_origin(type[T]) is type
    assert get_args(Type[T]) == (CT,)
    assert get_args(type[T]) == (T,)
