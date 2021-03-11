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
    assert cast(Union[str, int], '123') == '123'
    assert cast(Union[str, int], 123) == 123
    assert cast(Union[str, int], 123.0) == '123.0'

    assert cast(Union[int, str], '123') == '123'
    assert cast(Union[int, str], 123) == 123
    assert cast(Union[int, str], 123.0) == 123


def test_Optional():
    assert cast(Optional[int], 1) == 1
    assert cast(Optional[int], None) == None
