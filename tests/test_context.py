from dataclasses import dataclass

import pytest

from typeable import Context


def test_policies():
    @dataclass(slots=True)
    class MyContext(Context):
        test_option: int = 0

    ctx = MyContext()
    assert ctx.bool_is_int is True
    assert ctx.bytes_encoding == "utf-8"
    assert ctx.test_option == 0

    ctx = MyContext(bool_is_int=False)
    assert ctx.bool_is_int is False
    assert ctx.bytes_encoding == "utf-8"
    assert ctx.test_option == 0

    ctx = MyContext(bytes_encoding="ascii")
    assert ctx.bool_is_int is True
    assert ctx.bytes_encoding == "ascii"
    assert ctx.test_option == 0

    ctx = MyContext(test_option=1)
    assert ctx.bool_is_int is True
    assert ctx.bytes_encoding == "utf-8"
    assert ctx.test_option == 1

    with pytest.raises(TypeError):
        MyContext(traverse=lambda: 0)

    with pytest.raises(TypeError):
        MyContext(unknown_option=0)
