from .._deepcast import DeepCast, deepcast


@deepcast.register
def bytearray_from_bytes(
    deepcast: DeepCast, cls: type[bytearray], val: bytes
) -> bytearray:
    return cls(val)
