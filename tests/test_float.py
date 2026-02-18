import math
from decimal import Decimal
from fractions import Fraction

import pytest

from typeable import localcontext, typecast


def test_float():
    v = 1 / 3
    assert typecast(float, v) is v
    assert math.isnan(typecast(float, float("nan")))
    assert math.isinf(typecast(float, float("inf")))
    assert math.isinf(typecast(float, float("-inf")))


def test_str():
    with localcontext(parse_number=True):
        assert typecast(float, "+123.456") == 123.456
        assert typecast(float, "1.23456e2") == 123.456
        assert math.isnan(typecast(float, "nan"))
        assert math.isinf(typecast(float, "inf"))
        assert math.isinf(typecast(float, "-inf"))


def test_int():
    assert typecast(float, 123) == 123


def test_Fraction():
    assert typecast(float, Fraction(246, 2)) == 123

    with pytest.raises(TypeError):
        typecast(float, Fraction(1, 3))


def test_Decimal():
    assert typecast(float, Decimal("123.0")) == 123

    with pytest.raises(TypeError):
        typecast(float, Decimal("1") / 3)


def test_complex():
    assert typecast(float, complex(123.0)) == 123

    with pytest.raises(TypeError):
        typecast(float, complex(123.456, 1))


def test_bool():
    with pytest.raises(TypeError):
        typecast(float, True)
