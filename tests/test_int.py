from decimal import Decimal
from fractions import Fraction

import pytest

from typeable import localcontext, typecast


def test_int():
    v = 123456789
    assert typecast(int, v) is v


def test_bool():
    with pytest.raises(TypeError):
        typecast(int, True)
    with pytest.raises(TypeError):
        typecast(int, False)


def test_str():
    with localcontext(parse_number=True):
        assert typecast(int, "123") == 123

    with localcontext(parse_number=False):
        with pytest.raises(TypeError):
            typecast(int, "123")

    with localcontext(parse_number=True):
        assert typecast(int, "123.0") == 123
        with pytest.raises(TypeError):
            typecast(int, "123.456")

    with localcontext(parse_number=False):
        with pytest.raises(TypeError):
            typecast(int, "123.0")


def test_float():
    assert typecast(int, 123.0) == 123

    with pytest.raises(TypeError):
        typecast(int, 123.456)


def test_Fraction():
    assert typecast(int, Fraction(246, 2)) == 123

    with pytest.raises(TypeError):
        typecast(int, Fraction(246, 5))


def test_Decimal():
    assert typecast(int, Decimal("123.0")) == 123

    with pytest.raises(TypeError):
        typecast(int, Decimal("123.456"))


def test_complex():
    assert typecast(int, complex(123.0)) == 123

    with pytest.raises(TypeError):
        typecast(int, complex(123.456))
