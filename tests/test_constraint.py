# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import inspect

from typeable.typing import (
    Annotated,
)
from typeable import *

import pytest


#
# Annotated
#

def test_Annotated():
    assert cast(Annotated[int, None, Constraint()], "123") == 123

    class Negative(Constraint):
        def emit(self):
            return 'x < 0'

    with pytest.raises(ValueError):
        cast(Annotated[int, Negative()], "123")


def test_JsonSchema_from_Annotated():
    assert cast(dict, JsonSchema(Annotated[int, None, Constraint()])) == {'type': 'integer'}


#
# Constraint
#

def test_Constraint():
    c = Constraint()
    assert c(0)
    assert c(1)

    c = Constraint()
    assert c.compile() is c.compile()

    class Bad(Constraint):
        def emit(self):
            return 'x.x'

    c = Bad()
    with pytest.raises(AttributeError):
        c(0)
    with pytest.raises(AttributeError):
        c(1)


def test_namespace():
    class X(Constraint):
        def emit(self):
            return 'inspect.isclass(x)', {'inspect': inspect}

    c = X()
    assert inspect.isclass(X)
    assert c(X)
    assert not c(1)


def test_AllOf():
    class Positive(Constraint):
        def emit(self):
            return '(x > 0)', None

        def annotate(self, root, schema):
            schema.format = 'positive'

    class LT10(Constraint):
        def emit(self):
            return '(x < 10)'

        def annotate(self, root, schema):
            schema.format = 'lt10'

    c = AllOf(Positive(), LT10())
    assert c(5)
    assert not c(0)
    assert not c(10)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {
        'allOf': [
            {'format': 'positive'},
            {'format': 'lt10'},
        ]
    }

    c = AllOf(Positive())
    assert c(1)
    assert not c(0)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(dict, schema) == {'format': 'positive'}


def test_AnyOf():
    class Negative(Constraint):
        def emit(self):
            return '(x < 0)', None

        def annotate(self, root, schema):
            schema.format = 'negative'

    class GT10(Constraint):
        def emit(self):
            return '(x > 10)'

        def annotate(self, root, schema):
            schema.format = 'gt10'

    c = AnyOf(Negative(), GT10())
    assert c(-1)
    assert c(11)
    assert not c(5)
    assert not c(0)
    assert not c(10)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {
        'anyOf': [
            {'format': 'negative'},
            {'format': 'gt10'},
        ]
    }

    c = AnyOf(Negative())
    assert c(-1)
    assert not c(0)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(dict, schema) == {'format': 'negative'}


def test_NoneOf():
    class Negative(Constraint):
        def emit(self):
            return '(x < 0)'

        def annotate(self, root, schema):
            schema.format = 'negative'

    class GT10(Constraint):
        def emit(self):
            return '(x > 10)', None

        def annotate(self, root, schema):
            schema.format = 'gt10'

    c = NoneOf(Negative(), GT10())
    assert not c(-1)
    assert not c(11)
    assert c(5)
    assert c(0)
    assert c(10)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {
        'not': {
            'anyOf': [
                {'format': 'negative'},
                {'format': 'gt10'},
            ]
        },
    }

    c = NoneOf(Negative())
    assert c(0)
    assert not c(-1)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {
        'not': {'format': 'negative'}
    }


def test_IsFinite():
    c = IsFinite()

    assert c(1)
    assert c(3.14)
    assert c(complex(1, 3))
    assert not c(float('nan'))
    assert not c(complex(3, float('nan')))


def test_range():
    c = IsGreaterThan(0)
    assert c(1)
    assert not c(0)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'exclusiveMinimum': 0}

    c = IsGreaterThanOrEqual(0)
    assert c(0)
    assert not c(-1)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'minimum': 0}

    c = IsLessThan(0)
    assert c(-1)
    assert not c(0)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'exclusiveMaximum': 0}

    c = IsLessThanOrEqual(0)
    assert c(0)
    assert not c(1)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'maximum': 0}


def test_length():
    c = IsLongerThanOrEqual(1)
    assert c([1])
    assert not c([])
    root = JsonSchema(str)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'minLength': 1}
    root = JsonSchema(dict)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'minProperties': 1}
    root = JsonSchema(list)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'minItems': 1}
    root = JsonSchema(int)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {}

    c = IsShorterThanOrEqual(1)
    assert c([1])
    assert not c([1, 2])
    root = JsonSchema(str)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'maxLength': 1}
    root = JsonSchema(dict)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'maxProperties': 1}
    root = JsonSchema(list)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {'maxItems': 1}
    root = JsonSchema(int)
    schema = JsonSchema()
    c.annotate(root, schema)
    assert cast(JsonValue, schema) == {}


def test_IsMultipleOf():
    c = IsMultipleOf(2)
    assert c(8)
    assert not c(5)
    assert c(4.0)
    assert not c(4.1)
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'multipleOf': 2}

    with pytest.raises(ValueError):
        IsMultipleOf(0)


def test_IsMatched():
    c = IsMatched('p')
    assert c('apple')
    assert not c('orange')
    schema = JsonSchema()
    c.annotate(schema, schema)
    assert cast(JsonValue, schema) == {'pattern': 'p'}
