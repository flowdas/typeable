from collections import UserList, deque, namedtuple
from dataclasses import dataclass
from typing import NamedTuple, Tuple, get_origin

import pytest

from typeable import localcontext, typecast

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
        typecast(T, None)


def test_Iterable(RT, VT):
    """여러 iterable 을 tuple 로 변환할 수 있어야 한다."""
    data = range(10)
    v = VT(data)
    x = typecast(RT, v)
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
    l = typecast(T, data)
    assert l is data

    # generic
    l = typecast(T[X, ...], data)
    assert isinstance(l, tuple)
    for i in range(len(data)):
        assert isinstance(l[i], X)
        assert l[i].i == i


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_no_copy(T):
    """isinstance 이면 복사가 일어나지 말아야 한다."""
    data = tuple(range(10))
    assert typecast(T, data) is data
    assert typecast(T[int, ...], data) is data


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_copy(T):
    """형이 정확히 일치하지 않으면 복사가 일어나야 한다."""
    data = list(range(9))
    data.append("9")  # type: ignore
    data = tuple(data)
    expected = tuple(range(10))

    with localcontext(parse_number=True):
        assert typecast(T, data) is data
        assert typecast(T[int, ...], data) == expected
        assert typecast(T[int, ...], list(data)) == expected


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
        typecast(RT, v)


def test_hetero_tuple():
    # heterogeneous tuple
    data = (1, "2", "3")
    expected = ("1", 2, "3")

    l = typecast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = typecast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # heterogeneous generic tuple
    with typecast.localregister(str_from_int):
        l = typecast(Tuple[str, int, str], data)

        assert isinstance(l, tuple)
        assert l == expected

        l = typecast(Tuple[str, int, str], list(data))

        assert isinstance(l, tuple)
        assert l == expected

    assert typecast(Tuple[int, int, int], data) == (1, 2, 3)
    assert typecast(Tuple[int, int, int], list(data)) == (1, 2, 3)

    with typecast.localregister(str_from_int):
        l = typecast(tuple[str, int, str], data)

        assert isinstance(l, tuple)
        assert l == expected


def test_empty_tuple():
    # empty tuple
    data = ()

    l = typecast(Tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    l = typecast(tuple, data)
    assert isinstance(l, tuple)
    assert l == data

    # empty generic tuple
    l = typecast(Tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data

    l = typecast(tuple[()], data)

    assert isinstance(l, tuple)
    assert l == data


@pytest.mark.parametrize("T", [tuple, Tuple])
def test_length_mismatch(T):
    # length mismatch
    with pytest.raises(TypeError):
        typecast(T[()], (1,))

    with pytest.raises(TypeError):
        typecast(T[int], (1, 2))

    with pytest.raises(TypeError):
        typecast(T[int], [1, 2])

    with pytest.raises(TypeError):
        typecast(T[int], ())

    with pytest.raises(TypeError):
        typecast(T[int], [])


def test_complex(RT):
    """complex 는 tuple 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        typecast(RT, complex(1, 2))


def test_namedtuple_from_Iterable(VT):
    """Iterable 을 namedtuple 로 변환할 수 있다."""

    X = namedtuple("X", ["i", "j"], defaults=[9])

    data = [3]
    v = VT(data)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == data[0]
    assert x.j == 9

    data.append(7)
    v = VT(data)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == data[0]
    assert x.j == 7


def test_namedtuple_from_dict():
    """dict 를 namedtuple 로 변환할 수 있다."""

    X = namedtuple("X", ["i", "j"], defaults=[9])

    data = {"i": 3}
    x = typecast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 9

    data["j"] = 7
    x = typecast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 7


def test_namedtuple_from_dataclass():
    """dataclass 를 namedtuple 로 변환할 수 있다."""

    X = namedtuple("X", ["i", "j"], defaults=[9])

    @dataclass
    class V:
        i: int

    v = V(i=3)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == v.i
    assert x.j == 9

    @dataclass
    class VV:
        i: int
        j: int

    v = VV(i=3, j=7)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == v.i
    assert x.j == v.j


def test_NamedTuple_from_Iterable(VT):
    """Iterable 을 NamedTuple 로 변환할 수 있다."""

    class X(NamedTuple):
        i: int
        j: int = 9

    data = [3]
    v = VT(data)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == data[0]
    assert x.j == 9

    data.append(7)
    v = VT(data)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == data[0]
    assert x.j == 7


def test_NamedTuple_from_dict():
    """dict 를 NamedTuple 로 변환할 수 있다."""

    class X(NamedTuple):
        i: int
        j: int = 9

    data = {"i": 3}
    x = typecast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 9

    data["j"] = "7"  # type: ignore
    with localcontext(parse_number=True):
        x = typecast(X, data)
        assert isinstance(x, X)
        assert x.i == data["i"]
        assert x.j == 7


def test_NamedTuple_from_dataclass():
    """dataclass 를 NamedTuple 로 변환할 수 있다."""

    class X(NamedTuple):
        i: int
        j: int = 9

    @dataclass
    class V:
        i: int

    v = V(i=3)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == v.i
    assert x.j == 9

    @dataclass
    class VV:
        i: int
        j: int

    v = VV(i=3, j=7)
    x = typecast(X, v)
    assert isinstance(x, X)
    assert x.i == v.i
    assert x.j == v.j
