import pytest

from typeable._typecast import Typecast

collect_ignore = [
    "test_constraint_legacy.py",
]


@pytest.fixture
def typecast():
    return Typecast()


def str_from_int(typecast: Typecast, cls: type[str], val: int) -> str:
    return str(val)
