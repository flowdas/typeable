from collections import UserList, deque
from dataclasses import dataclass
from typing import FrozenSet, Set, get_origin

import pytest

from typeable import localcontext, typecast


@pytest.fixture(
    params=[
        frozenset,
        frozenset[int],
        FrozenSet,
        FrozenSet[int],
        set,
        set[int],
        Set,
        Set[int],
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


@pytest.mark.parametrize("T", [frozenset, FrozenSet, set, Set])
def test_None(T):
    """None 은 set 으로 변환될 수 없다."""
    with pytest.raises(TypeError):
        typecast(T, None)


def test_Iterable(RT, VT):
    """여러 iterable 을 set 으로 변환할 수 있어야 한다."""
    data = range(10)
    v = VT(data)
    x = typecast(RT, v)
    T = get_origin(RT) or RT
    if isinstance(v, T):
        assert x is v
    else:
        assert isinstance(x, T)
    assert x == set(v)
    assert set(v) == x


@pytest.mark.parametrize("T", [frozenset, FrozenSet, set, Set])
def test_nested(T):
    """dataclass 를 값으로 품은 set[] 변환."""

    @dataclass(frozen=True)
    class X:
        i: int

    OT = get_origin(T) or T

    # non-generic
    data = OT(X(i=i) for i in range(10))

    l = typecast(T, data)
    assert l is data

    # generic
    data = [{"i": i} for i in range(10)]

    l = typecast(T[X], data)
    assert isinstance(l, OT)
    for v in l:
        assert isinstance(v, X)
    for i in range(len(data)):
        assert X(i=i) in l


@pytest.mark.parametrize("T", [frozenset, FrozenSet, set, Set])
def test_no_copy(T):
    """isinstance 이면 복사가 일어나지 말아야 한다."""
    OT = get_origin(T) or T
    data = OT(range(10))
    assert typecast(T, data) is data
    assert typecast(T[int], data) is data


@pytest.mark.parametrize("T", [frozenset, FrozenSet, set, Set])
def test_copy(T):
    """형이 정확히 일치하지 않으면 복사가 일어나야 한다."""
    OT = get_origin(T) or T
    data = set(range(9))
    data.add("9")  # type: ignore
    data = OT(data)
    expected = OT(range(10))

    with localcontext(parse_number=True):
        assert typecast(T, data) is data
        assert typecast(T[int], data) == expected
        assert typecast(T[int], list(data)) == expected


@pytest.mark.parametrize(
    "v",
    [
        "",
        b"",
        bytearray(),
    ],
)
def test_string(RT, v):
    """str, bytes, bytearray 는 set 으로 변환할 수 없다."""
    with pytest.raises(TypeError):
        typecast(RT, v)
