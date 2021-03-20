# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import json

from ._cast import cast, declare
from .typing import Union, Dict, List

with declare('JsonValue') as _:
    JsonValue = Union[float, bool, int, str, None, Dict[str, _], List[_]]


@cast.function
def dump(obj: JsonValue, fp, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dump(obj, fp, ensure_ascii=ensure_ascii, separators=separators, **kw)


@cast.function
def dumps(obj: JsonValue, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators, **kw)
