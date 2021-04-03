# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typeable.typing import (
    Annotated,
)
from typeable import *


def test_Annotated():
    assert cast(Annotated[int, None], "123") == 123


def test_JsonSchema_from_Annotated():
    assert cast(dict, JsonSchema(Annotated[int, None])) == {'type': 'integer'}
