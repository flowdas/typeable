import cmath
from decimal import Decimal
from fractions import Fraction

from typeable import deepcast, localcontext

import pytest


def test_complex():
    v = complex(123, 456)
    assert deepcast(complex, v) is v


def test_str():
    with localcontext(parse_number=True):
        assert deepcast(complex, "123+456j") == complex(123, 456)
        assert deepcast(complex, "(123+456j)") == complex(123, 456)
        assert deepcast(complex, "1.23456e2") == complex(123.456, 0)
        assert cmath.isnan(deepcast(complex, "nan+nanj"))
        assert cmath.isinf(deepcast(complex, "inf"))
        assert cmath.isinf(deepcast(complex, "-inf"))


def test_bool():
    with pytest.raises(TypeError):
        deepcast(complex, True)


def test_int():
    assert deepcast(complex, 123) == 123 + 0j


def test_float():
    assert deepcast(complex, 123.456) == 123.456 + 0j


def test_Fraction():
    assert deepcast(complex, Fraction(246, 2)) == 123 + 0j

    with pytest.raises(TypeError):
        deepcast(complex, Fraction(1, 3))


def test_Decimal():
    assert deepcast(complex, Decimal("123.0")) == 123 + 0j

    with pytest.raises(TypeError):
        deepcast(complex, Decimal("1") / 3)


def test_tuple():
    assert deepcast(complex, [123, 456]) == complex(123, 456)
    assert deepcast(complex, (123, 456)) == complex(123, 456)

    with pytest.raises(TypeError):
        deepcast(complex, [123])
    with pytest.raises(TypeError):
        deepcast(complex, [123, 456, 789])


def test_bytes():
    with pytest.raises(TypeError):
        deepcast(complex, b"ab")
    with pytest.raises(TypeError):
        deepcast(complex, bytearray(b"ab"))
