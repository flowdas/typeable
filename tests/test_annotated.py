from typing import Annotated

from typeable import localcontext, typecast


def test_Annotated():
    with localcontext(parse_number=True):
        assert typecast(Annotated[int, None, object()], "123") == 123
