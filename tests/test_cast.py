# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import asyncio
import inspect
import sys

import pytest
from typeable.typing import (
    Annotated,
    Any,
    Dict,
    ForwardRef,
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
from typeable import *


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
    class X(Object):
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
    assert get_args(Literal['2.0']) == ('2.0',)
    assert get_args(Annotated) == ()
    assert get_args(Annotated[int, True, False]) == (int, True, False)


Integer = int


def test_declare():
    with declare('Integer') as Ref:
        T = List[Ref]

    assert cast(T, [2]) == [2]
    assert cast(T, ["2"]) == [2]


def test_register():
    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val, ctx) -> Object:
            return cls(val)


def test_invalid_register():
    with pytest.raises(TypeError):
        @cast.register
        def _():
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls, val, ctx):
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls: Object, val, ctx) -> Object:
            pass


def test_double_dispatch():
    class X:
        pass

    class Y(Object):
        pass

    @cast.register
    def _(cls, val: X, ctx) -> Object:
        return 1

    assert cast(Y, X()) == 1
    assert isinstance(cast(Y, {}), Y)

    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val: X, ctx) -> Object:
            return 1


def test_function():
    @cast.function
    def test(a: int):
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123
    with pytest.raises(TypeError):
        test(None)


def test_function_with_ctx():
    @cast.function
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
        @cast.function
        def test(ctx: int):
            pass

    with pytest.raises(TypeError):
        @cast.function
        def test(ctx):
            pass


def test_function_args():
    @cast.function
    def test(*args: int):
        for a in args:
            assert isinstance(a, int)
        return args

    assert test(1, "2", 3.14) == (1, 2, 3)


def test_function_kwargs():
    @cast.function
    def test(**kwargs: int):
        for k, v in kwargs.items():
            assert isinstance(v, int)
        return kwargs

    assert test(a=1, b="2", c=3.14) == {'a': 1, 'b': 2, 'c': 3}


def test_function_cast_return():
    @cast.function
    def test(a: int) -> str:
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123

    @cast.function(cast_return=True)
    def test(a: int):
        assert isinstance(a, int)
        return a

    assert test(123) == 123
    assert test("123") == 123

    @cast.function(cast_return=True)
    def test(a: int) -> str:
        assert isinstance(a, int)
        return a

    assert test(123) == '123'
    assert test("123") == '123'


def test_function_capture():
    @cast.function(cast_return=True)
    def test(a: int) -> str:
        return None

    ctx = Context()
    with pytest.raises(TypeError):
        with ctx.capture() as error:
            test(None, ctx=ctx)
    assert error.location == ('a',)

    with pytest.raises(TypeError):
        with ctx.capture() as error:
            test("123", ctx=ctx)
    assert error.location == ('return',)


def test_function_method():
    class X:
        @cast.function
        def test1(self, a: int):
            assert isinstance(self, X)
            assert isinstance(a, int)
            return a

        @classmethod
        @cast.function
        def test2(cls, a: int):
            assert cls is X
            assert isinstance(a, int)
            return a

        @staticmethod
        @cast.function
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
    @cast.function
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
