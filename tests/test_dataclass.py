# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from dataclasses import *

import pytest

from typeable import cast, JsonValue


def test_cast():
    @dataclass
    class X:
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert isinstance(x, X)
    assert x.i == data['i']


def test_required():
    @dataclass
    class X:
        a: int
        b: int = 2

    data = {'a': 1}
    x = cast(X, data)
    assert x.a == 1
    assert x.b == 2

    data = {'b': 1}
    with pytest.raises(TypeError):
        cast(X, data)


def test_dict():
    @dataclass
    class X:
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert cast(dict, x) == data


def test_JsonValue():
    @dataclass
    class X:
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert cast(JsonValue, x) == data

    assert cast(JsonValue, {'result': X(**data)}) == {'result': data}

