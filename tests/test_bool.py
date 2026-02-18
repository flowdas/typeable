import pytest

from typeable import localcontext, typecast


def test_bool():
    assert typecast(bool, False) is False
    assert typecast(bool, True) is True


def test_str():
    assert typecast(bool, "false") is False
    assert typecast(bool, "true") is True
    assert typecast(bool, "fAlSe") is False
    assert typecast(bool, "tRuE") is True
    with pytest.raises(TypeError):
        typecast(bool, "SUCCESS")
    with localcontext(bool_strings={}):
        with pytest.raises(TypeError):
            typecast(bool, "true")


def test_int():
    with localcontext(bool_from_01=True):
        assert typecast(bool, 0) is False
        assert typecast(bool, 1) is True
        with pytest.raises(ValueError):
            typecast(bool, 2)
    with localcontext(bool_from_01=False):
        with pytest.raises(TypeError):
            typecast(bool, 0)


def test_float():
    with pytest.raises(TypeError):
        typecast(bool, 0.0)
    with pytest.raises(TypeError):
        typecast(bool, 1.0)
