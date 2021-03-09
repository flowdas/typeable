# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest

from typeable.typing import (
    Optional,
    Union,
)
from typeable import *


def test_Union():
    data = '123'

    r = cast(Union[str, int], data)
    assert r == '123'

    r = cast(Union[int, str], data)
    assert r == 123


def test_Optional():
    assert cast(Optional[int], 1) == 1
    assert cast(Optional[int], None) == None