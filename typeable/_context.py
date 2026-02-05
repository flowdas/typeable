from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace

_default_bool_strings: dict[str, bool] = {
    "0": False,
    "1": True,
    "f": False,
    "false": False,
    "n": False,
    "no": False,
    "off": False,
    "on": True,
    "t": True,
    "true": True,
    "y": True,
    "yes": True,
}


@dataclass(slots=True)
class Context:
    bool_from_01: bool = True
    bool_strings: dict[str, bool] = field(default_factory=_default_bool_strings.copy)
    dict_from_empty_iterable: bool = False
    parse_number: bool = True
    validate_default: bool = False

    # TODO: review
    bytes_encoding: str = "utf-8"
    date_format: str = "iso"
    datetime_format: str = "iso"
    encoding_errors: str = "strict"
    naive_timestamp: bool = False
    time_format: str = "iso"
    union_prefers_same_type: bool = True
    union_prefers_base_type: bool = True
    union_prefers_super_type: bool = True
    union_prefers_nearest_type: bool = True

    # TO REMOVE
    bool_is_int: bool = True
    lossy_conversion: bool = False
    strict_str: bool = True  # test_enum_legacy 정리 후 제거


_default_context = Context()
_ctx = ContextVar("context", default=_default_context)


def getcontext() -> Context:
    return _ctx.get()


def setcontext(ctx: Context, /):
    if ctx is None:
        ctx = _default_context
    _ctx.set(ctx)


def setcontextclass(cls: type[Context], /):
    global _ctx, _default_context
    if not issubclass(cls, Context):
        raise TypeError(f"{cls.__name__} is not Context")
    _ctx.set(None)
    _default_context = cls()
    _ctx = ContextVar("context", default=_default_context)


@contextmanager
def localcontext(
    ctx: Context | None = None, /, **kwargs
) -> Generator[Context, None, None]:
    ctx = replace(_ctx.get() if ctx is None else ctx, **kwargs)
    token = _ctx.set(ctx)
    try:
        yield ctx
    finally:
        _ctx.reset(token)
