from .._typecast import Typecast, typecast


@typecast.register
def bytearray_from_bytes(
    typecast: Typecast, cls: type[bytearray], val: bytes
) -> bytearray:
    return cls(val)
