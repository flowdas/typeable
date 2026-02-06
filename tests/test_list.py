from collections import UserList, deque
from dataclasses import dataclass
from typing import List, get_origin

from typeable import deepcast, localcontext

import pytest


@pytest.fixture(
    params=[
        list,
        list[int],
        List,
        List[int],
    ]
)
def RT(request):
    return request.param


@pytest.fixture(
    params=[
        deque,
        frozenset,
        list,
        set,
        tuple,
        UserList,
    ]
)
def VT(request):
    return request.param


@pytest.mark.parametrize("T", [list, List])
def test_None(T):
    """None 은 list 로 변환될 수 없다."""
    with pytest.raises(TypeError):
        deepcast(T, None)


def test_Iterable(RT, VT):
    """여러 iterable 을 list 로 변환할 수 있어야 한다."""
    data = range(10)
    v = VT(data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    if isinstance(v, T):
        assert x is v
    else:
        assert isinstance(x, T)
    assert x == list(v)
    assert list(v) == x


@pytest.mark.parametrize("T", [list, List])
def test_nested(T):
    """dataclass 를 값으로 품은 list[] 변환."""

    @dataclass
    class X:
        i: int

    data = [{"i": i} for i in range(10)]

    # non-generic
    l = deepcast(T, data)
    assert l is data

    # generic
    l = deepcast(T[X], data)
    assert isinstance(l, list)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i


@pytest.mark.parametrize("T", [list, List])
def test_no_copy(T):
    """isinstance 이면 복사가 일어나지 말아야 한다."""
    data = list(range(10))
    assert deepcast(T, data) is data
    assert deepcast(T[int], data) is data


@pytest.mark.parametrize("T", [list, List])
def test_copy(T):
    """형이 정확히 일치하지 않으면 복사가 일어나야 한다."""
    data = list(range(9))
    data.append("9")  # type: ignore
    expected = list(range(10))

    with localcontext(parse_number=True):
        assert deepcast(T, data) is data
        assert deepcast(T[int], data) == expected
        assert deepcast(T[int], tuple(data)) == expected


@pytest.mark.parametrize(
    "v",
    [
        "",
        b"",
        bytearray(),
    ],
)
def test_string(RT, v):
    """str, bytes, bytearray 는 list 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        deepcast(RT, v)
