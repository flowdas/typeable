# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# typing polyfill
#
from typing import *

import typing


_GenericBases = []
for _name in (
    "GenericAlias",
    "_GenericAlias",
    "_SpecialForm",
):
    if hasattr(typing, _name):  # pragma: no cover
        _GenericBases.append(getattr(typing, _name))
if hasattr(Union, "__mro__"):
    _GenericBases.append(Union)
_GenericBases = tuple(_GenericBases)
