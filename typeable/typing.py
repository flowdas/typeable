#
# typing polyfill
#
from typing import *

import sys
import typing

if sys.version_info < (3, 8):  # pragma: no cover

    def get_origin(tp):
        if isinstance(tp, typing._GenericAlias):
            return tp.__origin__
        if tp is Generic:
            return tp
        return None

    def get_args(tp):
        if isinstance(tp, typing._GenericAlias):
            res = tp.__args__
            if get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
                res = (list(res[:-1]), res[-1])
            return res
        return ()
