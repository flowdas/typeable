from typing import Any

from typeable import typecast


def test_Any():
    assert typecast(Any, None) is None
    o = object()
    assert typecast(Any, o) is o

    assert typecast(list[Any], [None, o]) == [None, o]
