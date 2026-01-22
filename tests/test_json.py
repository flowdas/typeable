import datetime
import enum
import json
import io
from typing import (
    Any,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import pytest

from typeable import deepcast, JsonSchema, JsonValue, dump, dumps, Object, field


def test_JsonValue():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    expected = {"a": ["0", True, 2, 3.14], "b": [0, 1, 2, 3]}
    assert deepcast(JsonValue, data) == expected

    assert deepcast(JsonValue, []) == []
    assert deepcast(JsonValue, {}) == {}
    assert deepcast(JsonValue, ()) == ()

    # JsonValue is abstract
    with pytest.raises(TypeError):
        JsonValue()


def test_JsonSchema_register():
    # conflict
    with pytest.raises(RuntimeError):

        @JsonSchema.register(bool)
        def _(self, cls: Type[bool]):
            self.type = "boolean"


def test_dump():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    fp = io.StringIO()
    dump(data, fp)
    assert fp.getvalue() == '{"a":["0",true,2,3.14],"b":[0,1,2,3]}'
    with pytest.raises(TypeError):
        json.dump(data, fp)


def test_dumps():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    assert dumps(data) == '{"a":["0",true,2,3.14],"b":[0,1,2,3]}'
    with pytest.raises(TypeError):
        json.dumps(data)


def test_JsonSchema_instance():
    assert deepcast(dict, JsonSchema()) == {}
    assert deepcast(dict, JsonSchema({})) == {}


#
# builtins
#


def test_JsonSchema_from_bool():
    assert deepcast(dict, JsonSchema(bool)) == {"type": "boolean"}


def test_JsonSchema_from_bytearray():
    assert deepcast(dict, JsonSchema(bytearray)) == {"type": "string"}


def test_JsonSchema_from_bytes():
    assert deepcast(dict, JsonSchema(bytes)) == {"type": "string"}


def test_JsonSchema_from_complex():
    assert deepcast(JsonValue, JsonSchema(complex)) == {
        "type": "array",
        "items": [
            {
                "type": "number",
            },
            {
                "type": "number",
            },
        ],
    }


def test_JsonSchema_from_dict():
    assert deepcast(dict, JsonSchema(dict)) == {"type": "object"}


def test_JsonSchema_from_float():
    assert deepcast(dict, JsonSchema(float)) == {"type": "number"}


def test_JsonSchema_from_frozenset():
    assert deepcast(dict, JsonSchema(frozenset)) == {"type": "array", "uniqueItems": True}


def test_JsonSchema_from_int():
    assert deepcast(dict, JsonSchema(int)) == {"type": "integer"}


def test_JsonSchema_from_list():
    assert deepcast(dict, JsonSchema(list)) == {"type": "array"}


def test_JsonSchema_from_None():
    assert deepcast(dict, JsonSchema(type(None))) == {"type": "null"}


def test_JsonSchema_from_object():
    assert deepcast(dict, JsonSchema(object)) == {}


def test_JsonSchema_from_set():
    assert deepcast(dict, JsonSchema(set)) == {"type": "array", "uniqueItems": True}


def test_JsonSchema_from_str():
    assert deepcast(dict, JsonSchema(str)) == {"type": "string"}


def test_JsonSchema_from_tuple():
    assert deepcast(dict, JsonSchema(tuple)) == {"type": "array"}


#
# datetime
#


def test_JsonSchema_from_date():
    assert deepcast(dict, JsonSchema(datetime.date)) == {"type": "string", "format": "date"}


def test_JsonSchema_from_datetime():
    assert deepcast(dict, JsonSchema(datetime.datetime)) == {
        "type": "string",
        "format": "date-time",
    }


def test_JsonSchema_from_time():
    assert deepcast(dict, JsonSchema(datetime.time)) == {"type": "string", "format": "time"}


def test_JsonSchema_from_timedelta():
    assert deepcast(dict, JsonSchema(datetime.timedelta)) == {
        "type": "string",
        "format": "duration",
    }


#
# enum
#


def test_JsonSchema_from_Enum():
    class Color(enum.Enum):
        RED = None
        GREEN = 1
        BLUE = "blue"

    assert deepcast(dict, JsonSchema(Color)) == {
        "type": "string",
        "enum": ["RED", "GREEN", "BLUE"],
    }


def test_JsonSchema_from_Flag():
    class Perm(enum.Flag):
        R = 4
        W = 2
        X = 1

    assert deepcast(dict, JsonSchema(Perm)) == {
        "type": "integer",
    }


def test_JsonSchema_from_IntEnum():
    class Shape(enum.IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert deepcast(dict, JsonSchema(Shape)) == {
        "type": "integer",
        "enum": [1, 2],
    }


def test_JsonSchema_from_IntFlag():
    class Perm(enum.IntFlag):
        R = 4
        W = 2
        X = 1

    assert deepcast(dict, JsonSchema(Perm)) == {
        "type": "integer",
    }


#
# typing
#


def test_JsonSchema_from_Any():
    assert deepcast(dict, JsonSchema(Any)) == {}


def test_JsonSchema_from_Dict():
    assert deepcast(JsonValue, JsonSchema(Dict[str, int])) == {
        "type": "object",
        "additionalProperties": {"type": "integer"},
    }


def test_JsonSchema_from_FrozenSet():
    assert deepcast(JsonValue, JsonSchema(FrozenSet[str])) == {
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": "string",
        },
    }


def test_JsonSchema_from_List():
    assert deepcast(JsonValue, JsonSchema(List[str])) == {
        "type": "array",
        "items": {
            "type": "string",
        },
    }


def test_JsonSchema_from_Literal():
    assert deepcast(JsonValue, JsonSchema(Literal[0, "1", 2.3])) == {
        "enum": [0, "1", 2.3],
    }


def test_JsonSchema_from_Optional():
    assert deepcast(JsonValue, JsonSchema(Optional[int])) == {
        "type": ["integer", "null"],
    }


def test_JsonSchema_from_Set():
    assert deepcast(JsonValue, JsonSchema(Set[str])) == {
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": "string",
        },
    }


def test_JsonSchema_from_Tuple():
    assert deepcast(JsonValue, JsonSchema(Tuple[str, ...])) == {
        "type": "array",
        "items": {
            "type": "string",
        },
    }

    assert deepcast(JsonValue, JsonSchema(Tuple[()])) == {
        "type": "array",
        "items": [],
    }

    assert deepcast(JsonValue, JsonSchema(Tuple[(str, int)])) == {
        "type": "array",
        "items": [
            {
                "type": "string",
            },
            {
                "type": "integer",
            },
        ],
    }

    assert deepcast(JsonValue, JsonSchema(Tuple[(float, float)])) == {
        "type": "array",
        "items": [
            {
                "type": "number",
            },
            {
                "type": "number",
            },
        ],
    }


def test_JsonSchema_from_Union():
    assert deepcast(JsonValue, JsonSchema(Union[str, int, bool])) == {
        "type": ["string", "integer", "boolean"],
    }

    assert deepcast(JsonValue, JsonSchema(Union[str, int, bool, Any])) == {}

    assert deepcast(JsonValue, JsonSchema(Union[str, List[str]])) == {
        "anyOf": [
            {
                "type": "string",
            },
            {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
        ]
    }

    class Number:
        pass

    @JsonSchema.register(Number)
    def _(self, cls):
        self.type = ["integer", "number"]

    assert deepcast(JsonValue, JsonSchema(Union[str, int, Number])) == {
        "type": ["string", "integer", "number"],
    }


#
# typeable types
#


def test_JsonSchema_from_JsonValue():
    assert deepcast(JsonValue, JsonSchema(JsonValue)) == {}


def test_JsonSchema_from_Object():
    class X(Object):
        a: int
        b: str = field(required=True)

    assert deepcast(JsonValue, JsonSchema(X)) == {
        "type": "object",
        "properties": {
            "a": {
                "type": "integer",
            },
            "b": {
                "type": "string",
            },
        },
        "required": ["b"],
        "additionalProperties": False,
    }

    uri = "https://raw.githubusercontent.com/open-rpc/meta-schema/master/schema.json"

    class OpenRpcDoc(Object, jsonschema=uri):
        pass

    assert deepcast(JsonValue, JsonSchema(OpenRpcDoc)) == {"$ref": uri}

    class Empty(Object):
        pass

    assert deepcast(JsonValue, JsonSchema(Empty)) == {
        "type": "object",
        "additionalProperties": False,
    }

    class AllOptional(Object):
        a: int

    assert deepcast(JsonValue, JsonSchema(AllOptional)) == {
        "type": "object",
        "properties": {
            "a": {
                "type": "integer",
            },
        },
        "additionalProperties": False,
    }
