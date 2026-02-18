from typing import Literal

import pytest

from typeable import typecast


def test_Literal():
    assert typecast(Literal["2.0", "1.0", 3.0], "2.0") == "2.0"
    assert typecast(Literal["2.0", "1.0", 3.0], "1.0") == "1.0"
    assert typecast(Literal["2.0", "1.0", 3.0], 3.0) == 3.0
    with pytest.raises(TypeError):
        typecast(Literal["2.0", "1.0", 3.0], 4)
