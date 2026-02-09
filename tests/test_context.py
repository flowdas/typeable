from dataclasses import dataclass

import pytest

from typeable import Context


def test_policies():
    @dataclass(slots=True)
    class MyContext(Context):
        test_option: int = 0

    ctx = MyContext()
    assert ctx.validate_default is False
    assert ctx.datetime_format == "iso"
    assert ctx.test_option == 0

    ctx = MyContext(validate_default=True)
    assert ctx.validate_default is True
    assert ctx.datetime_format == "iso"
    assert ctx.test_option == 0

    ctx = MyContext(datetime_format="string")
    assert ctx.validate_default is False
    assert ctx.datetime_format == "string"
    assert ctx.test_option == 0

    ctx = MyContext(test_option=1)
    assert ctx.validate_default is False
    assert ctx.datetime_format == "iso"
    assert ctx.test_option == 1

    with pytest.raises(TypeError):
        MyContext(traverse=lambda: 0)

    with pytest.raises(TypeError):
        MyContext(unknown_option=0)
