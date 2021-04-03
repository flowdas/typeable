# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
    return cast(T, val, ctx=ctx)


@JsonSchema.register(Annotated)
def _jsonschema_Annotated(self, cls: Type[Annotated], T, *args):
    this = JsonSchema(T)
    for k, v in this.__dict__.items():
        setattr(self, k, v)
