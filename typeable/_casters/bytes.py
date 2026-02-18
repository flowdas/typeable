from .._typecast import DeepCast, typecast


@typecast.register
def bytes_from_bytearray(deepcast: DeepCast, cls: type[bytes], val: bytearray) -> bytes:
    return cls(val)
