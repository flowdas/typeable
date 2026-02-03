from collections import (
    ChainMap,
    Counter,
    OrderedDict,
    UserDict,
    UserList,
    defaultdict,
    deque,
    namedtuple,
)
from dataclasses import dataclass
from typing import DefaultDict, Dict, NamedTuple, get_origin
import typing

import pytest

from typeable import deepcast, localcontext


@pytest.fixture(
    params=[
        dict,
        dict[str, int],
        Dict,
        Dict[str, int],
        Counter,
        Counter[str],
        typing.Counter,
        typing.Counter[str],
        OrderedDict,
        OrderedDict[str, int],
        typing.OrderedDict,
        typing.OrderedDict[str, int],
        defaultdict,
        defaultdict[str, int],
        DefaultDict,
        DefaultDict[str, int],
    ]
)
def RT(request):
    return request.param


@pytest.mark.parametrize("T", [dict, Dict])
def test_subclass(T):
    """서브클래스는 일치할 때 그대로 반환되어야 한다."""
    d = {"a": 1, "b": 2}
    od = OrderedDict(d)
    assert isinstance(od, dict)
    r = deepcast(T, od)
    assert r is od


@pytest.mark.parametrize("T", [dict, Dict])
def test_None(T):
    """None 은 dict 로 변환될 수 없다."""
    with pytest.raises(TypeError):
        deepcast(T, None)


@pytest.mark.parametrize("T", [dict, Dict])
def test_nested(T):
    """dataclass 를 값으로 품은 dict[] 변환."""

    @dataclass
    class X:
        i: int

    data = {i: {"i": i} for i in range(10)}

    # dict
    r = deepcast(T, data)
    assert isinstance(r, dict)
    assert r == data

    # generic dict
    r = deepcast(T[str, X], data)

    assert isinstance(r, dict)
    assert len(r) == len(data)
    for i, (k, v) in enumerate(r.items()):
        assert k == str(i)
        assert isinstance(v, X)
        assert v.i == i


@pytest.mark.parametrize("T", [dict, Dict])
def test_no_copy(T):
    """isinstance 이면 복사가 일어나지 말아야 한다."""
    data = {str(i): i for i in range(10)}
    assert deepcast(T, data) is data
    assert deepcast(T[str, int], data) is data


@pytest.mark.parametrize("T", [dict, Dict])
def test_copy(T):
    """형이 정확히 일치하지 않으면 복사가 일어나야 한다."""
    data = {str(i): i for i in range(10)}

    expected = data.copy()
    data["9"] = "9"  # type: ignore

    assert deepcast(T[str, int], data) is not data
    assert deepcast(T[str, int], data) == expected
    data2 = UserDict(data)
    assert deepcast(T[str, int], data2) is not data2
    assert deepcast(T[str, int], data2) == expected
    assert isinstance(deepcast(T[str, int], data2), T)
    assert not isinstance(deepcast(T[str, int], data2), UserDict)


@pytest.mark.parametrize(
    "VT",
    [
        # dict
        dict,
        Counter,
        OrderedDict,
        defaultdict,
        # Mapping
        ChainMap,
        UserDict,
    ],
)
def test_dict_from_Mapping(RT, VT):
    """여러 dict 형들로의 다양한 변환을 지원해야 한다."""
    data = {str(i): i for i in range(10)}
    v = VT(None, data) if VT is defaultdict else VT(data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    if isinstance(v, T):
        assert x is v
    else:
        assert isinstance(x, T)
    assert x == v
    assert v == x


@pytest.mark.parametrize(
    "VT",
    [
        deque,
        frozenset,
        list,
        set,
        tuple,
        UserList,
    ],
)
def test_dict_from_Iterable(RT, VT):
    """(키,값) 쌍의 이터러블은 dict 로 변환된다."""
    data = {"a": 1, "b": 2}
    v = VT(data.items())
    empty_v = VT([])
    with localcontext() as ctx:
        for C in (True, False):
            ctx.dict_from_empty_iterable = C
            x = deepcast(RT, v)
            T = get_origin(RT) or RT
            assert isinstance(x, T)
            assert x == data
            assert data == x

            if C:
                assert deepcast(RT, empty_v) == {}
            else:
                with pytest.raises(TypeError):
                    deepcast(RT, empty_v)


def test_dict_from_NamedTuple(RT):
    """NamedTuple 도 dict 로 변환된다."""
    data = {"a": 1, "b": 2}

    class X(NamedTuple):
        a: int
        b: int

    v = X(**data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    assert isinstance(x, T)
    assert x == data
    assert data == x


def test_dict_from_namedtuple(RT):
    """namedtuple 도 dict 로 변환된다."""
    data = {"a": 1, "b": 2}

    X = namedtuple("X", ["a", "b"])
    v = X(**data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    assert isinstance(x, T)
    assert x == data
    assert data == x


@pytest.mark.parametrize(
    "v",
    [
        "",
        b"",
        bytearray(),
    ],
)
def test_dict_from_string(RT, v):
    """str, bytes, bytearray 는 dict 로 변환할 수 없다."""
    with localcontext(dict_from_empty_iterable=True):
        with pytest.raises(TypeError):
            deepcast(RT, v)
