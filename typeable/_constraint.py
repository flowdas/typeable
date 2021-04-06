# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import cmath
import math

from ._cast import cast
from ._json import JsonSchema
from .typing import (
    Annotated,
    Type,
)


#
# Annotated
#


@cast.register
def _cast_Annotated_object(cls: Type[Annotated], val, ctx, T, *args):
    r = cast(T, val, ctx=ctx)
    for arg in args:
        if isinstance(arg, Constraint):
            if not arg(r):
                raise ValueError(f"Constraint {arg!r} failed")
    return r


@JsonSchema.register(Annotated)
def _jsonschema_Annotated(self, cls: Type[Annotated], T, *args):
    this = JsonSchema(T)
    for k, v in this.__dict__.items():
        setattr(self, k, v)
    for arg in args:
        if isinstance(arg, Constraint):
            arg.annotate(self)


#
# Constraint
#

class Constraint:
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __call__(self, x):
        try:
            return self._code(x)
        except AttributeError:
            if hasattr(self, '_code'):
                raise
            code = self.compile()
            return code(x)

    def compile(self):
        code = getattr(self, '_code', None)
        if code is None:
            expr = self.emit()
            if isinstance(expr, tuple):
                expr, ns = expr
            else:
                ns = None
            self._code = code = eval(f"lambda x: {expr}", ns)
        return code

    def emit(self):
        return 'True'

    def annotate(self, schema):
        pass


class _Combined(Constraint):
    def __init__(self, arg, *args):
        self.args = (arg,) + args

    def emit(self):
        if len(self.args) == 1:
            return self.args[0].emit()
        else:
            ns = {}
            exprs = []
            for arg in self.args:
                expr = arg.emit()
                if isinstance(expr, tuple):
                    ns.update(expr[1] or {})
                    expr = expr[0]
                exprs.append(expr)
            expr = '(' + f" {self.OP} ".join(f"({expr})" for expr in exprs) + ')'
            return expr, (ns if ns else None)

    def annotate(self, schema):
        if len(self.args) == 1:
            self.args[0].annotate(schema)
        else:
            schemas = []
            for arg in self.args:
                s = JsonSchema()
                arg.annotate(s)
                schemas.append(s)
            setattr(schema, self.KEYWORD, schemas)


class AllOf(_Combined):
    OP = 'and'
    KEYWORD = 'allOf'


class AnyOf(_Combined):
    OP = 'or'
    KEYWORD = 'anyOf'


class NoneOf(AnyOf):
    def emit(self):
        expr = super().emit()
        if isinstance(expr, tuple):
            expr, ns = expr
        else:
            ns = None
        return f"(not {expr})", ns

    def annotate(self, schema):
        s = JsonSchema()
        super().annotate(s)
        schema.not_ = s


class IsFinite(Constraint):
    def emit(self):
        expr = '((isinstance(x,(float,int)) and math.isfinite(x)) or (isinstance(x,complex) and cmath.isfinite(x)))'
        ns = dict(math=math, cmath=cmath)
        return expr, ns
