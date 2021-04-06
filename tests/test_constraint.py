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

        def annotate(self, schema):
            schema.format = 'positive'

    class LT10(Constraint):
        def emit(self):
            return '(x < 10)'

        def annotate(self, schema):
            schema.format = 'lt10'

    c = AllOf(Positive(), LT10())
    assert c(5)
    assert not c(0)
    assert not c(10)
    schema = JsonSchema()
    c.annotate(schema)
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
    c.annotate(schema)
    assert cast(dict, schema) == {'format': 'positive'}


def test_AnyOf():
    class Negative(Constraint):
        def emit(self):
            return '(x < 0)', None

        def annotate(self, schema):
            schema.format = 'negative'

    class GT10(Constraint):
        def emit(self):
            return '(x > 10)'

        def annotate(self, schema):
            schema.format = 'gt10'

    c = AnyOf(Negative(), GT10())
    assert c(-1)
    assert c(11)
    assert not c(5)
    assert not c(0)
    assert not c(10)
    schema = JsonSchema()
    c.annotate(schema)
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
    c.annotate(schema)
    assert cast(dict, schema) == {'format': 'negative'}


def test_NoneOf():
    class Negative(Constraint):
        def emit(self):
            return '(x < 0)'

        def annotate(self, schema):
            schema.format = 'negative'

    class GT10(Constraint):
        def emit(self):
            return '(x > 10)', None

        def annotate(self, schema):
            schema.format = 'gt10'

    c = NoneOf(Negative(), GT10())
    assert not c(-1)
    assert not c(11)
    assert c(5)
    assert c(0)
    assert c(10)
    schema = JsonSchema()
    c.annotate(schema)
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
    c.annotate(schema)
    assert cast(JsonValue, schema) == {
        'not': {'format': 'negative'}
    }
