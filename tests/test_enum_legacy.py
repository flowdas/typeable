import sys
from enum import Enum, Flag, IntEnum, IntFlag

import pytest

from typeable import localcontext, typecast


def test_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = "blue"

    # str
    assert typecast(Color, "RED") is Color.RED
    assert typecast(Color, "GREEN") is Color.GREEN
    assert typecast(Color, "BLUE") is Color.BLUE

    # int
    assert typecast(Color, 1) is Color.GREEN
    with pytest.raises(ValueError):
        typecast(Color, 2)

    # None
    assert typecast(Color, None) is Color.RED

    # Enum
    assert typecast(Color, Color.RED) is Color.RED
    assert typecast(Color, Color.GREEN) is Color.GREEN
    assert typecast(Color, Color.BLUE) is Color.BLUE


def test_str_from_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = "blue"

    assert typecast(str, Color.RED) == "RED"
    assert typecast(str, Color.GREEN) == "GREEN"
    assert typecast(str, Color.BLUE) == "BLUE"

    with localcontext(strict_str=False):
        assert typecast(str, Color.RED) == "RED"
        assert typecast(str, Color.GREEN) == "GREEN"
        assert typecast(str, Color.BLUE) == "BLUE"


def test_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert typecast(Shape, 1) is Shape.CIRCLE
    assert typecast(Shape, 2) is Shape.SQUARE
    with pytest.raises(ValueError):
        typecast(Shape, 3)

    # str
    assert typecast(Shape, "CIRCLE") is Shape.CIRCLE
    assert typecast(Shape, "SQUARE") is Shape.SQUARE

    # float
    with pytest.raises(TypeError):
        typecast(Shape, 1.0)

    # None
    with pytest.raises(TypeError):
        typecast(Shape, None)

    # IntEnum
    assert typecast(Shape, Shape.CIRCLE) is Shape.CIRCLE
    assert typecast(Shape, Shape.SQUARE) is Shape.SQUARE

    class Request(IntEnum):
        POST = 1
        GET = 2

    assert typecast(Shape, Request.POST) is Shape.CIRCLE
    assert typecast(Shape, Request.GET) is Shape.SQUARE


def test_int_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert typecast(int, Shape.CIRCLE) == 1
    assert typecast(int, Shape.SQUARE) == 2


def test_str_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert typecast(str, Shape.CIRCLE) == "CIRCLE"
    assert typecast(str, Shape.SQUARE) == "SQUARE"

    with localcontext(strict_str=False):
        assert typecast(str, Shape.CIRCLE) == "CIRCLE"
        assert typecast(str, Shape.SQUARE) == "SQUARE"


#
# Flag
#


def test_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert typecast(Perm, 1) is Perm.X
    assert typecast(Perm, 2) is Perm.W
    assert typecast(Perm, 4) is Perm.R
    assert typecast(Perm, 7) == Perm.R | Perm.W | Perm.X
    with pytest.raises(ValueError):
        typecast(Perm, 8)

    # str
    with pytest.raises(TypeError):
        typecast(Perm, "R")

    # float
    with pytest.raises(TypeError):
        typecast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        typecast(Perm, None)

    # Flag
    assert typecast(Perm, Perm.R) is Perm.R
    assert typecast(Perm, Perm.W) is Perm.W
    assert typecast(Perm, Perm.X) is Perm.X

    class Perm2(Flag):
        R = 4
        W = 2
        X = 1

    if sys.version_info < (3, 11):
        Exc = TypeError
    else:
        Exc = ValueError

    with pytest.raises(Exc):
        typecast(Perm, Perm2.R)


def test_int_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert typecast(int, Perm.R) == 4
    assert typecast(int, Perm.W) == 2
    assert typecast(int, Perm.X) == 1
    assert typecast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        typecast(str, Perm.R)


#
# IntFlag
#


def test_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert typecast(Perm, 1) is Perm.X
    assert typecast(Perm, 2) is Perm.W
    assert typecast(Perm, 4) is Perm.R
    assert typecast(Perm, 7) == Perm.R | Perm.W | Perm.X
    assert typecast(Perm, 8) == Perm(8)

    # str
    with pytest.raises(TypeError):
        typecast(Perm, "R")

    # float
    with pytest.raises(TypeError):
        typecast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        typecast(Perm, None)

    # IntFlag
    assert typecast(Perm, Perm.R) is Perm.R
    assert typecast(Perm, Perm.W) is Perm.W
    assert typecast(Perm, Perm.X) is Perm.X


def test_int_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert typecast(int, Perm.R) == 4
    assert typecast(int, Perm.W) == 2
    assert typecast(int, Perm.X) == 1
    assert typecast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        typecast(str, Perm.R)
