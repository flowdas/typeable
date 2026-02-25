from enum import IntEnum

import pytest

from typeable import typecast


class Shape(IntEnum):
    CIRCLE = 1
    SQUARE = 2


class Request(IntEnum):
    POST = 1
    GET = 2


def test_value():
    assert typecast(Shape, 1) is Shape.CIRCLE
    assert typecast(Shape, 2) is Shape.SQUARE
    with pytest.raises(TypeError):
        typecast(Shape, 3)


def test_name():
    with pytest.raises(TypeError):
        typecast(Shape, "CIRCLE")


def test_float():
    with pytest.raises(TypeError):
        typecast(Shape, 1.0)


def test_None():
    with pytest.raises(TypeError):
        typecast(Shape, None)


def test_IntEnum():
    assert typecast(Shape, Shape.CIRCLE) is Shape.CIRCLE
    assert typecast(Shape, Shape.SQUARE) is Shape.SQUARE

    assert typecast(Shape, Request.POST) is Shape.CIRCLE
    assert typecast(Shape, Request.GET) is Shape.SQUARE
