from enum import IntEnum, Enum, IntFlag, Flag
import sys

from typeable import *

import pytest


def test_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = 'blue'

    # str
    assert cast(Color, 'RED') is Color.RED
    assert cast(Color, 'GREEN') is Color.GREEN
    assert cast(Color, 'BLUE') is Color.BLUE

    # int
    assert cast(Color, 1) is Color.GREEN
    with pytest.raises(ValueError):
        cast(Color, 2)

    # None
    assert cast(Color, None) is Color.RED

    # Enum
    assert cast(Color, Color.RED) is Color.RED
    assert cast(Color, Color.GREEN) is Color.GREEN
    assert cast(Color, Color.BLUE) is Color.BLUE


def test_str_from_Enum():
    class Color(Enum):
        RED = None
        GREEN = 1
        BLUE = 'blue'

    assert cast(str, Color.RED) == 'RED'
    assert cast(str, Color.GREEN) == 'GREEN'
    assert cast(str, Color.BLUE) == 'BLUE'

    ctx = Context(strict_str=False)

    assert cast(str, Color.RED, ctx=ctx) == 'RED'
    assert cast(str, Color.GREEN, ctx=ctx) == 'GREEN'
    assert cast(str, Color.BLUE, ctx=ctx) == 'BLUE'


def test_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert cast(Shape, 1) is Shape.CIRCLE
    assert cast(Shape, 2) is Shape.SQUARE
    with pytest.raises(ValueError):
        cast(Shape, 3)

    # str
    assert cast(Shape, 'CIRCLE') is Shape.CIRCLE
    assert cast(Shape, 'SQUARE') is Shape.SQUARE

    # float
    with pytest.raises(TypeError):
        cast(Shape, 1.0)

    # None
    with pytest.raises(TypeError):
        cast(Shape, None)

    # IntEnum
    assert cast(Shape, Shape.CIRCLE) is Shape.CIRCLE
    assert cast(Shape, Shape.SQUARE) is Shape.SQUARE

    class Request(IntEnum):
        POST = 1
        GET = 2

    assert cast(Shape, Request.POST) is Shape.CIRCLE
    assert cast(Shape, Request.GET) is Shape.SQUARE


def test_int_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert cast(int, Shape.CIRCLE) == 1
    assert cast(int, Shape.SQUARE) == 2


def test_str_from_IntEnum():
    class Shape(IntEnum):
        CIRCLE = 1
        SQUARE = 2

    assert cast(str, Shape.CIRCLE) == 'CIRCLE'
    assert cast(str, Shape.SQUARE) == 'SQUARE'

    ctx = Context(strict_str=False)

    assert cast(str, Shape.CIRCLE, ctx=ctx) == 'CIRCLE'
    assert cast(str, Shape.SQUARE, ctx=ctx) == 'SQUARE'


#
# Flag
#


def test_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert cast(Perm, 1) is Perm.X
    assert cast(Perm, 2) is Perm.W
    assert cast(Perm, 4) is Perm.R
    assert cast(Perm, 7) == Perm.R | Perm.W | Perm.X
    with pytest.raises(ValueError):
        cast(Perm, 8)

    # str
    with pytest.raises(TypeError):
        cast(Perm, 'R')

    # float
    with pytest.raises(TypeError):
        cast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        cast(Perm, None)

    # Flag
    assert cast(Perm, Perm.R) is Perm.R
    assert cast(Perm, Perm.W) is Perm.W
    assert cast(Perm, Perm.X) is Perm.X

    class Perm2(Flag):
        R = 4
        W = 2
        X = 1

    if sys.version_info < (3, 11):
        Exc = TypeError
    else:
        Exc = ValueError

    with pytest.raises(Exc):
        cast(Perm, Perm2.R)


def test_int_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    assert cast(int, Perm.R) == 4
    assert cast(int, Perm.W) == 2
    assert cast(int, Perm.X) == 1
    assert cast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_Flag():
    class Perm(Flag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        cast(str, Perm.R)


#
# IntFlag
#


def test_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert cast(Perm, 1) is Perm.X
    assert cast(Perm, 2) is Perm.W
    assert cast(Perm, 4) is Perm.R
    assert cast(Perm, 7) == Perm.R | Perm.W | Perm.X
    assert cast(Perm, 8) == Perm(8)

    # str
    with pytest.raises(TypeError):
        cast(Perm, 'R')

    # float
    with pytest.raises(TypeError):
        cast(Perm, 1.0)

    # None
    with pytest.raises(TypeError):
        cast(Perm, None)

    # IntFlag
    assert cast(Perm, Perm.R) is Perm.R
    assert cast(Perm, Perm.W) is Perm.W
    assert cast(Perm, Perm.X) is Perm.X


def test_int_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    assert cast(int, Perm.R) == 4
    assert cast(int, Perm.W) == 2
    assert cast(int, Perm.X) == 1
    assert cast(int, Perm.R | Perm.W | Perm.X) == 7


def test_str_from_IntFlag():
    class Perm(IntFlag):
        R = 4
        W = 2
        X = 1

    with pytest.raises(TypeError):
        cast(str, Perm.R)
