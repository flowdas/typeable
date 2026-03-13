from .._constraint import _type_from_str
from .._typecast import Typecast, typecast


@typecast.register
def type_from_str(typecast: Typecast, cls, val: str, T=None) -> type:
    return _type_from_str(val, T)
