from typeable import capture, typecast
from typeable.schemas.openapi import OpenAPI, OpenAPI32


def test_v32_minimal():
    data = {"openapi": "3.2.0", "info": {"title": "", "version": ""}, "paths": {}}
    try:
        with capture() as error:
            schema = typecast(OpenAPI, data)
    except TypeError:
        print(error.location)
        raise
    assert isinstance(schema, OpenAPI32)
