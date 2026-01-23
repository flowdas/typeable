from contextlib import AbstractContextManager, contextmanager, nullcontext
from contextvars import ContextVar
from dataclasses import dataclass
import sys
from types import TracebackType
from typing import Any, Generator

_nullctx = nullcontext()


class _NullStack:
    def traverse(self, _: Any) -> AbstractContextManager:
        return _nullctx


_stack = ContextVar("stack", default=_NullStack())


class _Stack(_NullStack):
    def __init__(self):
        self.stack: list[Any] = []

    @contextmanager
    def traverse(self, key: Any):
        self.stack.append(key)
        yield None
        self.stack.pop()


@dataclass
class ErrorInfo:
    exc_info: (
        tuple[type[BaseException] | None, BaseException | None, TracebackType | None]
        | None
    ) = None
    location: tuple | None = None


def traverse(key: Any) -> AbstractContextManager:
    return _stack.get().traverse(key)


@contextmanager
def capture() -> Generator[ErrorInfo, None, None]:
    instance = _Stack()
    token = _stack.set(instance)
    try:
        error: ErrorInfo = ErrorInfo()
        try:
            yield error
        except Exception:
            error.exc_info = sys.exc_info()
            error.location = tuple(instance.stack)
            raise
    finally:
        _stack.reset(token)
