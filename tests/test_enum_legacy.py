from enum import IntEnum, Enum, IntFlag, Flag
import sys

import pytest

from typeable import deepcast, localcontext


def test_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = "blue"

    # str
    assert deepcast(Color, "RED") is Color.RED
    assert deepcast(Color, "GREEN") is Color.GREEN
    assert deepcast(Color, "BLUE") is Color.BLUE

    # int
    assert deepcast(Color, 1) is Color.GREEN
    with pytest.raises(ValueError):
        deepcast(Color, 2)

    # None
    assert deepcast(Color, None) is Color.RED

    # Enum
    assert deepcast(Color, Color.RED) is Color.RED
    assert deepcast(Color, Color.GREEN) is Color.GREEN
    assert deepcast(Color, Color.BLUE) is Color.BLUE


def test_str_from_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = "blue"

    assert deepcast(str, Color.RED) == "RED"
    assert deepcast(str, Color.GREEN) == "GREEN"
    assert deepcast(str, Color.BLUE) == "BLUE"

    with localcontext(strict_str=False):
        assert deepcast(str, Color.RED) == "RED"
        assert deepcast(str, Color.GREEN) == "GREEN"
        assert deepcast(str, Color.BLUE) == "BLUE"


def test_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert deepcast(Shape, 1) is Shape.CIRCLE
    assert deepcast(Shape, 2) is Shape.SQUARE
    with pytest.raises(ValueError):
        deepcast(Shape, 3)

    # str
    assert deepcast(Shape, "CIRCLE") is Shape.CIRCLE
    assert deepcast(Shape, "SQUARE") is Shape.SQUARE

    # float
    with pytest.raises(TypeError):
        deepcast(Shape, 1.0)

    # None
    with pytest.raises(TypeError):
        deepcast(Shape, None)

    # IntEnum
    assert deepcast(Shape, Shape.CIRCLE) is Shape.CIRCLE
    assert deepcast(Shape, Shape.SQUARE) is Shape.SQUARE

    class Request(IntEnum):
        POST = 1
        GET = 2

    assert deepcast(Shape, Request.POST) is Shape.CIRCLE
    assert deepcast(Shape, Request.GET) is Shape.SQUARE


def test_int_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert deepcast(int, Shape.CIRCLE) == 1
    assert deepcast(int, Shape.SQUARE) == 2


def test_str_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert deepcast(str, Shape.CIRCLE) == "CIRCLE"
    assert deepcast(str, Shape.SQUARE) == "SQUARE"

    with localcontext(strict_str=False):
        assert deepcast(str, Shape.CIRCLE) == "CIRCLE"
        assert deepcast(str, Shape.SQUARE) == "SQUARE"


#
# Flag
#


def test_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert deepcast(Perm, 1) is Perm.X
    assert deepcast(Perm, 2) is Perm.W
    assert deepcast(Perm, 4) is Perm.R
    assert deepcast(Perm, 7) == Perm.R | Perm.W | Perm.X
    with pytest.raises(ValueError):
        deepcast(Perm, 8)

    # str
    with pytest.raises(TypeError):
        deepcast(Perm, "R")

    # float
    with pytest.raises(TypeError):
        deepcast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        deepcast(Perm, None)

    # Flag
    assert deepcast(Perm, Perm.R) is Perm.R
    assert deepcast(Perm, Perm.W) is Perm.W
    assert deepcast(Perm, Perm.X) is Perm.X

    class Perm2(Flag):
        R = 4
        W = 2
        X = 1

    if sys.version_info < (3, 11):
        Exc = TypeError
    else:
        Exc = ValueError

    with pytest.raises(Exc):
        deepcast(Perm, Perm2.R)


def test_int_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert deepcast(int, Perm.R) == 4
    assert deepcast(int, Perm.W) == 2
    assert deepcast(int, Perm.X) == 1
    assert deepcast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        deepcast(str, Perm.R)


#
# IntFlag
#


def test_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert deepcast(Perm, 1) is Perm.X
    assert deepcast(Perm, 2) is Perm.W
    assert deepcast(Perm, 4) is Perm.R
    assert deepcast(Perm, 7) == Perm.R | Perm.W | Perm.X
    assert deepcast(Perm, 8) == Perm(8)

    # str
    with pytest.raises(TypeError):
        deepcast(Perm, "R")

    # float
    with pytest.raises(TypeError):
        deepcast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        deepcast(Perm, None)

    # IntFlag
    assert deepcast(Perm, Perm.R) is Perm.R
    assert deepcast(Perm, Perm.W) is Perm.W
    assert deepcast(Perm, Perm.X) is Perm.X


def test_int_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert deepcast(int, Perm.R) == 4
    assert deepcast(int, Perm.W) == 2
    assert deepcast(int, Perm.X) == 1
    assert deepcast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        deepcast(str, Perm.R)
