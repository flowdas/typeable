import pytest

from typeable import typecast


@pytest.mark.parametrize("T", [bytearray, bytes])
@pytest.mark.parametrize("v", [bytearray(b"hello"), b"hello"])
def test_allowed(T, v):
    """bytes 와 bytearray 는 상호 변환된다."""
    if type(v) is T:
        assert typecast(T, v) is v
    else:
        assert typecast(T, v) == v


@pytest.mark.parametrize("T", [bytearray, bytes])
@pytest.mark.parametrize(
    "v",
    [
        None,
        True,
        123,
        123.456,
        complex(1, 2),
        "hello",
        [],
        {},
        set(),
        object(),
        int,
    ],
)
def test_forbidden_cast(T, v):
    """bytes 나 bytearray 가 아닌 것들을 bytes 나 bytearray 로 변환할 수 없다."""
    with pytest.raises(TypeError):
        typecast(T, v)
