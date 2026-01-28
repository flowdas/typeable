from typing import (
    Type,
)

import pytest

from typeable._deepcast import DeepCast


@pytest.fixture
def deepcast():
    return DeepCast()


@pytest.mark.parametrize(
    "T",
    [
        Type[bool],
        type[bool],
        type[int],
    ],
)
def test_supported_cls_types(deepcast, T):
    """첫번째 인자의 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(cls: T, val: object): ...  # type: ignore


@pytest.mark.parametrize(
    "T",
    [
        bool,  # type[bool] 을 써야 한다
    ],
)
def test_unsupported_cls_types(deepcast, T):
    """첫번째 인자의 타입으로 등록할 수 없음을 확인한다."""

    with pytest.raises(TypeError):

        @deepcast.register
        def _(cls: T, val: object): ...  # type: ignore


@pytest.mark.parametrize(
    "RT",
    [
        bool,
        int,
    ],
)
def test_supported_return_types(deepcast, RT):
    """반환 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(cls, val: object) -> RT: ...  # type: ignore


@pytest.mark.parametrize(
    "VT",
    [
        bool,
        int,
    ],
)
def test_supported_value_types(deepcast, VT):
    """두번째 인자의 타입으로 등록할 수 있음을 확인한다."""

    @deepcast.register
    def _(cls: type[object], val: VT): ...  # type: ignore


def test_register_collison(deepcast):
    """같은 서명으로 취급되는 두 변환기를 등록하면 RuntimeError 가 발생해야 한다."""

    @deepcast.register
    def _(cls: type[float], val: object): ...

    with pytest.raises(RuntimeError):

        @deepcast.register
        def _(cls, val: object) -> float: ...


def test_register_without_args(deepcast):
    """인자가 부족한 변환기를 등록하면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(): ...


def test_register_without_annotations(deepcast):
    """형 어노테이션을 제공하지 않으면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(cls, val): ...


def test_register_mismatch(deepcast):
    """첫 인자의 형과 반환 형이 호환되지 않으면 TypeError 가 발생해야 한다."""
    with pytest.raises(TypeError):

        @deepcast.register
        def _(cls: type[float], val: int) -> int: ...


def test_exact_match(deepcast):
    """변환기 서명과 정확히 일치하는 형 변환이 수행됨을 확인한다."""

    class X:
        pass

    @deepcast.register
    def _(cls: type[int], val: X) -> int:
        return 123

    assert deepcast(int, X()) == 123
