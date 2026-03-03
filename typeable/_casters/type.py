from importlib import import_module
from typing import Any

from .._typecast import Typecast, typecast


def import_fqn(val: str) -> Any:
    spec = val.rsplit(".", maxsplit=1)
    if len(spec) == 1:
        modname = "builtins"
        parts = spec
    else:
        modname = spec[0]
        parts = [spec[1]]
    if not (modname and parts[0]):
        raise TypeError
    while True:
        try:
            mod = import_module(modname)
            break
        except ModuleNotFoundError:
            spec = modname.rsplit(".", maxsplit=1)
            if len(spec) <= 1:
                raise
            modname = spec[0]
            parts.append(spec[1])
            continue
    cls = mod
    for part in reversed(parts):
        cls = getattr(cls, part)
    return cls


@typecast.register
def type_from_str(typecast: Typecast, cls, val: str, T=None) -> type:
    klass = import_fqn(val)
    if not isinstance(klass, type):
        raise TypeError
    if T and T is not Any and not issubclass(klass, T):
        raise TypeError
    return klass
