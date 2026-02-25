from enum import Enum

import pytest

from typeable import typecast


class Color(Enum):
    RED = None
    GREEN = 1
    BLUE = "blu"


def test_value():
    assert typecast(Color, None) is Color.RED
    assert typecast(Color, 1) is Color.GREEN
    assert typecast(Color, "blu") is Color.BLUE

    with pytest.raises(TypeError):
        typecast(Color, 2)
    with pytest.raises(TypeError):
        typecast(Color, "")


def test_Enum():
    assert typecast(Color, Color.RED) is Color.RED
    assert typecast(Color, Color.GREEN) is Color.GREEN
    assert typecast(Color, Color.BLUE) is Color.BLUE


def test_name():
    with pytest.raises(TypeError):
        typecast(Color, "RED")
