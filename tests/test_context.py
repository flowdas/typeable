# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest

from typeable import *
from typeable.typing import (
    Dict,
    List,
    Type,
    get_args,
    get_origin,
)


def test_policies():
    class MyContext(Context):
        test_option: int = 0

    ctx = MyContext()
    assert ctx.missing_is_null is False
    assert ctx.bytes_encoding == 'utf-8'
    assert ctx.test_option == 0

    ctx = MyContext(missing_is_null=True)
    assert ctx.missing_is_null is True
    assert ctx.bytes_encoding == 'utf-8'
    assert ctx.test_option == 0

    ctx = MyContext(bytes_encoding='ascii')
    assert ctx.missing_is_null is False
    assert ctx.bytes_encoding == 'ascii'
    assert ctx.test_option == 0

    ctx = MyContext(test_option=1)
    assert ctx.missing_is_null is False
    assert ctx.bytes_encoding == 'utf-8'
    assert ctx.test_option == 1

    with pytest.raises(TypeError):
        MyContext(test_option=None)

    with pytest.raises(TypeError):
        MyContext(traverse=lambda: 0)

    with pytest.raises(TypeError):
        MyContext(unknown_option=0)


def test_capture():
    class T:
        pass

    @cast.register
    def _(cls, val, ctx) -> T:
        raise NotImplementedError

    ctx = Context()
    with pytest.raises(NotImplementedError):
        with ctx.capture() as error:
            cast(T, 1, ctx=ctx)
    assert error.location == ()
    exc_type, exc_val, traceback = error.exc_info
    assert exc_type == NotImplementedError

    with pytest.raises(TypeError):
        with ctx.capture() as error:
            cast(List[int], [0, None], ctx=ctx)
    assert error.location == (1,)

    with pytest.raises(TypeError):
        with ctx.capture() as error:
            cast(Dict[T, List[int]], {None: [0, None]}, ctx=ctx)
    assert error.location == (None, 1)
