import dataclasses
from datetime import date, datetime
import enum
import importlib
import inspect
import sys
from abc import ABC, get_cache_token
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from dataclasses import MISSING, Field, dataclass, fields, is_dataclass
from functools import _compose_mro, _find_impl  # type: ignore
from types import NoneType
from typing import (
    Any,
    ForwardRef,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from ._context import Context, getcontext
from ._error import traverse
from ._polymorphic import Polymorphic

#
# declare
#

if sys.version_info < (3, 14):

    @contextmanager
    def declare(name):
        ref = ForwardRef(name)
        yield ref
        frame = inspect.currentframe().f_back.f_back
        args = [frame.f_globals, frame.f_locals]
        try:
            ref._evaluate(*args, recursive_guard=frozenset())
        finally:
            del frame
            del args
else:

    @contextmanager
    def declare(name):
        ref = ForwardRef(name)
        yield ref
        frame = inspect.currentframe().f_back.f_back
        globals = frame.f_globals.copy()
        globals.update(frame.f_locals)
        ref.__globals__ = globals
        del frame
        del globals

#
# JsonValue
#


class JsonValue(ABC):
    pass


JsonValue.register(NoneType)
JsonValue.register(int)
JsonValue.register(float)
JsonValue.register(str)
JsonValue.register(list)
JsonValue.register(tuple)
JsonValue.register(dict)

#
# typecast
#


_T = TypeVar("_T")

_CasterType = Callable[["Typecast", type[_T], Any], _T]

_TYPES = "__types__"

_META_ALIAS = "alias"
_META_HIDE = "hide"


def _get_type_args(tp):
    args = get_args(tp)
    # recover pre-3.11 empty tuple behavior
    if not args and hasattr(tp, "__args__"):
        args = ((),)
    evaled = list(args)
    changed = False
    for i, arg in enumerate(evaled):
        try:
            if isinstance(arg, ForwardRef):
                _args = [None, None]
                evaled[i] = arg._evaluate(*_args, recursive_guard=frozenset())
                changed = True
        except TypeError:  # pragma: no cover; TODO: Is this really necessary?
            continue
    return tuple(evaled) if changed else args


@dataclass
class Unioncast:
    args: tuple[type, ...]
    registry: dict[type, list[type]] = dataclasses.field(default_factory=dict)
    dispatch_cache: dict[type, list[type]] = dataclasses.field(default_factory=dict)
    cache_token: Any = None

    def __post_init__(self):
        reg = self.registry
        for cls in self.args:
            origin = get_origin(cls) or cls
            if origin not in reg:
                reg[origin] = []
                if self.cache_token is None and hasattr(origin, "__abstractmethods__"):
                    self.cache_token = get_cache_token()
            reg[origin].append(cls)

    def dispatch(self, cls):
        if self.cache_token is not None:
            current_token = get_cache_token()
            if self.cache_token != current_token:
                self.dispatch_cache.clear()
                self.cache_token = current_token
        cache = self.dispatch_cache.get(cls)
        if cache is None:
            args = {arg: None for arg in self.args}
            cache = []
            reg = self.registry
            mro = _compose_mro(cls, reg.keys())
            for t in mro:
                if t in reg:
                    for T in reg[t]:
                        cache.append(T)
                        del args[T]
            cache.extend(args.keys())
            self.dispatch_cache[cls] = cache
        for t in cache:
            yield t


class Typecast:
    _registry: dict[type, dict[type, _CasterType]]
    _dispatch_cache: dict[tuple[type, type], _CasterType]
    _cache_token: Any = None
    _unions: dict[tuple[type, ...], Unioncast]

    def __init__(self):
        self._registry = {}
        self._dispatch_cache = {}
        self._unions = {}

    @overload
    def __call__(self, cls: type[_T], val: Any) -> _T: ...
    @overload
    def __call__(self, cls: object, val: Any) -> Any: ...

    def __call__(self, cls: type[_T] | object, val: Any) -> _T | Any:
        origin = cast(type, get_origin(cls) or cls)
        if origin == Any:
            origin = object
        Ts = _get_type_args(cls)
        tp = val.__class__
        try:
            if (
                not Ts
                and isinstance(val, origin)
                and not (tp is bool and cls is int)
                and not (origin is JsonValue and isinstance(val, (dict, list, tuple)))
                and not (tp is datetime and cls is date)
            ):
                if origin is int:
                    if tp is not bool:
                        return val
                elif origin is JsonValue:
                    if not isinstance(val, (dict, list, tuple)):
                        return val
                elif origin is date:
                    if not issubclass(tp, datetime):
                        return val
                else:
                    return val
        except TypeError:
            pass
        func = self.dispatch(origin, tp)
        return func(self, origin, val, *Ts)

    def _register(self, cls, V, func):
        if cls in self._registry:
            if V in self._registry[cls]:
                raise RuntimeError("Ambiguous `typecast.register()`")
            self._registry[cls][V] = func
        else:
            self._registry[cls] = {V: func}
        setattr(func, _TYPES, (cls, V))

        if self._cache_token is None and any(
            hasattr(T, "__abstractmethods__") for T in (cls, V)
        ):
            self._cache_token = get_cache_token()
        self._dispatch_cache.clear()

    def _deregister(self, func):
        cls, V = getattr(func, _TYPES)
        del self._registry[cls][V]
        if not self._registry[cls]:
            del self._registry[cls]
        delattr(func, _TYPES)
        self._dispatch_cache.clear()

    def register(self, func):
        sig = inspect.signature(func)
        if len(sig.parameters) < 3:
            raise TypeError(
                f"{func!r}() takes {len(sig.parameters)} arguments but at least 3 required"
            )
        it = iter(sig.parameters.items())
        next(it)  #
        argname, _ = next(it)
        hints = get_type_hints(func)
        typ = hints.get(argname)
        if typ:
            type_args = _get_type_args(typ)
            if get_origin(typ) is not type or not type_args:
                raise TypeError(
                    f"Invalid second argument to `typecast.register()`: {typ!r}. "
                    f"Use either type[] annotation or return type annotation."
                )
            cls = type_args[0]
            _rcls = hints.get("return")
            if _rcls not in {None, cls}:
                raise TypeError(
                    "The type annotation of the second argument does not match the return type annotation."
                )
        else:
            cls = hints.get("return")
            if cls is None:
                raise TypeError(
                    "Invalid signature to `typecast.register()`. "
                    "Use either type[] annotation or return type annotation."
                )

        argname, _ = next(it)
        vcls = hints.get(argname)
        if not vcls or vcls is Any:
            vcls = object

        self._register(cls, vcls, func)

        return func

    def forbid(self, cls, *Vs):
        def forbid(*args):
            raise TypeError(f"{cls.__qualname__} from {V.__qualname__} not supported")

        for V in Vs:
            self._register(cls, V, forbid)

    @contextmanager
    def localregister(self, func):
        self.register(func)
        try:
            yield
        finally:
            self._deregister(func)

    def dispatch(self, cls, vcls):
        if self._cache_token is not None:
            current_token = get_cache_token()
            if self._cache_token != current_token:
                self._dispatch_cache.clear()
                self._cache_token = current_token

        try:
            func = self._dispatch_cache[(cls, vcls)]
        except KeyError:
            try:
                vreg = self._registry[cls]
            except KeyError:
                try:
                    vreg = _find_impl(cls, self._registry)
                except AttributeError:
                    raise TypeError(f"{cls!r} is not a supported type.")
                if not vreg:
                    raise NotImplementedError(
                        f"No implementation found for '{cls.__qualname__}'"
                    )

            try:
                return vreg[vcls]
            except KeyError:
                func = _find_impl(vcls, vreg)
                if not func:
                    raise TypeError(
                        f"No implementation found for '{cls.__qualname__}' from {vcls.__qualname__}"
                    )
            self._dispatch_cache[(cls, vcls)] = func

        return func

    def apply(
        self, func: Callable[..., _T], val: Any, *, validate_return: bool = False
    ) -> _T:
        if not callable(func):
            raise TypeError(f"{func!r} is not callable.")

        # val 에서 Mapping 인터페이스를 얻는다.
        if not isinstance(val, Mapping):
            val = self(dict, val)

        # resolve interface
        func = Polymorphic.resolve(func, val)

        # func 의 서명을 파싱한다.
        aliases: dict[str, str] = {}  # val's name -> func's name mapping
        omissibles: set[str] = set()
        mandatories: set[str] = set()
        args_keys: list[str] = []
        kwargs_key: str | None = None
        empty = inspect.Parameter.empty
        dataclass_fields: dict[str, Field] = {}
        if is_dataclass(func):
            dataclass_fields = {f.name: f for f in fields(func)}
        sig = inspect.signature(func)
        ann = get_type_hints(func, include_extras=True)
        ctx: Context = getcontext()
        for key, p in sig.parameters.items():
            if key in dataclass_fields:
                f = dataclass_fields[key]
                if _META_ALIAS in (f.metadata or {}):
                    aliases[self(str, f.metadata[_META_ALIAS])] = key
            if p.kind == p.POSITIONAL_ONLY:
                args_keys.append(key)
            if p.kind == p.VAR_KEYWORD:
                kwargs_key = key
            if p.default == empty:
                if p.kind not in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                }:
                    mandatories.add(key)
            elif ctx.validate_default and p.annotation != empty:
                omissibles.add(key)

        # kwargs 를 만든다
        kwargs = {}
        for key in val:
            with traverse(key):
                value = val[key]
                key = self(str, key)
                if key in aliases:
                    key = aliases[key]
                if key in sig.parameters:
                    if sig.parameters[key].kind in {
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    }:
                        raise TypeError(f"Unknown field {key!r}")
                    annotation = ann.get(key, empty)
                else:
                    if kwargs_key is None:
                        if ctx.allow_extra_items:
                            continue
                        raise TypeError(f"Unknown field {key!r}")
                    annotation = ann.get(kwargs_key, empty)
                kwargs[key] = value if annotation == empty else self(annotation, value)
                omissibles.discard(key)
                mandatories.discard(key)

        # 기본 값들도 형검사한다.
        for key in omissibles:
            with traverse(key):
                # defauly_factory 미리 호출하는 이유는 frozen 일 가능성 때문이다.
                factory = MISSING
                if key in dataclass_fields:
                    factory = dataclass_fields[key].default_factory
                if factory is not MISSING:
                    value = factory()
                else:
                    value = sig.parameters[key].default
                # omissibles 에는 어노테이션이 있는 것만 모아두었다.
                kwargs[key] = self(ann[key], value)

        # 필수 인자 중 빠진 것이 있는지 검사한다
        # 미리 검사하는 대신 호출시 예외가 발생할 때 검사하는 대안도 있다.
        for key in mandatories:
            with traverse(key):
                raise TypeError(f"Missing field {key!r}")

        # 위치전용 인자를 추출한다
        args = []
        try:
            for key in args_keys:
                args.append(kwargs.pop(key))
        except KeyError:
            # 필수 인자 중 빠진 것은 없으므로 이 이후로 모두 default 가 있어야만 한다.
            pass

        # callable 을 호출한다.
        ret = func(*args, **kwargs)
        if validate_return and sig.return_annotation != empty:
            return_type = ann["return"]
            with traverse("return"):
                ret = self(return_type, ret)
        return ret

    def field(
        self,
        *,
        default=MISSING,
        default_factory=MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,
        kw_only=MISSING,
        doc=None,
        alias: str | None = None,
        hide: bool = False,
    ) -> Any:
        kwargs = {}
        if metadata is None:
            metadata = {}
        else:
            metadata = metadata.copy()
        if doc is not None:
            if sys.version_info < (3, 14):
                metadata["doc"] = doc
            else:
                kwargs["doc"] = doc
        if alias is None:
            alias = metadata.pop(_META_ALIAS, None)
        if alias is not None:
            if not isinstance(alias, str):
                raise TypeError(f"The alias must be a str: {alias!r}")
            metadata[_META_ALIAS] = alias
        hide = hide or metadata.pop(_META_HIDE, False)
        if hide:
            metadata[_META_HIDE] = True
        return dataclasses.field(
            default=default,
            default_factory=default_factory,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=(metadata or None),
            kw_only=kw_only,
            **kwargs,
        )

    def get_unioncast(self, args: tuple[type, ...]) -> Unioncast:
        try:
            return self._unions[args]
        except KeyError:
            entry = self._unions[args] = Unioncast(args)
            return entry


typecast = Typecast()

#
# enum.Enum
#


@typecast.register
def _cast_Enum_object(typecast: Typecast, cls: type[enum.Enum], val):
    # assume not isinstance(val, cls)
    return cls(val)


@typecast.register
def _cast_Enum_str(typecast: Typecast, cls: type[enum.Enum], val: str):
    return getattr(cls, val)


@typecast.register
def _cast_str_Enum(typecast: Typecast, cls: type[str], val: enum.Enum):
    return val.name


#
# enum.IntEnum
#


@typecast.register
def _cast_IntEnum_int(typecast: Typecast, cls: type[enum.IntEnum], val: int):
    return cls(val)


@typecast.register
def _cast_IntEnum_str(typecast: Typecast, cls: type[enum.IntEnum], val: str):
    return getattr(cls, val)


@typecast.register
def _cast_str_IntEnum(typecast: Typecast, cls: type[str], val: enum.IntEnum):
    return val.name


#
# enum.Flag
#


@typecast.register
def _cast_Flag_Flag(typecast: Typecast, cls: type[enum.Flag], val: enum.Flag):
    # assume not isinstance(val, cls)
    return cls(val)


@typecast.register
def _cast_Flag_int(typecast: Typecast, cls: type[enum.Flag], val: int):
    return cls(val)


@typecast.register
def _cast_int_Flag(typecast: Typecast, cls: type[int], val: enum.Flag):
    return cls(val.value)


@typecast.register
def _cast_str_Flag(typecast: Typecast, cls: type[str], val: enum.Flag):
    raise TypeError


#
# enum.IntFlag
#


@typecast.register
def _cast_IntFlag_int(typecast: Typecast, cls: type[enum.IntFlag], val: int):
    return cls(val)


@typecast.register
def _cast_str_IntFlag(typecast: Typecast, cls: type[str], val: enum.IntFlag):
    raise TypeError


#
# type
#


@typecast.register
def _cast_type_type(typecast: Typecast, cls, val: type, T=None) -> type:
    if T and T is not Any and not issubclass(val, T):
        raise TypeError
    return val


@typecast.register
def _cast_type_str(typecast: Typecast, cls, val: str, T=None) -> type:
    spec = val.rsplit(".", maxsplit=1)
    if len(spec) == 1:
        modname = "builtins"
        parts = spec
    else:
        modname = spec[0]
        parts = [spec[1]]
    if not (modname and parts[0]):
        raise TypeError
    while True:
        try:
            mod = importlib.import_module(modname)
            break
        except ModuleNotFoundError:
            spec = modname.rsplit(".", maxsplit=1)
            if len(spec) <= 1:
                raise
            modname = spec[0]
            parts.append(spec[1])
            continue
    cls = mod
    for part in reversed(parts):
        cls = getattr(cls, part)
    if not isinstance(cls, type):
        raise TypeError
    if T and T is not Any and not issubclass(cls, T):
        raise TypeError
    return cls
