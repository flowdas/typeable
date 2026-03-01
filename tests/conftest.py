import pytest

from typeable._typecast import Typecast


@pytest.fixture
def typecast():
    return Typecast()


def str_from_int(typecast: Typecast, cls: type[str], val: int) -> str:
    return str(val)
