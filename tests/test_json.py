import json
import io

import pytest

from typeable import cast, JsonSchema, JsonValue, dump, dumps
import typeable
from typeable.typing import (
    Any,
)


def test_JsonValue():
    data = {'a': ["0", True, 2, 3.14], 'b': range(4)}
    expected = {'a': ['0', True, 2, 3.14], 'b': [0, 1, 2, 3]}
    assert cast(JsonValue, data) == expected

    assert cast(JsonValue, []) == []
    assert cast(JsonValue, {}) == {}
    assert cast(JsonValue, ()) == ()


def test_dump():
    data = {'a': ["0", True, 2, 3.14], 'b': range(4)}
    fp = io.StringIO()
    dump(data, fp)
    assert fp.getvalue() == '{"a":["0",true,2,3.14],"b":[0,1,2,3]}'
    with pytest.raises(TypeError):
        json.dump(data, fp)


def test_dumps():
    data = {'a': ["0", True, 2, 3.14], 'b': range(4)}
    assert dumps(data) == '{"a":["0",true,2,3.14],"b":[0,1,2,3]}'
    with pytest.raises(TypeError):
        json.dumps(data)


def test_JsonSchema_instance():
    assert cast(dict, JsonSchema()) == {}
    assert cast(dict, JsonSchema({})) == {}


def test_JsonSchema_from_type():
    assert cast(dict, JsonSchema(Any)) == {}
