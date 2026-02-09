from typeable import deepcast

import pytest


def test_str_from_str():
    """str 은 str 로 변환된다."""
    v = "hello"
    assert deepcast(str, v) is v


@pytest.mark.parametrize(
    "v",
    [
        None,
        True,
        123,
        123.456,
        complex(1, 2),
        b"hello",
        bytearray(b"hello"),
        [],
        {},
        set(),
        object(),
        int,
    ],
)
def test_forbidden_cast(v):
    """str 이 아닌 것들을 str 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        deepcast(str, v)
