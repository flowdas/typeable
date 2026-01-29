import pytest

from typeable import deepcast


def test_object():
    """isinstance(v, T) == True 일 때 deepcast(T, v) 는 보통 v 를 반환한다."""
    v = object()
    assert deepcast(object, v) is v
