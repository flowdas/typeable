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
from typing import DefaultDict, Dict, NamedTuple, TypedDict, get_origin
import typing

from typeable import deepcast

import pytest
from .conftest import str_from_int


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


@pytest.fixture(
    params=[
        # dict
        dict,
        Counter,
        OrderedDict,
        defaultdict,
        # Mapping
        ChainMap,
        UserDict,
    ]
)
def VTMapping(request):
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
def VTIterable(request):
    return request.param


@pytest.fixture(
    params=[
        ({"a": 1, "b": 2}, None),
        ({"a": 1}, None),  # b 는 없어도 좋다.
        ({"a": 1, "b": 2, "c": 3}, TypeError),  # c 가 더있다.
        ({"b": 2}, TypeError),  # a 가 없다.
    ]
)
def DSTypedDict(request):
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
    with deepcast.localregister(str_from_int):
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


def test_dict_from_Mapping(RT, VTMapping):
    """여러 dict 형들로의 다양한 변환을 지원해야 한다."""
    data = {str(i): i for i in range(10)}
    v = VTMapping(None, data) if VTMapping is defaultdict else VTMapping(data)
    x = deepcast(RT, v)
    T = get_origin(RT) or RT
    if isinstance(v, T):
        assert x is v
    else:
        assert isinstance(x, T)
    assert x == v
    assert v == x


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
    with pytest.raises(TypeError):
        deepcast(RT, v)


def test_TypedDict_from_Mapping(VTMapping, DSTypedDict):
    """여러 dict 형들로부터 TypedDict 로의 변환을 지원해야 한다."""

    # 3.10 호환성 때문에 Required, NotRequired 를 사용하지 않는다.
    class Base(TypedDict):
        a: int

    class X(Base, total=False):
        b: int

    assert X.__required_keys__ == frozenset(["a"])
    assert X.__optional_keys__ == frozenset(["b"])

    data, Exc = DSTypedDict
    v = VTMapping(None, data) if VTMapping is defaultdict else VTMapping(data)
    if Exc is None:
        x = deepcast(X, v)
        if isinstance(v, dict):
            assert x is v
        else:
            assert isinstance(x, dict)
        assert x == v
        assert v == x
    else:
        with pytest.raises(Exc):
            deepcast(X, v)
