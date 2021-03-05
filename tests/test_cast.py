# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest

from typeable import *


def test_register():
    with pytest.raises(RuntimeError):
        @cast.register
        def _(cls, val) -> Object:
            return cls(val)


def test_invalid_register():
    with pytest.raises(TypeError):
        @cast.register
        def _():
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls, val):
            pass

    with pytest.raises(TypeError):
        @cast.register
        def _(cls: Object, val) -> Object:
            pass


def test_Object():
    class X(Object):
        i: int

    data = {'i': 0}

    x = cast(X, data)
    assert x.i == data['i']
