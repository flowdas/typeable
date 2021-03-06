# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from collections.abc import Mapping
from .typing import (
    Type,
    Union,
    get_type_hints,
    get_origin,
    get_args,
)
from .cast import cast
from .context import Context

try:
    from dataclasses import MISSING
except ImportError:  # pragma: no cover
    class _MISSING_TYPE:
        pass
    MISSING = _MISSING_TYPE()

__all__ = [
    'MISSING',
    'Object',
    'field',
    'fields',
]

# avoid name mangling
_FIELDS = '__fields'
_VALIDATE = '__validate'


class Object:

    def __init__(self, value=MISSING, *, ctx=None):
        if ctx is None:
            ctx = Context()
        if isinstance(value, Mapping):
            flds = fields(self)
            for field in flds:
                if field.key in value:
                    val = value[field.key]
                elif field.required:
                    raise TypeError(
                        f"Missing key '{field.key}' for '{self.__class__.__qualname__}' object")
                elif field.default_factory is not None:
                    val = field.default_factory()
                else:
                    continue
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
            validate = getattr(self.__class__, _VALIDATE)
            if validate:
                validate(self)
        elif value is not MISSING:
            raise TypeError(
                f"'{value.__class__.__qualname__}' object is not mapping")

    def __init_subclass__(cls, *, validate=None, **kwargs):
        super().__init_subclass__(**kwargs)
        setattr(cls, _FIELDS, None)
        setattr(cls, _VALIDATE, validate)


class _Field:
    __slots__ = (
        'name',
        'type',
        'key',
        'default',
        'default_factory',
        'nullable',
        'required',
    )

    def __init__(self, key, default, default_factory, nullable, required):
        self.name = None
        self.type = MISSING
        self.key = key
        self.default = default
        self.default_factory = default_factory
        self.nullable = nullable
        self.required = required


def fields(class_or_instance):
    try:
        fields = getattr(class_or_instance, _FIELDS)
    except AttributeError:
        raise TypeError('must be called with an Object type or instance')
    if fields is None:
        cls = class_or_instance if _FIELDS in class_or_instance.__dict__ else class_or_instance.__class__
        fields = []
        for name, type in get_type_hints(cls).items():
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
            fields.append(f)
        fields = tuple(fields)
        setattr(cls, _FIELDS, fields)
    return fields


def field(*, key=None, default=MISSING, default_factory=None, nullable=None, required=False):
    if default is not MISSING and default_factory is not None:
        raise ValueError('cannot specify both default and default_factory')
    return _Field(key, default, default_factory, nullable, required)


@cast.register
def _(cls: Type[Object], val, ctx) -> Object:
    return cls(val, ctx=ctx)
