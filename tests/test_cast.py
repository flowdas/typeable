# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest
from typeable.typing import (
    Dict,
    FrozenSet,
    List,
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


def test_get_args():
    class X(Object):
        i: int

    assert get_args(Type[int]) == (int,)
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
    assert get_args(Tuple[()]) == ((),)
    assert get_args(Tuple) == ()
    assert get_args(Union[int, None]) == (int, type(None))


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
