import pytest

from typeable import typecast


def test_object():
    """isinstance(v, T) == True 일 때 deepcast(T, v) 는 보통 v 를 반환한다."""
    v = object()
    assert typecast(object, v) is v


def test_None():
    """None 도 object 다."""
    assert typecast(object, None) is None


def test_custom_class():
    """isinstance(v, T) == True 조건은 커스텀 클래스에도 적용된다."""

    class X:
        pass

    x = X()
    assert typecast(X, x) is x


def test_X_from_str():
    """str 에서 커스텀 클래스로의 변환은 실패해야 한다."""

    class X:
        pass

    with pytest.raises(TypeError):
        typecast(X, "")


def test_init_from_dict():
    """생성자로 dict 를 언패킹할 수 있다."""

    class X:
        def __init__(self, i: int):
            self.i = i

    data = {"i": 3}
    x = typecast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
