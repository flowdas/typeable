# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import (
    Dict,
    get_type_hints,
)


class Context:
    # default policies
    bool_is_int: bool = True
    bool_strings: Dict[str, bool] = {
        "0": False,
        "1": True,
        "f": False,
        "false": False,
        "n": False,
        "no": False,
        "off": False,
        "on": True,
        "t": True,
        "true": True,
        "y": True,
        "yes": True,
    }
    bytes_encoding: str = "utf-8"
    date_format: str = "iso"
    datetime_format: str = "iso"
    encoding_errors: str = "strict"
    lossy_conversion: bool = True
    naive_timestamp: bool = False
    strict_str: bool = True
    time_format: str = "iso"
    union_prefers_same_type: bool = True
    union_prefers_base_type: bool = True
    union_prefers_super_type: bool = True
    union_prefers_nearest_type: bool = True

    def __init__(self, **policies):
        self._stack = None
        if policies:
            from ._deepcast import deepcast  # avoid partial import

            hints = get_type_hints(self.__class__)
            ctx = Context()
            for key, val in policies.items():
                try:
                    cls = hints[key]
                except KeyError:
                    raise TypeError(
                        f"{self.__class__.__qualname__}() got an unexpected keyword argument '{key}'"
                    )
                setattr(self, key, deepcast(cls, val, ctx=ctx))
