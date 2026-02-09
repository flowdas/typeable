from typing import Annotated


from typeable import deepcast, localcontext


def test_Annotated():
    with localcontext(parse_number=True):
        assert deepcast(Annotated[int, None, object()], "123") == 123
