import json

from .cast import cast, declare
from .typing import Union, Dict, List

__all__ = [
    'JsonValue',
    'dump',
    'dumps',
]

with declare('JsonValue') as _:
    JsonValue = Union[float, bool, int, str, None, Dict[str, _], List[_]]


@cast.function
def dump(obj: JsonValue, fp, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dump(obj, fp, ensure_ascii=ensure_ascii, separators=separators, **kw)


@cast.function
def dumps(obj: JsonValue, *, ensure_ascii=False, separators=(',', ':'), **kw):
    return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators, **kw)
