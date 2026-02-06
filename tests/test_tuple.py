from collections import UserList, deque
from dataclasses import dataclass
from typing import Tuple, get_origin
from typeable import deepcast

import pytest

from typeable._context import localcontext
from .conftest import str_from_int


@pytest.fixture(
    params=[
        tuple,
        tuple[int, ...],
        Tuple,
        Tuple[int, ...],
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


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_None(T):
    """None 은 tuple 로 변환될 수 없다."""
    with pytest.raises(TypeError):
        deepcast(T, None)


def test_Iterable(RT, VT):
    """여러 iterable 을 tuple 로 변환할 수 있어야 한다."""
    data = range(10)
    v = VT(data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    if isinstance(v, T):
        assert x is v
    else:
        assert isinstance(x, T)
    assert x == tuple(v)
    assert tuple(v) == x


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_nested(T):
    """dataclass 를 값으로 품은 tuple[] 변환."""

    @dataclass
    class X:
        i: int

    data = tuple({"i": i} for i in range(10))

    # non-generic
    l = deepcast(T, data)
    assert l is data

    # generic
    l = deepcast(T[X, ...], data)
    assert isinstance(l, tuple)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_no_copy(T):
    """isinstance 이면 복사가 일어나지 말아야 한다."""
    data = tuple(range(10))
    assert deepcast(T, data) is data
    assert deepcast(T[int, ...], data) is data


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_copy(T):
    """형이 정확히 일치하지 않으면 복사가 일어나야 한다."""
    data = list(range(9))
    data.append("9")  # type: ignore
    data = tuple(data)
    expected = tuple(range(10))

    with localcontext(parse_number=True):
        assert deepcast(T, data) is data
        assert deepcast(T[int, ...], data) == expected
        assert deepcast(T[int, ...], list(data)) == expected


@pytest.mark.parametrize(
    "v",
    [
        "",
        b"",
        bytearray(),
    ],
)
def test_string(RT, v):
    """str, bytes, bytearray 는 tuple 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        deepcast(RT, v)


def test_hetero_tuple():
    # heterogeneous tuple
    data = (1, "2", "3")
    expected = ("1", 2, "3")

    l = deepcast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # heterogeneous generic tuple
    with deepcast.localregister(str_from_int):
        l = deepcast(Tuple[str, int, str], data)

        assert isinstance(l, tuple)
        assert l == expected

        l = deepcast(Tuple[str, int, str], list(data))

        assert isinstance(l, tuple)
        assert l == expected

    assert deepcast(Tuple[int, int, int], data) == (1, 2, 3)
    assert deepcast(Tuple[int, int, int], list(data)) == (1, 2, 3)

    with deepcast.localregister(str_from_int):
        l = deepcast(tuple[str, int, str], data)

        assert isinstance(l, tuple)
        assert l == expected


def test_empty_tuple():
    # empty tuple
    data = ()

    l = deepcast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # empty generic tuple
    l = deepcast(Tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data

    l = deepcast(tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_length_mismatch(T):
    # length mismatch
    with pytest.raises(TypeError):
        deepcast(T[()], (1,))

    with pytest.raises(TypeError):
        deepcast(T[int], (1, 2))

    with pytest.raises(TypeError):
        deepcast(T[int], [1, 2])

    with pytest.raises(TypeError):
        deepcast(T[int], ())

    with pytest.raises(TypeError):
        deepcast(T[int], [])


def test_complex(RT):
    """complex 는 tuple 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        deepcast(RT, complex(1, 2))
