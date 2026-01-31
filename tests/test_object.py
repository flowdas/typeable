from typeable import deepcast


def test_object():
    """isinstance(v, T) == True 일 때 deepcast(T, v) 는 보통 v 를 반환한다."""
    v = object()
    assert deepcast(object, v) is v


def test_init_from_dict():
    """생성자로 dict 를 언패킹할 수 있다."""

    class X:
        def __init__(self, i: int):
            self.i = i

    data = {"i": 3}
    x = deepcast(X, data)
    assert isinstance(x, X)
    assert x.i == data["i"]
