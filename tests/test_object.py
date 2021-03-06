# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest

from typeable import *


def test_empty_constructor():
    class X(Object):
        i: int

    x = X()

    with pytest.raises(AttributeError):
        x.i

    x.i = 0
    assert x.i == 0

    del x.i
    with pytest.raises(AttributeError):
        x.i


def test_initializer():
    class X(Object):
        i: int

    data = {'i': 0}

    x = X(data)
    assert x.i == data['i']

    with pytest.raises(TypeError):
        X(1)


class NestedX(Object):
    x: 'NestedX'


def test_nesting():
    class X(Object):
        x: NestedX

    data = {'x': {'x': {}}}
    x = X(data)

    assert isinstance(x.x, NestedX)
    assert isinstance(x.x.x, NestedX)

    with pytest.raises(AttributeError):
        x.x.x.x


def test_fields():
    class X(Object):
        i: int = 1

    flds = fields(X)
    assert isinstance(flds, tuple)
    assert len(flds) == 1
    field = flds[0]
    assert field.name == 'i'
    assert field.type == int
    assert field.default == 1

    assert fields(X()) == flds

    class Y:
        i: int = 1

    with pytest.raises(TypeError):
        fields(Y)


def test_default():
    class X(Object):
        i: int = 1

    class Y(Object):
        i: int = field(default=1)

    for T in (X, Y):
        data = {}
        x = T(data)

        assert x.i == 1

        data = {'i': 0}
        x = T(data)

        assert x.i == 0


def test_None_default():
    class X(Object):
        i: int = None

    class Y(Object):
        i: int = field(default=None)

    for T in (X, Y):
        data = {}
        x = T(data)

        assert x.i is None

        data = {'i': 0}
        x = T(data)

        assert x.i == 0

        data = {'i': None}
        x = T(data)

        assert x.i is None


def test_default_factory():
    class X(Object):
        l: list = field(default_factory=list)

    fields(X)  # resolve
    assert 'l' not in X.__dict__

    data = {}
    x = X(data)

    assert x.l == []

    y = X(data)
    assert y.l is not x.l

    assert 'l' in x.__dict__


def test_default_collison():
    with pytest.raises(ValueError):
        field(default=1, default_factory=lambda: 1)


def test_key():
    class X(Object):
        _def: bool = field(key='def')
        _return: bool = field(key='return')

    data = {'def': True, 'return': False}
    x = X(data)

    assert x._def
    assert not x._return


def test_inheritance():
    class B(Object):
        i: int = 1
        s: str
        f: float = 3

    class X(B):
        i = 2
        j: int

    data = {'s': 'str', 'j': 0}
    x = X(data)

    assert x.i == 2
    assert x.s == 'str'
    assert x.f == 3
    assert x.j == 0

    data = {'i': 9, 's': 'str', 'f': 99, 'j': 0}
    x = X(data)

    assert x.i == 9
    assert x.s == 'str'
    assert x.f == 99
    assert x.j == 0

    flds = fields(X)

    assert len(flds) == 4


def test_nullable():
    class X(Object):
        a: int          # not allowed
        b: int = None   # allowed
        c: int = field(nullable=True)  # allowed
        # not allowed, but default is None
        d: int = field(default=None, nullable=False)

    for key in ('a', 'd'):
        data = {key: None}
        with pytest.raises(TypeError):
            cast(X, data)

    for key in ('b', 'c'):
        data = {key: None}
        x = cast(X, data)
        assert getattr(x, key) is None

    assert X.d is None


def test_required():
    class X(Object):
        a: int  # not required
        b: int = field(required=True)  # required

    data = {'b': 1}
    x = cast(X, data)
    assert x.b == 1
    with pytest.raises(AttributeError):
        x.a

    data = {'a': 1}
    with pytest.raises(TypeError):
        cast(X, data)


def test_class_validate():
    def positive(self):
        if self.i <= 0:
            raise ValueError

    class X(Object, validate=positive):
        i: int

    data = {'i': 1}
    x = cast(X, data)
    assert x.i == 1

    data = {'i': 0}
    with pytest.raises(ValueError):
        x = cast(X, data)
