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
