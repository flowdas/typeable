from typeable import deepcast, localcontext

import pytest


def test_bool():
    assert deepcast(bool, False) is False
    assert deepcast(bool, True) is True


def test_str():
    assert deepcast(bool, "false") is False
    assert deepcast(bool, "true") is True
    assert deepcast(bool, "fAlSe") is False
    assert deepcast(bool, "tRuE") is True
    with pytest.raises(TypeError):
        deepcast(bool, "SUCCESS")
    with localcontext(bool_strings={}):
        with pytest.raises(TypeError):
            deepcast(bool, "true")


def test_int():
    with localcontext(bool_from_01=True):
        assert deepcast(bool, 0) is False
        assert deepcast(bool, 1) is True
        with pytest.raises(ValueError):
            deepcast(bool, 2)
    with localcontext(bool_from_01=False):
        with pytest.raises(TypeError):
            deepcast(bool, 0)


def test_float():
    with pytest.raises(TypeError):
        deepcast(bool, 0.0)
    with pytest.raises(TypeError):
        deepcast(bool, 1.0)
