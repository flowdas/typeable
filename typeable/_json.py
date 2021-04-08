# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from abc import get_cache_token
from dataclasses import MISSING
import datetime
import enum
from functools import _find_impl
import json

from ._cast import cast, declare, _get_type_args
from ._object import Object, fields, field, _META
from .typing import Union, Dict, List, Tuple, _GenericBases, get_origin, Type, Any, Literal

with declare('_JsonValue') as _:
    _JsonValue = Union[float, bool, int, str, None, Dict[str, _], List[_], Tuple[_, ...]]


class JsonValue:
    def __init__(self):
        raise TypeError(f"Can't instantiate JsonValue")


@cast.register
def _cast_JsonValue_object(cls: Type[JsonValue], val, ctx):
    return cast(_JsonValue, val, ctx=ctx)


@cast.function
def dump(obj: JsonValue, fp, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dump(obj, fp, ensure_ascii=ensure_ascii, separators=separators, **kw)


@cast.function
def dumps(obj: JsonValue, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators, **kw)


_TypeBases = (type,) + _GenericBases


def _istype(tp):
    return issubclass(type(tp), _TypeBases)


class JsonSchema(Object):
    _registry = {}
    _dispatch_cache = {}
    _cache_token = None

    ref: str = field(key='$ref')
    type: Union[str, List[str]]
    uniqueItems: bool
    format: str
    enum: list
    additionalProperties: Union[bool, 'JsonSchema']
    items: Union['JsonSchema', List['JsonSchema']]
    allOf: List['JsonSchema']
    anyOf: List['JsonSchema']
    not_: 'JsonSchema' = field(key='not')
    properties: Dict[str, 'JsonSchema']
    required: List[str]
    exclusiveMinimum: Union[int, float]
    exclusiveMaximum: Union[int, float]
    minimum: Union[int, float]
    maximum: Union[int, float]
    minLength: int
    maxLength: int
    minProperties: int
    maxProperties: int
    minItems: int
    maxItems: int

    def __init__(self, value_or_type=MISSING, *, ctx=None):
        if value_or_type is MISSING:
            super().__init__(ctx=ctx)
        elif not _istype(value_or_type):
            super().__init__(value_or_type, ctx=ctx)
        else:
            origin = get_origin(value_or_type) or value_or_type
            func = self.dispatch(origin)
            if func:
                func(self, origin, *_get_type_args(value_or_type))

    @classmethod
    def register(cls, klass):
        def deco(func):
            if klass in cls._registry:
                raise RuntimeError(f"Ambiguous `JsonSchema.register()`")
            cls._registry[klass] = func

            if cls._cache_token is None:
                if hasattr(klass, '__abstractmethods__'):
                    cls._cache_token = get_cache_token()
            cls._dispatch_cache.clear()

            return func

        return deco

    @classmethod
    def dispatch(cls, tp):
        if cls._cache_token is not None:
            current_token = get_cache_token()
            if cls._cache_token != current_token:
                cls._dispatch_cache.clear()
                cls._cache_token = current_token

        try:
            func = cls._dispatch_cache[tp]
        except KeyError:
            try:
                func = cls._registry[tp]
            except KeyError:
                func = _find_impl(tp, cls._registry)
                if func:
                    cls._dispatch_cache[tp] = func

        return func


#
# builtins
#


@JsonSchema.register(bool)
def _jsonschema_bool(self, cls: Type[bool]):
    self.type = 'boolean'


@JsonSchema.register(bytearray)
def _jsonschema_bytearray(self, cls: Type[bytearray]):
    self.type = 'string'


@JsonSchema.register(bytes)
def _jsonschema_bytes(self, cls: Type[bytes]):
    self.type = 'string'


@JsonSchema.register(complex)
def _jsonschema_complex(self, cls: Type[complex]):
    self.type = 'array'
    self.items = [JsonSchema(float), JsonSchema(float)]


@JsonSchema.register(dict)
def _jsonschema_dict(self, cls: Type[dict], K=None, V=None):
    self.type = 'object'
    if K is not None:
        self.additionalProperties = JsonSchema(V)


@JsonSchema.register(float)
def _jsonschema_float(self, cls: Type[float]):
    self.type = 'number'


@JsonSchema.register(frozenset)
def _jsonschema_frozenset(self, cls: Type[frozenset], T=None):
    self.type = 'array'
    self.uniqueItems = True
    if T is not None:
        self.items = JsonSchema(T)


@JsonSchema.register(int)
def _jsonschema_int(self, cls: Type[int]):
    self.type = 'integer'


@JsonSchema.register(list)
def _jsonschema_list(self, cls: Type[list], T=None):
    self.type = 'array'
    if T is not None:
        self.items = JsonSchema(T)


@JsonSchema.register(type(None))
def _jsonschema_None(self, cls: Type[None]):
    self.type = 'null'


@JsonSchema.register(set)
def _jsonschema_set(self, cls: Type[set], T=None):
    self.type = 'array'
    self.uniqueItems = True
    if T is not None:
        self.items = JsonSchema(T)


@JsonSchema.register(str)
def _jsonschema_str(self, cls: Type[str]):
    self.type = 'string'


@JsonSchema.register(tuple)
def _jsonschema_tuple(self, cls: Type[tuple], *Ts):
    self.type = 'array'

    if not Ts:
        return

    if Ts[-1] == ...:
        self.items = JsonSchema(Ts[0])
        return

    if Ts[0] == ():
        Ts = ()

    self.items = [JsonSchema(T) for T in Ts]


#
# datetime
#


@JsonSchema.register(datetime.date)
def _jsonschema_date(self, cls: Type[datetime.date]):
    self.type = 'string'
    self.format = 'date'


@JsonSchema.register(datetime.datetime)
def _jsonschema_datetime(self, cls: Type[datetime.datetime]):
    self.type = 'string'
    self.format = 'date-time'


@JsonSchema.register(datetime.time)
def _jsonschema_time(self, cls: Type[datetime.time]):
    self.type = 'string'
    self.format = 'time'


@JsonSchema.register(datetime.timedelta)
def _jsonschema_timedelta(self, cls: Type[datetime.timedelta]):
    self.type = 'string'
    self.format = 'duration'


#
# enum
#


@JsonSchema.register(enum.Enum)
def _jsonschema_Enum(self, cls: Type[enum.Enum]):
    self.type = 'string'
    self.enum = [x.name for x in cls]


@JsonSchema.register(enum.Flag)
def _jsonschema_Flag(self, cls: Type[enum.Flag]):
    self.type = 'integer'


@JsonSchema.register(enum.IntEnum)
def _jsonschema_IntEnum(self, cls: Type[enum.IntEnum]):
    self.type = 'integer'
    self.enum = [x.value for x in cls]


@JsonSchema.register(enum.IntFlag)
def _jsonschema_IntFlag(self, cls: Type[enum.IntFlag]):
    self.type = 'integer'


#
# typing
#


@JsonSchema.register(Any)
def _jsonschema_Any(self, cls: Type[Any]):
    pass


@JsonSchema.register(Literal)
def _jsonschema_Literal(self, cls, *Ts):
    self.enum = list(Ts)


@JsonSchema.register(Union)
def _jsonschema_Union(self, cls, *Ts):
    schemas = []
    simple = True
    for T in Ts:
        schema = JsonSchema(T)
        json = cast(JsonValue, schema)
        if not json:  # {}
            return
        if 'type' not in json or len(json) != 1:
            simple = False
        schemas.append(schema)
    if simple:
        types = {}
        for schema in schemas:
            if isinstance(schema.type, str):
                values = [schema.type]
            else:
                values = schema.type
            for value in values:
                if value not in types:
                    types[value] = None
        self.type = list(types.keys())
    else:
        self.anyOf = schemas


#
# typeable
#


@JsonSchema.register(JsonValue)
def _jsonschema_JsonValue(self, cls):
    pass


@JsonSchema.register(Object)
def _jsonschema_Object(self, cls):
    meta = getattr(cls, _META)
    if meta.jsonschema:
        self.ref = meta.jsonschema
    else:
        self.type = 'object'
        self.additionalProperties = False

        flds = fields(cls)
        if flds:
            properties = {}
            required = []
            for f in flds:
                properties[f.key] = JsonSchema(f.type)
                if f.required:
                    required.append(f.key)
            self.properties = properties
            if required:
                self.required = required
