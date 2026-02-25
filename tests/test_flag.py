from enum import Flag

import pytest

from typeable import typecast


class Perm(Flag):
    R = 4
    W = 2
    X = 1


class Perm2(Flag):
    R = 4
    W = 2
    X = 1


def test_value():
    assert typecast(Perm, 1) is Perm.X
    assert typecast(Perm, 2) is Perm.W
    assert typecast(Perm, 4) is Perm.R
    assert typecast(Perm, 7) == Perm.R | Perm.W | Perm.X
    with pytest.raises(TypeError):
        typecast(Perm, 8)


def test_name():
    with pytest.raises(TypeError):
        typecast(Perm, "R")


def test_None():
    with pytest.raises(TypeError):
        typecast(Perm, None)


def test_Flag():
    assert typecast(Perm, Perm.R) is Perm.R
    assert typecast(Perm, Perm.W) is Perm.W
    assert typecast(Perm, Perm.X) is Perm.X

    with pytest.raises(TypeError):
        typecast(Perm, Perm2.R)
