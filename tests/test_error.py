# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import (
    Dict,
    List,
)

import pytest

from typeable import deepcast, capture


def test_capture():
    class T:
        pass

    @deepcast.register
    def _(cls, val, ctx) -> T:
        raise NotImplementedError

    with pytest.raises(NotImplementedError):
        with capture() as error:
            deepcast(T, 1)
    assert error.location == ()
    assert error.exc_info is not None
    exc_type, _, _ = error.exc_info
    assert exc_type is NotImplementedError

    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(List[int], [0, None])
    assert error.location == (1,)

    with pytest.raises(NotImplementedError):
        with capture() as error:
            deepcast(Dict[T, List[int]], {None: [0, None]})
    assert error.location == (None,)

    t = T()
    with pytest.raises(TypeError):
        with capture() as error:
            deepcast(Dict[T, List[int]], {t: [0, None]})
    assert error.location == (t, 1)
