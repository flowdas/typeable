import asyncio
from dataclasses import dataclass
import inspect
import sys
from typing import (
    Annotated,
    Any,
    Dict,
    FrozenSet,
    List,
    Literal,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

import pytest

from typeable import Context, capture, declare, deepcast


def test_get_origin():
    assert get_origin(Type[int]) == type
    assert get_origin(Type) == type
    assert get_origin(List[int]) == list
    assert get_origin(List) == list
    assert get_origin(Dict[str, str]) == dict
    assert get_origin(Dict) == dict
    assert get_origin(Set[int]) == set
    assert get_origin(Set) == set
    assert get_origin(FrozenSet[int]) == frozenset
    assert get_origin(FrozenSet) == frozenset
    assert get_origin(Tuple[int]) == tuple
    assert get_origin(Tuple[int, str]) == tuple
    assert get_origin(Tuple[int, ...]) == tuple
    assert get_origin(Tuple[()]) == tuple
    assert get_origin(Tuple) == tuple
    assert get_origin(Union[int, None]) == Union
    assert get_origin(Any) is None
    assert get_origin(Literal) is None
    assert get_origin(Annotated) is None
    assert get_origin(Annotated[int, lambda: True]) is Annotated


def test_get_args():
    @dataclass
    class X:
        i: int

    assert get_args(Type[int]) == (int,)
    assert get_args(Type) == ()
    assert get_args(List[int]) == (int,)
    assert get_args(List[X]) == (X,)
    assert get_args(List) == ()
    assert get_args(Dict[str, X]) == (str, X)
    assert get_args(Dict) == ()
    assert get_args(Set[int]) == (int,)
    assert get_args(Set) == ()
    assert get_args(FrozenSet[int]) == (int,)
    assert get_args(FrozenSet) == ()
    assert get_args(Tuple[int]) == (int,)
    assert get_args(Tuple[int, str]) == (int, str)
    assert get_args(Tuple[int, ...]) == (int, ...)
    if sys.version_info < (3, 11):
        assert get_args(Tuple[()]) == ((),)
    else:
        assert get_args(Tuple[()]) == ()
    assert get_args(Tuple) == ()
    assert get_args(Union[int, None]) == (int, type(None))
    assert get_args(Any) == ()
    assert get_args(Literal) == ()
    assert get_args(Literal["2.0"]) == ("2.0",)
    assert get_args(Annotated) == ()
    assert get_args(Annotated[int, True, False]) == (int, True, False)


Integer = int


def test_declare():
    with declare("Integer") as Ref:
        T = List[Ref]

    assert deepcast(T, [2]) == [2]
    assert deepcast(T, ["2"]) == [2]


def test_register():
    with pytest.raises(RuntimeError):
        # _cast_float_object 와 충돌
        @deepcast.register
        def _(cls, val) -> float:
            return cls(val)


def test_invalid_register():
    @dataclass
    class X:
        i: int

    with pytest.raises(TypeError):

        @deepcast.register
        def _():
            pass

    with pytest.raises(TypeError):

        @deepcast.register
        def _(cls, val):
            pass

    with pytest.raises(TypeError):

        @deepcast.register
        def _(cls: X, val) -> X:
            pass


@pytest.mark.skip(reason="Object 제거로 인해 다른 구현이 필요")
def test_double_dispatch():
    class X:
        pass

    @dataclass
    class Y:
        pass

    @deepcast.register
    def _(cls, val: X) -> Object:
        return 1

    assert deepcast(Y, X()) == 1
    assert isinstance(deepcast(Y, {}), Y)

    with pytest.raises(RuntimeError):

        @deepcast.register
        def _(cls, val: X) -> Object:
            return 1


def test_function():
    @deepcast.function
    def test(a: int):
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123
    with pytest.raises(TypeError):
        test(None)


def test_function_with_ctx():
    @deepcast.function
    def test(a: int, *, ctx: Context = None):
        assert isinstance(a, int)
        assert ctx is not None
        return a

    assert test(123) == 123
    assert test("123") == 123
    with pytest.raises(TypeError):
        test(None)


def test_function_ctx_conflict():
    with pytest.raises(TypeError):

        @deepcast.function
        def test(ctx: int):
            pass

    with pytest.raises(TypeError):

        @deepcast.function
        def test(ctx):
            pass


def test_function_args():
    @deepcast.function
    def test(*args: int):
        for a in args:
            assert isinstance(a, int)
        return args

    assert test(1, "2", 3.14) == (1, 2, 3)


def test_function_kwargs():
    @deepcast.function
    def test(**kwargs: int):
        for k, v in kwargs.items():
            assert isinstance(v, int)
        return kwargs

    assert test(a=1, b="2", c=3.14) == {"a": 1, "b": 2, "c": 3}


def test_function_cast_return():
    @deepcast.function
    def test(a: int) -> str:
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123

    @deepcast.function(cast_return=True)
    def test(a: int):
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123

    @deepcast.function(cast_return=True)
    def test(a: int) -> str:
        assert isinstance(a, int)
        return a

    assert test(123) == "123"
    assert test("123") == "123"


def test_function_capture():
    @deepcast.function(cast_return=True)
    def test(a: int) -> str:
        return None

    with pytest.raises(TypeError):
        with capture() as error:
            test(None)
    assert error.location == ("a",)

    with pytest.raises(TypeError):
        with capture() as error:
            test("123")
    assert error.location == ("return",)


def test_function_method():
    class X:
        @deepcast.function
        def test1(self, a: int):
            assert isinstance(self, X)
            assert isinstance(a, int)
            return a

        @classmethod
        @deepcast.function
        def test2(cls, a: int):
            assert cls is X
            assert isinstance(a, int)
            return a

        @staticmethod
        @deepcast.function
        def test3(a: int):
            assert isinstance(a, int)
            return a

    x = X()

    assert x.test1(123) == 123
    assert x.test1("123") == 123

    assert x.test2(123) == 123
    assert x.test2("123") == 123

    assert X.test2(123) == 123
    assert X.test2("123") == 123

    assert x.test3(123) == 123
    assert x.test3("123") == 123

    assert X.test3(123) == 123
    assert X.test3("123") == 123


def test_function_async():
    @deepcast.function
    async def test(a: int):
        assert isinstance(a, int)
        return a

    assert inspect.iscoroutinefunction(test)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    assert loop.run_until_complete(test(123)) == 123
    assert loop.run_until_complete(test("123")) == 123
