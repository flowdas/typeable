import asyncio
from collections import namedtuple
from dataclasses import dataclass, field
from typing import ForwardRef, List, NamedTuple, Type

from typeable import capture, deepcast, localcontext

import pytest
from .conftest import str_from_int

#
# deepcast.register
#


@pytest.mark.parametrize(
    "T",
    [
        Type[bool],
        type[bool],
        type[int],
    ],
)
def test_supported_cls_types(deepcast, T):
    """두번째 인자의 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(deepcast, cls: T, val: object): ...  # type: ignore


@pytest.mark.parametrize(
    "T",
    [
        bool,  # type[bool] 을 써야 한다
    ],
)
def test_unsupported_cls_types(deepcast, T):
    """두번째 인자의 타입으로 등록할 수 없음을 확인한다."""

    with pytest.raises(TypeError):

        @deepcast.register
        def _(deepcast, cls: T, val: object): ...  # type: ignore


@pytest.mark.parametrize(
    "RT",
    [
        bool,
        int,
    ],
)
def test_supported_return_types(deepcast, RT):
    """반환 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(deepcast, cls, val: object) -> RT: ...  # type: ignore


@pytest.mark.parametrize(
    "VT",
    [
        bool,
        int,
    ],
)
def test_supported_value_types(deepcast, VT):
    """세번째 인자의 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(deepcast, cls: type[object], val: VT): ...  # type: ignore


def test_register_collison(deepcast):
    """같은 서명으로 취급되는 두 변환기를 등록하면 RuntimeError 가 발생해야 한다."""

    @deepcast.register
    def _(deepcast, cls: type[float], val: object): ...

    with pytest.raises(RuntimeError):

        @deepcast.register
        def _(deepcast, cls, val: object) -> float: ...


def test_register_without_args(deepcast):
    """인자가 부족한 변환기를 등록하면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(deepcast): ...


def test_register_without_annotations(deepcast):
    """형 어노테이션을 제공하지 않으면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(deepcast, cls, val): ...


def test_register_mismatch(deepcast):
    """두번째 인자의 형과 반환 형이 호환되지 않으면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(deepcast, cls: type[float], val: int) -> int: ...


def test_exact_match(deepcast):
    """변환기 서명과 정확히 일치하는 형 변환이 수행됨을 확인한다."""

    class X:
        pass

    @deepcast.register
    def _(deepcast, cls: type[int], val: X) -> int:
        return 123

    assert deepcast(int, X()) == 123


#
# deepcast.apply
#


def test_apply_class():
    """클래스에 dict 를 apply 하면 인스턴스를 반환한다."""

    class X:
        def __init__(self, i: int):
            self.i = i

    data = {"i": 3}
    x = deepcast.apply(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]


def test_apply_dataclass():
    """alaias 가 포함된 dataclass에 dict 를 apply 하면 인스턴스를 반환한다."""

    @dataclass
    class X:
        i: int = deepcast.field(alias="$i")

    data = {"$i": 3}
    x = deepcast.apply(X, data)
    assert isinstance(x, X)
    assert x.i == data["$i"]

    @dataclass
    class Y:
        i: int = field(metadata={"alias": "$i"})

    y = deepcast.apply(Y, data)
    assert isinstance(y, Y)
    assert y.i == data["$i"]


def test_apply_namedtuple():
    """namedtuple 에 dict 를 apply 하면 인스턴스를 반환한다."""

    X = namedtuple("X", ["i", "j"], defaults=[9])

    data = {"i": 3}
    x = deepcast.apply(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 9

    data["j"] = 7
    x = deepcast.apply(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 7


def test_apply_NamedTuple():
    """NamedTuple 에 dict 를 apply 하면 인스턴스를 반환한다."""

    class X(NamedTuple):
        i: int
        j: int = 9

    data = {"i": 3}
    x = deepcast.apply(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
    assert x.j == 9

    data["j"] = "7"  # type: ignore
    with localcontext(parse_number=True):
        x = deepcast.apply(X, data)
        assert isinstance(x, X)
        assert x.i == data["i"]
        assert x.j == 7


def test_apply_function():
    """함수에 dict 를 apply 하면 언패킹해서 호출한다."""

    def f(i: int) -> int:
        return i

    data = {"i": 3}
    x = deepcast.apply(f, data)
    assert x == data["i"]


def test_apply_function_validation():
    """함수 인자형으로 형변환을 시도한다."""

    def test(a: int):
        assert isinstance(a, int)
        return a

    assert deepcast.apply(test, dict(a=123)) == 123
    assert deepcast.apply(test, dict(a="123")) == 123
    with pytest.raises(TypeError):
        deepcast.apply(test, dict(a=None))


def test_apply_kwargs():
    """**kwargs 의 어노테이션도 처리된다."""

    def test(**kwargs: int):
        for k, v in kwargs.items():
            assert isinstance(v, int)
        return kwargs

    with localcontext(parse_number=True):
        assert deepcast.apply(test, dict(a=1, b="2", c=3)) == {
            "a": 1,
            "b": 2,
            "c": 3,
        }


def test_apply_validate_default():
    """잘못된 인자 기본값에 대한 처리를 확인한다."""

    def f(i: str = 1) -> str:  # type: ignore
        return i

    with localcontext() as ctx:
        ctx.validate_default = False
        assert deepcast.apply(f, {}) == 1

        ctx.validate_default = True
        with pytest.raises(TypeError):
            with capture() as error:
                deepcast.apply(f, {})
        assert error.location == ("i",)


def test_apply_validate_return():
    def test(a: int) -> str:  # type: ignore
        assert isinstance(a, int)
        return a  # type: ignore

    assert deepcast.apply(test, dict(a=123)) == 123
    assert deepcast.apply(test, dict(a="123")) == 123

    def test(a: int):  # type: ignore
        assert isinstance(a, int)
        return a

    assert deepcast.apply(test, dict(a=123), validate_return=True) == 123
    assert deepcast.apply(test, dict(a="123"), validate_return=True) == 123

    def test(a: int) -> str:
        assert isinstance(a, int)
        return a  # type: ignore

    with deepcast.localregister(str_from_int):
        assert deepcast.apply(test, dict(a=123), validate_return=True) == "123"
        assert deepcast.apply(test, dict(a="123"), validate_return=True) == "123"


def test_apply_capture():
    def test(a: int) -> str:
        return None  # type: ignore

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast.apply(test, dict(a=None))
    assert error.location == ("a",)

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast.apply(test, dict(a=123), validate_return=True)
    assert error.location == ("return",)


def test_apply_method():
    class X:
        def test1(self, a: int):
            assert isinstance(self, X)
            assert isinstance(a, int)
            return a

        @classmethod
        def test2(cls, a: int):
            assert cls is X
            assert isinstance(a, int)
            return a

        @staticmethod
        def test3(a: int):
            assert isinstance(a, int)
            return a

    x = X()

    assert deepcast.apply(x.test1, dict(a=123)) == 123
    assert deepcast.apply(x.test1, dict(a="123")) == 123

    assert deepcast.apply(x.test2, dict(a=123)) == 123
    assert deepcast.apply(x.test2, dict(a="123")) == 123

    assert deepcast.apply(X.test2, dict(a=123)) == 123
    assert deepcast.apply(X.test2, dict(a="123")) == 123

    assert deepcast.apply(x.test3, dict(a=123)) == 123
    assert deepcast.apply(x.test3, dict(a="123")) == 123

    assert deepcast.apply(X.test3, dict(a=123)) == 123
    assert deepcast.apply(X.test3, dict(a="123")) == 123


def test_apply_async():
    async def test(a: int):
        assert isinstance(a, int)
        return a

    assert asyncio.iscoroutinefunction(test)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    assert loop.run_until_complete(deepcast.apply(test, dict(a=123))) == 123
    assert loop.run_until_complete(deepcast.apply(test, dict(a="123"))) == 123


def my_func(i: List["MyClass"], j: list[ForwardRef("MyClass")]):  # type: ignore
    return i, j


@dataclass
class MyClass:
    i: List["MyClass"]
    j: list[ForwardRef("MyClass")]  # type: ignore


def test_apply_ForwardRef_in_func():
    v = MyClass(i=[], j=[])
    assert deepcast.apply(my_func, {"i": [v], "j": [v]}) == ([v], [v])


def test_apply_ForwardRef_in_class():
    v = MyClass(i=[], j=[])
    v.i.append(v)
    v.j.append(v)
    assert deepcast.apply(MyClass, {"i": [v], "j": [v]}) == v
