import pytest

from typeable._typecast import DeepCast


collect_ignore = [
    "test_constraint_legacy.py",
]


@pytest.fixture
def deepcast():
    return DeepCast()


def str_from_int(deepcast: DeepCast, cls: type[str], val: int) -> str:
    return str(val)
