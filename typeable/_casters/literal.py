from typing import Literal

from .._typecast import Typecast, typecast


@typecast.register
def Literal_from_object(
    typecast: Typecast, cls: type[Literal], val: object, *literals
) -> Literal:  # type: ignore
    for literal in literals:
        if literal == val:
            return literal  # type: ignore
    else:
        raise TypeError(f"One of {literals!r} required, but {val!r} is given")
