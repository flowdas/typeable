from typing import Optional

from typeable import typecast


def test_Optional():
    assert typecast(Optional[int], 1) == 1
    assert typecast(Optional[int], None) is None
