# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from dataclasses import dataclass, is_dataclass
from typing import Literal

import pytest

from typeable import cast, polymorphic, JsonValue, Context, is_polymorphic


def test_polymorphic_is_dataclass():
    @polymorphic
    class Authenticator:
        type: str

    assert is_dataclass(Authenticator)


def test_polymorphic_with_explicit_dataclass():
    @polymorphic
    @dataclass
    class Authenticator:
        type: str

    assert is_dataclass(Authenticator)


def test_polymorphic_requires_discriminator():
    with pytest.raises(TypeError):
        @polymorphic
        class Authenticator:
            pass


def test_polymorphic_prohibit_ambiguity():
    with pytest.raises(TypeError):
        @polymorphic
        class Authenticator:
            type: str
            scheme: str


def test_polymorphic_on():
    @polymorphic(on="type")
    class Authenticator:
        type: str
        scheme: str


def test_impl_requires_discriminator_redefinition():
    @polymorphic
    class Authenticator:
        type: str

    with pytest.raises(TypeError):
        @dataclass
        class ApiKeyAuthenticator(Authenticator):
            name: str = 'X-API-Key'


def test_impl_discriminator_is_literal():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    data = dict(
        type='apiKey',
        name='x-api-key',
    )

    x = cast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert cast(JsonValue, x) == data

    with pytest.raises(TypeError):
        @dataclass
        class ApiKeyAuthenticator2(Authenticator):
            type: str = "apiKey"
            name: str = 'X-API-Key'


def test_impl_discriminator_conflict():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    with pytest.raises(TypeError):
        @dataclass
        class ApiKeyAuthenticator2(Authenticator):
            type: Literal["apiKey"]
            name: str = 'X-API-Key'


def test_impl_discriminator_is_case_sensitive():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    data = dict(
        type='APIKEY',
        name='x-api-key',
    )

    with pytest.raises(TypeError):
        cast(Authenticator, data)


def test_impl_discriminator_type_mismatch():
    @polymorphic
    class Authenticator:
        type: str

    with pytest.raises(TypeError):
        @dataclass
        class ApiKeyAuthenticator(Authenticator):
            type: Literal[1]
            name: str = 'X-API-Key'


def test_impl_instanciation():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    data = dict(
        type='apiKey',
        name='x-api-key',
    )

    x = cast(ApiKeyAuthenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert cast(JsonValue, x) == data


def test_impl_discriminator_mismatch():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    @dataclass
    class HttpAuthenticator(Authenticator):
        type: Literal["http"]
        scheme: str = "bearer"

    data = dict(
        type='http',
    )

    with pytest.raises(TypeError):
        cast(ApiKeyAuthenticator, data)


def test_impl_type_check():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: int

    data = dict(
        type='apiKey',
        name='X-API-Key',
    )

    ctx = Context()

    with pytest.raises(ValueError):
        with ctx.capture() as error:
            cast(Authenticator, data, ctx=ctx)
    assert error.location == ("name",)


def test_impl_type_conversion():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: int

    data = dict(
        type='apiKey',
        name='123',
    )

    x = cast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert x.name == 123


def test_multiple_discriptor():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    @polymorphic
    class HttpAuthenticator(Authenticator):
        type: Literal["http"]
        scheme: str

    @dataclass
    class HttpBearerAuthenticator(HttpAuthenticator):
        scheme: Literal["bearer"]
        format: str = 'jwt'

    data = dict(
        type='http',
        scheme='bearer',
        format='JWT',
    )
    x = cast(Authenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert cast(JsonValue, x) == data


def test_partially_polymorphic():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    @polymorphic
    class HttpAuthenticator(Authenticator):
        type: Literal["http"]
        scheme: str

    @dataclass
    class HttpBearerAuthenticator(HttpAuthenticator):
        scheme: Literal["bearer"]
        format: str = 'jwt'

    data = dict(
        type='http',
        scheme='bearer',
        format='JWT',
    )
    x = cast(HttpAuthenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert cast(JsonValue, x) == data


def test_is_polymorphic():
    @polymorphic
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        type: Literal["apiKey"]
        name: str = 'X-API-Key'

    @polymorphic
    class HttpAuthenticator(Authenticator):
        type: Literal["http"]
        scheme: str

    assert is_polymorphic(Authenticator)
    assert not is_polymorphic(ApiKeyAuthenticator)
    assert is_polymorphic(HttpAuthenticator)
