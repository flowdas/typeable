# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# typing polyfill
#
from typing import *

import sys
import typing

if sys.version_info < (3, 8):  # pragma: no cover
    import collections.abc

    if hasattr(typing, '_GenericAlias'):
        # 3.7
        generic_types = typing._GenericAlias

        def get_origin(tp):
            if isinstance(tp, generic_types):
                return tp.__origin__
            if tp is Generic:
                return tp
            return None

    else:
        # 3.6
        generic_types = (typing.GenericMeta, typing._Union,
                         typing._Optional, typing._ClassVar)

        _origin_map = {
            Dict: dict,
            List: list,
            Type: type,
        }

        def get_origin(tp):
            if isinstance(tp, generic_types):
                if tp.__origin__:
                    return _origin_map.get(tp.__origin__, tp.__origin__)
                else:
                    return _origin_map.get(tp)
            return None

    def get_args(tp):
        if isinstance(tp, generic_types):
            res = tp.__args__
            if get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
                res = (list(res[:-1]), res[-1])
            if res and isinstance(res[0], TypeVar):
                res = ()
            return res or ()
        return ()
