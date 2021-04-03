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

    x = X(**data)
    assert x.i == data['i']

    with pytest.raises(TypeError):
        X({}, **data)

    with pytest.raises(TypeError):
        X(1)


def test_missing():
    class X(Object):
        i: int
        j: int

    data = {'i': 0}

    x = X(data)
    assert x.i == data['i']
    with pytest.raises(AttributeError):
        x.j

    x = X(**data)
    assert x.i == data['i']
    with pytest.raises(AttributeError):
        x.j


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

    z = X()
    assert z.l == []


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
        a: int  # not allowed
        b: int = None  # allowed
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


def test_cast():
    class X(Object):
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert x.i == data['i']


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


def test_dict():
    class X(Object):
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert cast(dict, x) == data


def test_JsonValue():
    class X(Object):
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert cast(JsonValue, x) == data

    assert cast(JsonValue, {'result': X()}) == {'result': {}}


def test_kind():
    class Authenticator(Object):  # abstract
        type: str = field(kind=True)

    class ApiKeyAuthenticator(Authenticator, kind='apiKey'):  # concrete
        name: str = 'X-API-Key'

    class HttpAuthenticator(Authenticator):  # abstract
        pass

    class HttpBearerAuthenticator(HttpAuthenticator, kind='http.bearer'):  # concrete
        format: str = 'jwt'

    data = dict(
        type='apiKey',
        name='x-api-key',
    )
    x = cast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert cast(JsonValue, x) == data

    with pytest.raises(TypeError):  # no kind field
        cast(Authenticator, {'name': 'x-api-key'})

    with pytest.raises(TypeError):  # incompatible kind field
        cast(HttpAuthenticator, dict(
            type='apiKey',
            name='x-api-key',
        ))

    data = dict(
        type='http.bearer',
        format='JWT',
    )
    x = cast(Authenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert cast(JsonValue, x) == data

    x = cast(HttpAuthenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert cast(JsonValue, x) == data

    # For concrete classes, the kind field behaves as if default_factory was specified.
    x = cast(HttpBearerAuthenticator, dict(format=data['format']))
    assert isinstance(x, HttpBearerAuthenticator)
    assert cast(JsonValue, x) == data

    # only one kind field allowed
    with pytest.raises(TypeError):
        class XAuthenticator(Authenticator):
            scheme: str = field(kind=True)

    # kind option requires kind field
    with pytest.raises(TypeError):
        class XObject(Object, kind='X'):
            pass

    # duplicated kind option not allowed
    with pytest.raises(TypeError):
        class XAuthenticator(Authenticator, kind='apiKey'):
            pass

    # kind field cannot be nullable
    with pytest.raises(ValueError):
        class XObject(Object):
            type: str = field(kind=True, nullable=True)


def test_kind_fields():
    class Authenticator(Object):  # abstract
        type: str = field(kind=True)

    class ApiKeyAuthenticator(Authenticator, kind='apiKey'):  # concrete
        name: str = 'X-API-Key'

    class HttpAuthenticator(Authenticator):  # abstract
        pass

    class HttpBearerAuthenticator(HttpAuthenticator, kind='http.bearer'):  # concrete
        format: str = 'jwt'

    flds = fields(Authenticator)
    assert len(flds) == 1
    assert flds[0].kind
    type_field = flds[0]

    flds = fields(ApiKeyAuthenticator)
    assert len(flds) == 2
    assert flds[0] is type_field
    assert flds[0].name == 'type'
    assert flds[0].kind

    flds = fields(HttpAuthenticator)
    assert len(flds) == 1
    assert flds[0] is type_field
    assert flds[0].name == 'type'
    assert flds[0].kind

    flds = fields(HttpBearerAuthenticator)
    assert len(flds) == 2
    assert flds[0] is type_field
    assert flds[0].name == 'type'
    assert flds[0].kind


def test_kind_ctor():
    class Authenticator(Object):  # abstract
        type: str = field(kind=True)

    class ApiKeyAuthenticator(Authenticator, kind='apiKey'):  # concrete
        name: str = 'X-API-Key'

    with pytest.raises(TypeError):  # cannot instantiate abstract class
        Authenticator()

    x = ApiKeyAuthenticator()
    assert x.__class__ is ApiKeyAuthenticator
    assert x.type == 'apiKey'

    x = ApiKeyAuthenticator(name='x-api-key')
    assert x.type == 'apiKey'
    assert x.name == 'x-api-key'
    assert x.__class__ is ApiKeyAuthenticator

    x = ApiKeyAuthenticator(type='apiKey', name='x-api-key')
    assert x.type == 'apiKey'
    assert x.name == 'x-api-key'
    assert x.__class__ is ApiKeyAuthenticator

    # cannot instantiate concrete class with invalid kind
    with pytest.raises(TypeError):
        ApiKeyAuthenticator(type='x', name='x-api-key')
