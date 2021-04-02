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
)


def test_policies():
    class MyContext(Context):
        test_option: int = 0

    ctx = MyContext()
    assert ctx.bool_is_int is True
    assert ctx.bytes_encoding == 'utf-8'
    assert ctx.test_option == 0

    ctx = MyContext(bool_is_int=False)
    assert ctx.bool_is_int is False
    assert ctx.bytes_encoding == 'utf-8'
    assert ctx.test_option == 0

    ctx = MyContext(bytes_encoding='ascii')
    assert ctx.bool_is_int is True
    assert ctx.bytes_encoding == 'ascii'
    assert ctx.test_option == 0

    ctx = MyContext(test_option=1)
    assert ctx.bool_is_int is True
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

    assert ctx._stack is None
    try:
        with ctx.capture() as error:
            assert ctx._stack is not None
            cast(T, 1, ctx=ctx)
    except:
        pass
    assert error.location == ()

    with pytest.raises(TypeError):
        with ctx.capture() as error:
            cast(List[int], [0, None], ctx=ctx)
    assert error.location == (1,)

    with pytest.raises(NotImplementedError):
        with ctx.capture() as error:
            cast(Dict[T, List[int]], {None: [0, None]}, ctx=ctx)
    assert error.location == (None,)

    t = T()
    with pytest.raises(TypeError):
        with ctx.capture() as error:
            cast(Dict[T, List[int]], {t: [0, None]}, ctx=ctx)
    assert error.location == (t, 1)
