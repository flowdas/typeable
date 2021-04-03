# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from collections.abc import Mapping
from .typing import (
    Type,
    get_type_hints,
)
from ._cast import cast
from ._context import Context

from dataclasses import MISSING

# avoid name mangling
_FIELDS = '__fields'
_VTABLE = '__vtable'
_META = '__meta'


class Object:

    def __init__(self, _=MISSING, *, ctx=None, **kwargs):
        vtable = getattr(self.__class__, _VTABLE, None)
        kind = getattr(self.__class__, _META).kind
        if vtable and kind is None:
            raise TypeError(
                f"Can't instantiate abstract class {self.__class__.__qualname__} with kind field {vtable.field.name}")

        if ctx is None:
            ctx = Context()
        if kwargs:
            if _ is MISSING:
                value = kwargs
            else:
                raise TypeError
        else:
            value = _

        if isinstance(value, Mapping):
            flds = fields(self.__class__)
            for field in flds:
                if field.kind:
                    val = value.get(field.key, kind)
                    if val != kind:
                        with ctx.traverse(field.key):
                            raise TypeError(
                                f"Unexpected '{self.__class__.__qualname__}.{vtable.field.name}' field value: {val}")
                elif field.key in value:
                    val = value[field.key]
                elif field.required:
                    with ctx.traverse(field.key):
                        raise TypeError(
                            f"Missing key '{field.key}' for '{self.__class__.__qualname__}' object")
                elif field.default_factory is not None:
                    val = field.default_factory()
                else:
                    continue  # pragma: no cover; TODO: coverage's bug?
                if val is None and field.nullable is not None:
                    if field.nullable:
                        self.__dict__[field.name] = val
                    else:
                        with ctx.traverse(field.key):
                            raise TypeError("None not allowed")
                else:
                    with ctx.traverse(field.key):
                        val = cast(field.type, val, ctx=ctx)
                self.__dict__[field.name] = val
        elif value is MISSING:
            flds = fields(self)
            for field in flds:
                if field.kind:
                    self.__dict__[field.name] = kind
                elif field.default_factory is not None:
                    self.__dict__[field.name] = field.default_factory()
        else:
            raise TypeError(
                f"'{value.__class__.__qualname__}' object is not mapping")

    def __new__(cls, _=MISSING, *, ctx=None, **kwargs):
        if kwargs:
            if _ is MISSING:
                value = kwargs
            else:
                return super().__new__(cls)
        else:
            value = _
        vtable = getattr(cls, _VTABLE, None)
        if not vtable or getattr(cls, _META).kind is not None:
            return super().__new__(cls)
        if isinstance(value, Mapping):
            fields(cls)  # resolve _Field.key
            kind = value.get(vtable.field.key)
            if kind in vtable.classes:
                klass = vtable.classes[kind]
                if issubclass(klass, cls):
                    cls = klass
                else:
                    raise TypeError(f"{klass.__qualname__} is not subclass of {cls.__qualname__}")
            else:
                raise TypeError(f"Unknown '{vtable.field.name}' field value: {kind}")

        return super().__new__(cls)

    def __init_subclass__(cls, *, kind=None, jsonschema=None):
        super().__init_subclass__()
        setattr(cls, _FIELDS, None)

        vtable = getattr(cls, _VTABLE, None)
        created = False
        for name, val in cls.__dict__.items():
            if isinstance(val, _Field) and val.kind:
                if vtable:
                    raise TypeError(f"Duplicated kind field '{name}'")
                vtable = _VTable(val)
                created = True
        if created:
            setattr(cls, _VTABLE, vtable)
        if kind is not None:
            if not vtable:
                raise TypeError(f"No kind field")
            if kind in vtable.classes:
                raise TypeError(f"Kind '{kind}' is already defined by class {vtable.classes[kind].__qualname__}")
            else:
                vtable.classes[kind] = cls
        setattr(cls, _META, _Meta(kind, jsonschema))


setattr(Object, _FIELDS, None)


class _VTable:
    __slots__ = (
        'field',
        'classes',
    )

    def __init__(self, field):
        self.field = field
        self.classes = {}


class _Meta:
    __slots__ = (
        'kind',
        'jsonschema',
    )

    def __init__(self, kind, jsonschema):
        self.kind = kind
        self.jsonschema = jsonschema


setattr(Object, _META, _Meta(None, None))


class _Field:
    __slots__ = (
        'name',
        'type',
        'key',
        'default',
        'default_factory',
        'nullable',
        'required',
        'kind',
    )

    def __init__(self, key, default, default_factory, nullable, required, kind):
        self.name = None
        self.type = MISSING
        self.key = key
        self.default = default
        self.default_factory = default_factory
        self.nullable = nullable
        self.required = required
        self.kind = kind

    def __repr__(self):
        return f"_Field({id(self)}: {self.key!r}, {self.default!r}, {self.default_factory!r}, {self.nullable!r}, {self.required!r}, {self.kind!r})"


def fields(class_or_instance):
    try:
        _fields = getattr(class_or_instance, _FIELDS)
    except AttributeError:
        raise TypeError(f"must be called with an Object type or instance: {class_or_instance}")
    if _fields is None:
        cls = class_or_instance if _FIELDS in class_or_instance.__dict__ else class_or_instance.__class__
        fields_map = {}
        for b in cls.__mro__[-1:0:-1]:
            # Only process Object subclasses
            if not issubclass(b, Object):
                continue
            base_fields = fields(b)
            if base_fields:
                for f in base_fields:
                    fields_map[f.name] = f

        _fields = []
        # We need __annotations__ to find the newly defined field in cls.
        # __annotations__ may not be defined, and for this purpose it should be looked up in cls.__dict__.
        annotations = cls.__dict__.get('__annotations__', {})
        for name, type in get_type_hints(cls).items():
            if name in annotations:
                has_class_var = hasattr(cls, name)
                if has_class_var:
                    default = getattr(cls, name)
                    if isinstance(default, _Field):
                        f = default
                    else:
                        f = field(default=default)
                else:
                    f = field()
                f.name, f.type = name, type
                if f.key is None:
                    f.key = name
                if f.default is not MISSING:
                    if f.default is None:
                        if f.nullable is None:
                            f.nullable = True
                    else:
                        # validate default. Note ctx not transferred. Is this wrong decision?
                        f.default = cast(f.type, f.default)
                    setattr(cls, name, f.default)
                elif has_class_var:
                    delattr(cls, name)
            else:
                f = fields_map[name]
            _fields.append(f)
        _fields = tuple(_fields)
        setattr(cls, _FIELDS, _fields)
    return _fields


def field(*, key=None, default=MISSING, default_factory=None, nullable=None, required=False, kind=False):
    if default is not MISSING and default_factory is not None:
        raise ValueError('cannot specify both default and default_factory')
    if nullable and kind:
        raise ValueError('kind cannot be nullable')
    return _Field(key, default, default_factory, nullable, required, kind)


@cast.register
def _cast_Object_object(cls: Type[Object], val, ctx):
    # assume not isinstance(val, cls)
    return cls(val, ctx=ctx)


@cast.register
def _cast_dict_Object(cls: Type[dict], val: Object, ctx, K=None, V=None):
    d = val.__dict__
    r = cls()
    for f in fields(val):
        if f.name in d:
            if K is None:
                r[f.key] = d[f.name]
            else:
                with ctx.traverse(f.key):
                    r[cast(K, f.key, ctx=ctx)] = cast(V, d[f.name], ctx=ctx)
    return r
