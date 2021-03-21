# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from collections.abc import Mapping
from dataclasses import MISSING
import json

from ._cast import cast, declare
from ._object import Object
from .typing import Union, Dict, List, Tuple, _GenericBases

with declare('JsonValue') as _:
    JsonValue = Union[float, bool, int, str, None, Dict[str, _], List[_], Tuple[_, ...]]


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
    def __init__(self, value_or_type=MISSING, *, ctx=None):
        if value_or_type is MISSING or _istype(value_or_type):
            super().__init__(ctx=ctx)
        else:
            super().__init__(value_or_type, ctx=ctx)
