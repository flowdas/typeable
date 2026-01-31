import pytest

from typeable._deepcast import DeepCast


collect_ignore = [
    "test_constraint_legacy.py",
]


@pytest.fixture
def deepcast():
    return DeepCast()
