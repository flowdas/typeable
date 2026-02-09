from types import NoneType

import pytest

from typeable import deepcast


def test_NoneType():
    """NoneType 은 오직 None 만 받아들인다."""
    assert deepcast(NoneType, None) is None

    with pytest.raises(TypeError):
        deepcast(NoneType, object())


def test_None():
    """None 은 타입으로 직접 사용할 수 없다."""

    with pytest.raises(TypeError):
        deepcast(None, None)  # type: ignore
