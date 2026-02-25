from enum import IntFlag

import pytest

from typeable import typecast


class Perm(IntFlag):
    R = 4
    W = 2
    X = 1


def test_value():
    assert typecast(Perm, 1) is Perm.X
    assert typecast(Perm, 2) is Perm.W
    assert typecast(Perm, 4) is Perm.R
    assert typecast(Perm, 7) == Perm.R | Perm.W | Perm.X
    assert typecast(Perm, 8) == Perm(8)


def test_name():
    with pytest.raises(TypeError):
        typecast(Perm, "R")


def test_float():
    with pytest.raises(TypeError):
        typecast(Perm, 1.0)


def test_None():
    with pytest.raises(TypeError):
        typecast(Perm, None)


def test_IntFlag():
    assert typecast(Perm, Perm.R) is Perm.R
    assert typecast(Perm, Perm.W) is Perm.W
    assert typecast(Perm, Perm.X) is Perm.X
