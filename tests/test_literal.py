from typing import Literal

from typeable import deepcast

import pytest


def test_Literal():
    assert deepcast(Literal["2.0", "1.0", 3.0], "2.0") == "2.0"
    assert deepcast(Literal["2.0", "1.0", 3.0], "1.0") == "1.0"
    assert deepcast(Literal["2.0", "1.0", 3.0], 3.0) == 3.0
    with pytest.raises(TypeError):
        deepcast(Literal["2.0", "1.0", 3.0], 4)
