# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytest

from typeable.typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
)
from typeable import *
from datetime import datetime, date


def test_Any():
    assert cast(Any, None) is None
    o = object()
    assert cast(Any, o) is o

    assert cast(List[Any], [None, o]) == [None, o]


def test_Union():
    assert cast(Union[str, int], '123') == '123'
    assert cast(Union[str, int], 123) == 123
    assert cast(Union[str, int], 123.0) == '123.0'

    assert cast(Union[int, str], '123') == '123'
    assert cast(Union[int, str], 123) == 123
    assert cast(Union[int, str], 123.0) == 123


def test_recursive_Union():
    with declare('Json') as _Json:
        Json = Union[float, bool, int, str, None,
                     Dict[str, _Json], List[_Json], Tuple[_Json, ...]]

    assert cast(Json, 1) == 1
    assert cast(Json, 1.0) == 1.0
    assert cast(Json, '1') == '1'
    assert cast(Json, True) is True
    assert cast(Json, None) is None
    assert cast(Json, {}) == {}
    assert cast(Json, []) == []
    assert cast(Json, ()) == ()
    assert cast(Json, {"k1": 1}) == {"k1": 1}

    assert cast(Json, [date(1970, 1, 1)]) == ['1970-01-01']


def test_distance_based_Union():
    ctx = Context()
    ctx.union_prefers_same_type = False
    ctx.union_prefers_base_type = False
    ctx.union_prefers_super_type = False
    ctx.union_prefers_nearest_type = False

    # union_prefers_same_type
    assert cast(Union[float, int, bool], True) is True
    assert cast(Union[float, int, bool], True, ctx=ctx) is not True
    ctx.union_prefers_same_type = True
    assert cast(Union[float, int, bool], True, ctx=ctx) is True
    ctx.union_prefers_same_type = False

    # union_prefers_base_type
    x = cast(Union[str, int], True)
    assert x == 1
    assert type(x) is bool
    assert cast(Union[str, int], True, ctx=ctx) == 'True'
    ctx.union_prefers_base_type = True
    x = cast(Union[str, int], True, ctx=ctx)
    assert x == 1
    assert type(x) is bool
    ctx.union_prefers_base_type = False

    # union_prefers_super_type
    assert cast(Union[str, bool], 1) is True
    assert cast(Union[str, bool], 1, ctx=ctx) == '1'
    ctx.union_prefers_super_type = True
    assert cast(Union[str, bool], 1, ctx=ctx) is True
    ctx.union_prefers_super_type = False

    # union_prefers_nearest_type
    ctx.union_prefers_nearest_type = True
    assert cast(Union[str, bool], 1, ctx=ctx) is True
    assert cast(Union[str, bool], True, ctx=ctx) is True
    assert cast(Union[str, bool], 'true', ctx=ctx) == 'true'
    # bool has str specialization
    assert cast(Union[bool, str], 'true', ctx=ctx) is True
    # bool conversion failure
    assert cast(Union[bool, str], 'XXX', ctx=ctx) == 'XXX'
    ctx.union_prefers_nearest_type = False

    # no preference, sequential
    assert cast(Union[str, bool], 1, ctx=ctx) == '1'
    assert cast(Union[bool, str], 1, ctx=ctx) is True

    # no match
    with pytest.raises(TypeError):
        cast(Union[int, float], None)


def test_Optional():
    assert cast(Optional[int], 1) == 1
    assert cast(Optional[int], None) == None


def test_Literal():
    assert cast(Literal['2.0', '1.0', 3.0], '2.0') == '2.0'
    assert cast(Literal['2.0', '1.0', 3.0], '1.0') == '1.0'
    assert cast(Literal['2.0', '1.0', 3.0], 3.0) == 3.0
    with pytest.raises(ValueError):
        cast(Literal['2.0', '1.0', 3.0], 4)
