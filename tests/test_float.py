from decimal import Decimal
from fractions import Fraction
import math
from typeable import deepcast, localcontext

import pytest


def test_float():
    v = 1 / 3
    assert deepcast(float, v) is v
    assert math.isnan(deepcast(float, float("nan")))
    assert math.isinf(deepcast(float, float("inf")))
    assert math.isinf(deepcast(float, float("-inf")))


def test_str():
    with localcontext(parse_number=True):
        assert deepcast(float, "+123.456") == 123.456
        assert deepcast(float, "1.23456e2") == 123.456
        assert math.isnan(deepcast(float, "nan"))
        assert math.isinf(deepcast(float, "inf"))
        assert math.isinf(deepcast(float, "-inf"))


def test_int():
    assert deepcast(float, 123) == 123


def test_Fraction():
    assert deepcast(float, Fraction(246, 2)) == 123

    with pytest.raises(TypeError):
        deepcast(float, Fraction(1, 3))


def test_Decimal():
    assert deepcast(float, Decimal("123.0")) == 123

    with pytest.raises(TypeError):
        deepcast(float, Decimal("1") / 3)


def test_complex():
    assert deepcast(float, complex(123.0)) == 123

    with pytest.raises(TypeError):
        deepcast(float, complex(123.456, 1))


def test_bool():
    with pytest.raises(TypeError):
        deepcast(float, True)
