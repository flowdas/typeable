from decimal import Decimal
from fractions import Fraction
from typeable import deepcast, localcontext

import pytest


def test_int():
    v = 123456789
    assert deepcast(int, v) is v


def test_bool():
    with pytest.raises(TypeError):
        deepcast(int, True)
    with pytest.raises(TypeError):
        deepcast(int, False)


def test_str():
    with localcontext(parse_int=True):
        assert deepcast(int, "123") == 123

    with localcontext(parse_int=False):
        with pytest.raises(TypeError):
            deepcast(int, "123")

    with localcontext(parse_int=True):
        assert deepcast(int, "123.0") == 123
        with pytest.raises(TypeError):
            deepcast(int, "123.456")

    with localcontext(parse_int=False):
        with pytest.raises(TypeError):
            deepcast(int, "123.0")


def test_float():
    assert deepcast(int, 123.0) == 123

    with pytest.raises(TypeError):
        deepcast(int, 123.456)


def test_Fraction():
    assert deepcast(int, Fraction(246, 2)) == 123

    with pytest.raises(TypeError):
        deepcast(int, Fraction(246, 5))


def test_Decimal():
    assert deepcast(int, Decimal("123.0")) == 123

    with pytest.raises(TypeError):
        deepcast(int, Decimal("123.456"))


def test_complex():
    assert deepcast(int, complex(123.0)) == 123

    with pytest.raises(TypeError):
        deepcast(int, complex(123.456))
