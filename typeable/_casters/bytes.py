from .._typecast import Typecast, typecast


@typecast.register
def bytes_from_bytearray(deepcast: Typecast, cls: type[bytes], val: bytearray) -> bytes:
    return cls(val)
