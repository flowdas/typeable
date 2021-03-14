from enum import IntEnum

from typeable import *

import pytest


def test_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert cast(Shape, 1) is Shape.CIRCLE
    assert cast(Shape, 2) is Shape.SQUARE
    with pytest.raises(ValueError):
        cast(Shape, 3)

    assert cast(int, Shape.CIRCLE) == 1
    assert cast(int, Shape.SQUARE) == 2

    # float
    with pytest.raises(ValueError):
        cast(Shape, 1.1)
    assert cast(Shape, 2.0) is Shape.SQUARE

    # str
    with pytest.raises(ValueError):
        cast(Shape, '1')

    # None
    with pytest.raises(ValueError):
        cast(Shape, None)

    # EnumInt
    assert cast(Shape, Shape.CIRCLE) is Shape.CIRCLE
    assert cast(Shape, Shape.SQUARE) is Shape.SQUARE

    class Request(IntEnum):
        POST = 1
        GET = 2

    assert cast(Shape, Request.POST) is Shape.CIRCLE
    assert cast(Shape, Request.GET) is Shape.SQUARE
