from typing import Optional

from typeable import deepcast


def test_Optional():
    assert deepcast(Optional[int], 1) == 1
    assert deepcast(Optional[int], None) is None
