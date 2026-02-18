from dataclasses import dataclass, is_dataclass

import pytest

from typeable import capture, identity, localcontext, polymorphic, typecast


def test_polymorphic_with_plain_class():
    @polymorphic(on="type")
    class Authenticator:
        def __init__(self, type: str):
            self._type = str


def test_polymorphic_with_dataclass():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    assert is_dataclass(Authenticator)


def test_polymorphic_requires_discriminator():
    with pytest.raises(TypeError):

        @polymorphic(on="")
        class Authenticator:
            pass


def test_polymorphic_requires_str():
    with pytest.raises(TypeError):

        @polymorphic(on="type")
        @dataclass
        class Authenticator:
            type: int


def test_polymorphic_on():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str
        scheme: str


def test_single_polymorphic():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    data = dict(
        type="apiKey",
        name="x-api-key",
    )

    x = typecast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert typecast(dict, x) == data

    with pytest.raises(TypeError):

        @identity("apiKey")
        @dataclass
        class ApiKeyAuthenticator2(Authenticator):
            name: str = "X-API-Key"


def test_impl_do_not_requires_identity():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator2(ApiKeyAuthenticator):
        name2: str = "X-API-Key"

    data = dict(
        type="apiKey",
        name="x-api-key",
        name2="XXX",
    )

    x = typecast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator2)
    assert typecast(dict, x) == data


def test_impl_discriminator_conflict():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    with pytest.raises(TypeError):

        @identity("apiKey")
        @dataclass
        class ApiKeyAuthenticator2(Authenticator):
            name: str = "X-API-Key"


def test_impl_discriminator_is_case_sensitive():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    data = dict(
        type="APIKEY",
        name="x-api-key",
    )

    with pytest.raises(TypeError):
        typecast(Authenticator, data)


def test_impl_discriminator_type_mismatch():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    with pytest.raises(TypeError):

        @identity(1)
        @dataclass
        class ApiKeyAuthenticator(Authenticator):
            name: str = "X-API-Key"


def test_impl_instanciation():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    data = dict(
        type="apiKey",
        name="x-api-key",
    )

    x = typecast(ApiKeyAuthenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert typecast(dict, x) == data


def test_impl_discriminator_mismatch():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    @identity("http")
    @dataclass
    class HttpAuthenticator(Authenticator):
        scheme: str = "bearer"

    data = dict(
        type="http",
    )

    with pytest.raises(TypeError):
        typecast(ApiKeyAuthenticator, data)


def test_impl_type_check():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: int

    data = dict(
        type="apiKey",
        name="X-API-Key",
    )

    with pytest.raises(TypeError):
        with capture() as error:
            typecast(Authenticator, data)
    assert error.location == ("name",)


def test_impl_type_conversion():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: int

    data = dict(
        type="apiKey",
        name="123",
    )

    with localcontext(parse_number=True):
        x = typecast(Authenticator, data)
    assert isinstance(x, ApiKeyAuthenticator)
    assert x.name == 123


def test_multiple_polymorphic():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    @polymorphic(on="scheme")
    @identity("http")
    @dataclass
    class HttpAuthenticator(Authenticator):
        scheme: str

    @identity("bearer")
    @dataclass
    class HttpBearerAuthenticator(HttpAuthenticator):
        format: str = "jwt"

    data = dict(
        type="http",
        scheme="bearer",
        format="JWT",
    )
    x = typecast(Authenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert typecast(dict, x) == data


def test_partially_polymorphic():
    @polymorphic(on="type")
    @dataclass
    class Authenticator:
        type: str

    @identity("apiKey")
    @dataclass
    class ApiKeyAuthenticator(Authenticator):
        name: str = "X-API-Key"

    @polymorphic(on="scheme")
    @identity("http")
    @dataclass
    class HttpAuthenticator(Authenticator):
        scheme: str

    @identity("bearer")
    @dataclass
    class HttpBearerAuthenticator(HttpAuthenticator):
        format: str = "jwt"

    data = dict(
        type="http",
        scheme="bearer",
        format="JWT",
    )
    x = typecast(HttpAuthenticator, data)
    assert isinstance(x, HttpBearerAuthenticator)
    assert typecast(dict, x) == data


def test_alias():
    @polymorphic(on="_schema")
    @dataclass
    class JsonSchema:
        _schema: str = typecast.field(alias="$schema")

    @identity("https://json-schema.org/draft/2020-12/schema")
    @dataclass
    class JsonSchema202012(JsonSchema):
        pass

    @identity("https://json-schema.org/draft/2019-09/schema")
    @dataclass
    class JsonSchema201909(JsonSchema):
        pass

    x = typecast(
        JsonSchema, {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    )
    assert isinstance(x, JsonSchema202012)


def test_key():
    def remove_patch_version(version):
        try:
            return ".".join(version.split(".")[:2])
        except Exception:
            return version

    @polymorphic(on="openapi", key=remove_patch_version)
    @dataclass
    class OpenAPI:
        openapi: str

    @identity("3.0")
    @dataclass
    class OpenAPI30(OpenAPI):
        pass

    @identity("3.1")
    @dataclass
    class OpenAPI31(OpenAPI):
        pass

    @identity("3.2")
    @dataclass
    class OpenAPI32(OpenAPI):
        pass

    for version, cls in [
        ("3.0.4", OpenAPI30),
        ("3.1.2", OpenAPI31),
        ("3.2.0", OpenAPI32),
    ]:
        x = typecast(OpenAPI, {"openapi": version})
        assert isinstance(x, cls)
