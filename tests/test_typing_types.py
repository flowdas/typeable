# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from datetime import date
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import pytest

from typeable import *


def test_Any():
    assert deepcast(Any, None) is None
    o = object()
    assert deepcast(Any, o) is o

    assert deepcast(List[Any], [None, o]) == [None, o]


def test_Union():
    assert deepcast(Union[str, int], "123") == "123"
    assert deepcast(Union[str, int], 123) == 123
    assert deepcast(Union[str, int], 123.0) == "123.0"

    assert deepcast(Union[int, str], "123") == "123"
    assert deepcast(Union[int, str], 123) == 123
    assert deepcast(Union[int, str], 123.0) == 123


def test_recursive_Union():
    with declare("Json") as _Json:
        Json = Union[
            float,
            bool,
            int,
            str,
            None,
            Dict[str, _Json],
            List[_Json],
            Tuple[_Json, ...],
        ]

    assert deepcast(Json, 1) == 1
    assert deepcast(Json, 1.0) == 1.0
    assert deepcast(Json, "1") == "1"
    assert deepcast(Json, True) is True
    assert deepcast(Json, None) is None
    assert deepcast(Json, {}) == {}
    assert deepcast(Json, []) == []
    assert deepcast(Json, ()) == ()
    assert deepcast(Json, {"k1": 1}) == {"k1": 1}

    assert deepcast(Json, [date(1970, 1, 1)]) == ["1970-01-01"]


def test_distance_based_Union():
    ctx = Context()
    ctx.union_prefers_same_type = False
    ctx.union_prefers_base_type = False
    ctx.union_prefers_super_type = False
    ctx.union_prefers_nearest_type = False

    # union_prefers_same_type
    assert deepcast(Union[float, int, bool], True) is True
    assert deepcast(Union[float, int, bool], True, ctx=ctx) is not True
    ctx.union_prefers_same_type = True
    assert deepcast(Union[float, int, bool], True, ctx=ctx) is True
    ctx.union_prefers_same_type = False

    # union_prefers_base_type
    x = deepcast(Union[str, int], True)
    assert x == 1
    assert type(x) is bool
    assert deepcast(Union[str, int], True, ctx=ctx) == "True"
    ctx.union_prefers_base_type = True
    x = deepcast(Union[str, int], True, ctx=ctx)
    assert x == 1
    assert type(x) is bool
    ctx.union_prefers_base_type = False

    # union_prefers_super_type
    assert deepcast(Union[str, bool], 1) is True
    assert deepcast(Union[str, bool], 1, ctx=ctx) == "1"
    ctx.union_prefers_super_type = True
    assert deepcast(Union[str, bool], 1, ctx=ctx) is True
    ctx.union_prefers_super_type = False

    # union_prefers_nearest_type
    ctx.union_prefers_nearest_type = True
    assert deepcast(Union[str, bool], 1, ctx=ctx) is True
    assert deepcast(Union[str, bool], True, ctx=ctx) is True
    assert deepcast(Union[str, bool], "true", ctx=ctx) == "true"
    # bool has str specialization
    assert deepcast(Union[bool, str], "true", ctx=ctx) is True
    # bool conversion failure
    assert deepcast(Union[bool, str], "XXX", ctx=ctx) == "XXX"
    ctx.union_prefers_nearest_type = False

    # no preference, sequential
    assert deepcast(Union[str, bool], 1, ctx=ctx) == "1"
    assert deepcast(Union[bool, str], 1, ctx=ctx) is True

    # no match
    with pytest.raises(TypeError):
        deepcast(Union[int, float], None)


def test_Optional():
    assert deepcast(Optional[int], 1) == 1
    assert deepcast(Optional[int], None) == None


def test_Literal():
    assert deepcast(Literal["2.0", "1.0", 3.0], "2.0") == "2.0"
    assert deepcast(Literal["2.0", "1.0", 3.0], "1.0") == "1.0"
    assert deepcast(Literal["2.0", "1.0", 3.0], 3.0) == 3.0
    with pytest.raises(TypeError):
        deepcast(Literal["2.0", "1.0", 3.0], 4)
