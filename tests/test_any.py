from typing import Any

from typeable import deepcast


def test_Any():
    assert deepcast(Any, None) is None
    o = object()
    assert deepcast(Any, o) is o

    assert deepcast(list[Any], [None, o]) == [None, o]
