from typing import Type, get_args, get_origin

import pytest


@pytest.mark.parametrize(
    "T, GT",
    [
        (type, Type),
    ],
)
def test_builtin_generics(T, GT):
    """빌트인 제네릭 타입들에 대한 typing 호환성 테스트."""
    assert get_origin(GT[int]) is T
    assert get_origin(GT) is T
    assert get_args(GT[int]) == (int,)
    assert get_args(GT) == ()

    assert get_origin(T[int]) is T
    assert get_origin(T) is None
    assert get_args(T[int]) == (int,)
    assert get_args(T) == ()
