from .._typecast import DeepCast, typecast


@typecast.register
def bytearray_from_bytes(
    deepcast: DeepCast, cls: type[bytearray], val: bytes
) -> bytearray:
    return cls(val)
