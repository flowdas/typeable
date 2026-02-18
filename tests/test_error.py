from typing import (
    Dict,
    List,
)

import pytest

from typeable import capture, typecast


def test_capture():
    class T:
        pass

    @typecast.register
    def _(typecast, cls, val) -> T:
        raise NotImplementedError

    with pytest.raises(NotImplementedError):
        with capture() as error:
            typecast(T, 1)
    assert error.location == ()
    assert error.exc_info is not None
    exc_type, _, _ = error.exc_info
    assert exc_type is NotImplementedError

    with pytest.raises(TypeError):
        with capture() as error:
            typecast(List[int], [0, None])
    assert error.location == (1,)

    with pytest.raises(NotImplementedError):
        with capture() as error:
            typecast(Dict[T, List[int]], {None: [0, None]})
    assert error.location == (None,)

    t = T()
    with pytest.raises(TypeError):
        with capture() as error:
            typecast(Dict[T, List[int]], {t: [0, None]})
    assert error.location == (t, 1)
