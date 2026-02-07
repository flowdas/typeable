from abc import get_cache_token
from collections.abc import (
    Callable,
    Mapping,
)
from contextlib import contextmanager
import dataclasses
from dataclasses import is_dataclass, fields, Field, MISSING
import datetime
from email.utils import parsedate_to_datetime
import enum
from functools import _find_impl  # type: ignore
import importlib
import inspect
import re
import sys
from types import NoneType
from typing import (
    Any,
    ForwardRef,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from ._context import Context, getcontext
from ._error import traverse
from ._polymorphic import _resolve_polymorphic

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
# deepcast
#


_T = TypeVar("_T")

_CasterType = Callable[["DeepCast", type[_T], Any], _T]

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


class DeepCast:
    _registry: dict[type, dict[type, _CasterType]]
    _dispatch_cache: dict[tuple[type, type], _CasterType]
    _cache_token: Any = None

    def __init__(self):
        self._registry = {}
        self._dispatch_cache = {}

    def __call__(self, cls: type[_T], val: Any) -> _T:
        origin = get_origin(cls) or cls
        Ts = _get_type_args(cls)
        tp = val.__class__
        try:
            if not Ts and isinstance(val, origin) and not (tp is bool and cls is int):
                return val
        except TypeError:
            pass
        func = self.dispatch(origin, tp)
        return func(self, origin, val, *Ts)

    def _register(self, cls, V, func):
        if cls in self._registry:
            if V in self._registry[cls]:
                raise RuntimeError("Ambiguous `deepcast.register()`")
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
                    f"Invalid second argument to `deepcast.register()`: {typ!r}. "
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
                    "Invalid signature to `deepcast.register()`. "
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
        func = _resolve_polymorphic(func, val)

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
        validate_default = getcontext().validate_default
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
            elif validate_default and p.annotation != empty:
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
                    annotation = sig.parameters[key].annotation
                else:
                    if kwargs_key is None:
                        raise TypeError(f"Unknown field {key!r}")
                    annotation = sig.parameters[kwargs_key].annotation
                kwargs[key] = value if annotation == empty else self(annotation, value)
                omissibles.discard(key)
                mandatories.discard(key)

        # 기본 값들도 형검사한다.
        for key in omissibles:
            with traverse(key):
                value = sig.parameters[key].default
                # defauly_factory 미리 호출하는 이유는 frozen 일 가능성 때문이다.
                factory = MISSING
                if key in dataclass_fields:
                    factory = dataclass_fields[key].default_factory
                if factory is not MISSING:
                    value = factory()
                else:
                    value = sig.parameters[key].default
                # omissibles 에는 어노테이션이 있는 것만 모아두었다.
                kwargs[key] = self(sig.parameters[key].annotation, value)

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
            return_type = sig.return_annotation or NoneType
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


deepcast = DeepCast()

#
# Any
#


@deepcast.register
def _cast_Any_object(deepcast: DeepCast, cls: type[Any], val):
    return val


#
# Union
#

# TODO: caching


def _type_distance(tp1, tp2):
    m1 = tp1.__mro__
    m2 = tp2.__mro__
    n = 0
    i = -1
    try:
        while m1[i] == m2[i]:
            i -= 1
            n += 1
    except IndexError:
        pass

    return len(m1) + len(m2) - 2 * n


@deepcast.register
def _cast_Union_object(deepcast: DeepCast, cls, val, *Ts) -> Union:
    vcls = val.__class__
    types = []  # [(kind, distance, index, type)]
    ctx: Context = getcontext()
    for i, T in enumerate(Ts):
        origin = get_origin(T) or T
        try:
            func = deepcast.dispatch(origin, vcls)
        except:
            continue
        if ctx.union_prefers_same_type and vcls is origin:
            k = 0
            d = 0
        elif ctx.union_prefers_base_type and isinstance(val, origin):
            k = 1
            d = _type_distance(vcls, origin)
        elif ctx.union_prefers_super_type and issubclass(origin, vcls):
            k = 2
            d = _type_distance(vcls, origin)
        elif ctx.union_prefers_nearest_type:
            k = 3
            fcls, fvcls = getattr(func, _TYPES)
            d = _type_distance(vcls, fcls)
            if d > 0:
                d = min(d, _type_distance(vcls, fvcls))
        else:
            k = 3
            d = 0
        types.append((k, d, i, T))
    types.sort()
    for _, _, _, T in types:
        try:
            return deepcast(T, val)
        except:
            import traceback

            traceback.print_exc()
            continue
    else:
        raise TypeError("no match")


#
# datetime.datetime
#


@deepcast.register
def _cast_datetime_object(deepcast: DeepCast, cls: type[datetime.datetime], val):
    # assume not isinstance(val, cls)
    if isinstance(val, (int, float)):
        ctx: Context = getcontext()
        if ctx.naive_timestamp:
            return cls.utcfromtimestamp(val)
        else:
            return cls.fromtimestamp(val, datetime.timezone.utc)
    elif isinstance(val, datetime.datetime):  # datetime is subclass of date
        return cls.combine(val.date(), val.timetz())
    elif isinstance(val, datetime.date):
        return cls.combine(val, datetime.time())
    else:
        return cls(*val)


ISO_DATE_HEAD = r"(?P<Y>\d{4})(-(?P<m>\d{1,2})(-(?P<D>\d{1,2})"
ISO_DATE_TAIL = r")?)?"
ISO_TIME = r"(?P<H>\d{1,2}):(?P<M>\d{1,2})(:(?P<S>\d{1,2}([.]\d*)?))?(?P<tzd>[+-](?P<tzh>\d{1,2}):(?P<tzm>\d{1,2})|Z)?"
ISO_DURATION = r"(?P<sgn>[+-])?P?((?P<W>\d+)[Ww])?((?P<D>\d+)[Dd])?T?((?P<H>\d+)[Hh])?((?P<M>\d+)[Mm])?((?P<S>\d+([.]\d*)?)[Ss]?)?"
ISO_PATTERN1 = re.compile(
    ISO_DATE_HEAD + r"([T ](" + ISO_TIME + r")?)?" + ISO_DATE_TAIL + "$"
)
ISO_PATTERN2 = re.compile(ISO_DATE_HEAD + ISO_DATE_TAIL + "$")
ISO_PATTERN3 = re.compile(ISO_TIME + "$")
ISO_PATTERN4 = re.compile(ISO_DURATION + "$")


def _parse_isotzinfo(m):
    if m.group("tzd"):
        if m.group("tzd") in ("Z", "+00:00", "-00:00"):
            tzinfo = datetime.timezone.utc
        else:
            offset = int(m.group("tzh")) * 60 + int(m.group("tzm"))
            if m.group("tzd").startswith("-"):
                offset = -offset
            tzinfo = datetime.timezone(datetime.timedelta(minutes=offset))
    else:
        tzinfo = None
    return tzinfo


def _parse_isotime(cls, m):
    hour, min, sec = m.group("H", "M", "S")
    hour = int(hour)
    min = int(min) if min else 0
    sec = float(sec) if sec else 0.0

    tzinfo = _parse_isotzinfo(m)
    return cls(hour, min, int(sec), int((sec % 1.0) * 1000000), tzinfo=tzinfo)


def _parse_isodate(cls, m):
    return datetime.date(
        *map(lambda x: 1 if x is None else int(x), m.group("Y", "m", "D"))
    )


def _parse_isoduration(cls, m):
    sign, week, day, hour, min, sec = m.group("sgn", "W", "D", "H", "M", "S")
    week = int(week) if week else 0
    day = int(day) if day else 0
    hour = int(hour) if hour else 0
    min = int(min) if min else 0
    sec = float(sec) if sec else 0.0

    td = cls(weeks=week, days=day, hours=hour, minutes=min, seconds=sec)
    return -td if sign == "-" else td


@deepcast.register
def _cast_datetime_str(deepcast: DeepCast, cls: type[datetime.datetime], val: str):
    ctx: Context = getcontext()
    if ctx.datetime_format == "iso":
        m = ISO_PATTERN1.match(val.strip())
        if m is None:
            raise ValueError()

        date = _parse_isodate(datetime.date, m)

        if m.group("H"):
            time = _parse_isotime(datetime.time, m)
        else:
            time = datetime.time(tzinfo=_parse_isotzinfo(m))

        return cls.combine(date, time)
    elif ctx.datetime_format == "timestamp":
        return deepcast(cls, float(val))
    elif ctx.datetime_format == "http" or ctx.datetime_format == "email":
        dt = parsedate_to_datetime(val.strip())
        if cls is not datetime.datetime:
            dt = cls.combine(dt.date(), dt.timetz())
        return dt
    else:
        return cls.strptime(val, ctx.datetime_format)


@deepcast.register
def _cast_float_datetime(deepcast: DeepCast, cls: type[float], val: datetime.datetime):
    return cls(val.timestamp())


@deepcast.register
def _cast_int_datetime(deepcast: DeepCast, cls: type[int], val: datetime.datetime):
    ts = val.timestamp()
    r = cls(ts)
    ctx: Context = getcontext()
    if not ctx.lossy_conversion and r != ts:
        raise ValueError(f"ctx.lossy_conversion={ctx.lossy_conversion}")
    return r


WDAY = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MON = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


@deepcast.register
def _cast_str_datetime(deepcast: DeepCast, cls: type[str], val: datetime.datetime):
    ctx: Context = getcontext()
    if ctx.datetime_format == "iso":
        r = val.isoformat()
        return cls(r[:-6] + "Z") if r.endswith("+00:00") else cls(r)
    elif ctx.datetime_format == "timestamp":
        if val.microsecond > 0:
            return cls(val.timestamp())
        else:
            return cls(int(val.timestamp()))
    elif ctx.datetime_format == "http" or ctx.datetime_format == "email":
        if ctx.datetime_format == "http":
            if val.tzinfo and val.utcoffset() != datetime.timedelta():
                val = val.replace(tzinfo=datetime.timezone.utc) - val.utcoffset()
            format = "%s, %%d %s %%Y %%H:%%M:%%S GMT"
        else:
            TZ = (
                (" %%z" if val.utcoffset() != datetime.timedelta() else " GMT")
                if val.tzinfo
                else ""
            )
            format = "%s, %%d %s %%Y %%H:%%M:%%S" + TZ
        format = format % (WDAY[val.weekday()], MON[val.month - 1])
        return cls(val.strftime(format))
    else:
        return cls(val.strftime(ctx.datetime_format))


#
# datetime.date
#


@deepcast.register
def _cast_date_object(deepcast: DeepCast, cls: type[datetime.date], val):
    # assume not isinstance(val, cls)
    if isinstance(val, datetime.datetime):  # datetime is subclass of date
        ctx: Context = getcontext()
        if not ctx.lossy_conversion and (val.tzinfo or val.time() != datetime.time()):
            raise ValueError(f"ctx.lossy_conversion={ctx.lossy_conversion}")
        return cls(val.year, val.month, val.day)
    elif isinstance(val, datetime.date):
        return cls(val.year, val.month, val.day)
    else:
        return cls(*val)


@deepcast.register
def _cast_date_str(deepcast: DeepCast, cls: type[datetime.date], val: str):
    ctx: Context = getcontext()
    if ctx.date_format == "iso":
        m = ISO_PATTERN2.match(val.strip())
        if m is None:
            raise ValueError()
        return _parse_isodate(cls, m)
    else:
        dt = datetime.datetime.strptime(val, ctx.date_format)
        return cls(dt.year, dt.month, dt.day)


@deepcast.register
def _cast_str_date(deepcast: DeepCast, cls: type[str], val: datetime.date):
    ctx: Context = getcontext()
    if ctx.date_format == "iso":
        return cls(val.isoformat())
    else:
        return cls(val.strftime(ctx.date_format))


#
# datetime.time
#


@deepcast.register
def _cast_time_object(deepcast: DeepCast, cls: type[datetime.time], val):
    # assume not isinstance(val, cls)
    if isinstance(val, datetime.time):
        return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
    elif isinstance(val, datetime.datetime):
        ctx: Context = getcontext()
        if not ctx.lossy_conversion:
            raise ValueError(f"ctx.lossy_conversion={ctx.lossy_conversion}")
        t = val.timetz()
        if t.__class__ is cls:
            return t
        return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
    else:
        return cls(*val)


@deepcast.register
def _cast_time_str(deepcast: DeepCast, cls: type[datetime.time], val: str):
    ctx: Context = getcontext()
    if ctx.time_format == "iso":
        m = ISO_PATTERN3.match(val.strip())
        if m is None:
            raise ValueError()
        return _parse_isotime(cls, m)
    else:
        dt = datetime.datetime.strptime(val, ctx.time_format)
        return cls(dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=dt.tzinfo)


@deepcast.register
def _cast_str_time(deepcast: DeepCast, cls: type[str], val: datetime.time):
    ctx: Context = getcontext()
    if ctx.time_format == "iso":
        return cls(val.isoformat())
    else:
        return cls(val.strftime(ctx.time_format))


#
# datetime.timedelta
#


@deepcast.register
def _cast_timedelta_object(deepcast: DeepCast, cls: type[datetime.timedelta], val):
    # assume not isinstance(val, cls)
    if isinstance(val, datetime.timedelta):
        return cls(days=val.days, seconds=val.seconds, microseconds=val.microseconds)
    elif isinstance(val, (int, float)):
        return cls(seconds=val)
    elif isinstance(val, str):
        m = ISO_PATTERN4.match(val.strip())
        if m is None:
            raise ValueError()
        return _parse_isoduration(cls, m)
    else:
        raise TypeError


@deepcast.register
def _cast_float_timedelta(
    deepcast: DeepCast, cls: type[float], val: datetime.timedelta
):
    return cls(val.total_seconds())


@deepcast.register
def _cast_int_timedelta(deepcast: DeepCast, cls: type[int], val: datetime.timedelta):
    td = val.total_seconds()
    r = cls(td)
    ctx: Context = getcontext()
    if not ctx.lossy_conversion and r != td:
        raise ValueError(f"ctx.lossy_conversion={ctx.lossy_conversion}")
    return r


@deepcast.register
def _cast_str_timedelta(deepcast: DeepCast, cls: type[str], val: datetime.timedelta):
    r = []
    if val.days < 0:
        r.append("-P")
        val = -val
    else:
        r.append("P")
    if val.days:
        r.append(f"{val.days}D")
    if val.seconds or val.microseconds:
        r.append("T")
        min, sec = divmod(val.seconds, 60)
        hour, min = divmod(min, 60)
        if hour:
            r.append(f"{hour}H")
        if min:
            r.append(f"{min}M")
        if val.microseconds:
            sec += val.microseconds / 1000000
        if sec:
            r.append(f"{sec}S")
    return cls("".join(r))


#
# enum.Enum
#


@deepcast.register
def _cast_Enum_object(deepcast: DeepCast, cls: type[enum.Enum], val):
    # assume not isinstance(val, cls)
    return cls(val)


@deepcast.register
def _cast_Enum_str(deepcast: DeepCast, cls: type[enum.Enum], val: str):
    return getattr(cls, val)


@deepcast.register
def _cast_str_Enum(deepcast: DeepCast, cls: type[str], val: enum.Enum):
    return val.name


#
# enum.IntEnum
#


@deepcast.register
def _cast_IntEnum_int(deepcast: DeepCast, cls: type[enum.IntEnum], val: int):
    return cls(val)


@deepcast.register
def _cast_IntEnum_str(deepcast: DeepCast, cls: type[enum.IntEnum], val: str):
    return getattr(cls, val)


@deepcast.register
def _cast_str_IntEnum(deepcast: DeepCast, cls: type[str], val: enum.IntEnum):
    return val.name


#
# enum.Flag
#


@deepcast.register
def _cast_Flag_Flag(deepcast: DeepCast, cls: type[enum.Flag], val: enum.Flag):
    # assume not isinstance(val, cls)
    return cls(val)


@deepcast.register
def _cast_Flag_int(deepcast: DeepCast, cls: type[enum.Flag], val: int):
    return cls(val)


@deepcast.register
def _cast_int_Flag(deepcast: DeepCast, cls: type[int], val: enum.Flag):
    return cls(val.value)


@deepcast.register
def _cast_str_Flag(deepcast: DeepCast, cls: type[str], val: enum.Flag):
    raise TypeError


#
# enum.IntFlag
#


@deepcast.register
def _cast_IntFlag_int(deepcast: DeepCast, cls: type[enum.IntFlag], val: int):
    return cls(val)


@deepcast.register
def _cast_str_IntFlag(deepcast: DeepCast, cls: type[str], val: enum.IntFlag):
    raise TypeError


#
# typing.Literal
#


@deepcast.register
def _cast_Literal_object(deepcast: DeepCast, cls, val, *literals) -> Literal:
    for literal in literals:
        if literal == val:
            return literal
    else:
        raise TypeError(f"One of {literals!r} required, but {val!r} is given")


#
# type
#


@deepcast.register
def _cast_type_type(deepcast: DeepCast, cls, val: type, T=None) -> type:
    if T and T is not Any and not issubclass(val, T):
        raise TypeError
    return val


@deepcast.register
def _cast_type_str(deepcast: DeepCast, cls, val: str, T=None) -> type:
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
