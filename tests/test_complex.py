import cmath
from decimal import Decimal
from fractions import Fraction

import pytest

from typeable import localcontext, typecast


def test_complex():
    v = complex(123, 456)
    assert typecast(complex, v) is v


def test_str():
    with localcontext(parse_number=True):
        assert typecast(complex, "123+456j") == complex(123, 456)
        assert typecast(complex, "(123+456j)") == complex(123, 456)
        assert typecast(complex, "1.23456e2") == complex(123.456, 0)
        assert cmath.isnan(typecast(complex, "nan+nanj"))
        assert cmath.isinf(typecast(complex, "inf"))
        assert cmath.isinf(typecast(complex, "-inf"))


def test_bool():
    with pytest.raises(TypeError):
        typecast(complex, True)


def test_int():
    assert typecast(complex, 123) == 123 + 0j


def test_float():
    assert typecast(complex, 123.456) == 123.456 + 0j


def test_Fraction():
    assert typecast(complex, Fraction(246, 2)) == 123 + 0j

    with pytest.raises(TypeError):
        typecast(complex, Fraction(1, 3))


def test_Decimal():
    assert typecast(complex, Decimal("123.0")) == 123 + 0j

    with pytest.raises(TypeError):
        typecast(complex, Decimal("1") / 3)


def test_tuple():
    assert typecast(complex, [123, 456]) == complex(123, 456)
    assert typecast(complex, (123, 456)) == complex(123, 456)

    with pytest.raises(TypeError):
        typecast(complex, [123])
    with pytest.raises(TypeError):
        typecast(complex, [123, 456, 789])


def test_bytes():
    with pytest.raises(TypeError):
        typecast(complex, b"ab")
    with pytest.raises(TypeError):
        typecast(complex, bytearray(b"ab"))
