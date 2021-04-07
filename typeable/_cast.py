# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import asyncio
from contextlib import contextmanager
import datetime
from email.utils import parsedate_to_datetime
import enum
import functools
import importlib
import inspect
import itertools
import re
from abc import get_cache_token
from collections.abc import (
    Mapping,
)
from functools import _find_impl
from numbers import Number
from inspect import (
    signature,
)
from .typing import (
    Any,
    Dict,
    ForwardRef,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    _RECURSIVE_GUARD,
)

from ._context import Context


#
# declare
#


@contextmanager
def declare(name):
    ref = ForwardRef(name)
    yield ref
    frame = inspect.currentframe().f_back.f_back
    args = [frame.f_globals, frame.f_locals]
    if _RECURSIVE_GUARD:
        args.append(set())
    try:
        ref._evaluate(*args)
    finally:
        del frame
        del args


#
# cast
#


_T = TypeVar('_T')

_registry = {}
_dispatch_cache = {}
_cache_token = None

_TYPES = '__types__'


def _get_type_args(tp):
    args = get_args(tp)
    evaled = list(args)
    changed = False
    for i, arg in enumerate(evaled):
        try:
            if isinstance(arg, ForwardRef):
                _args = [None, None]
                if _RECURSIVE_GUARD:
                    _args.append(frozenset())
                evaled[i] = arg._evaluate(*_args)
                changed = True
        except TypeError:  # pragma: no cover; TODO: Is this really necessary?
            continue
    return tuple(evaled) if changed else args


def _register(func):
    global _cache_token
    sig = signature(func)
    if len(sig.parameters) < 3:
        raise TypeError(
            f"{func!r}() takes {len(sig.parameters)} arguments but 3 required")
    it = iter(sig.parameters.items())
    argname, parameter = next(it)
    hints = get_type_hints(func)
    typ = hints.get(argname)
    if typ:
        type_args = _get_type_args(typ)
        if get_origin(typ) is not type or not type_args:
            raise TypeError(
                f"Invalid first argument to `cast.register()`: {typ!r}. "
                f"Use either typing.Type[] annotation or return type annotation."
            )
        cls = type_args[0]
    else:
        cls = hints.get('return')
        if cls is None:
            raise TypeError(
                f"Invalid signature to `cast.register()`. "
                f"Use either typing.Type[] annotation or return type annotation."
            )

    argname, parameter = next(it)
    vcls = hints.get(argname)
    if not vcls:
        vcls = Any
    if vcls == Any:
        vcls = object

    if cls in _registry:
        if vcls in _registry[cls]:
            raise RuntimeError(f"Ambiguous `cast.register()`")
        _registry[cls][vcls] = func
    else:
        _registry[cls] = {vcls: func}
    setattr(func, _TYPES, (cls, vcls))

    if _cache_token is None:
        if hasattr(cls, '__abstractmethods__') or hasattr(vcls, '__abstractmethods__'):
            _cache_token = get_cache_token()
    _dispatch_cache.clear()

    return func


def _dispatch(cls, vcls):
    global _cache_token
    if _cache_token is not None:
        current_token = get_cache_token()
        if _cache_token != current_token:
            _dispatch_cache.clear()
            _cache_token = current_token

    try:
        func = _dispatch_cache[(cls, vcls)]
    except KeyError:
        try:
            vreg = _registry[cls]
        except KeyError:
            vreg = _find_impl(cls, _registry)
            if not vreg:
                raise NotImplementedError(
                    f"No implementation found for '{cls.__qualname__}'")

        try:
            return vreg[vcls]
        except KeyError:
            func = _find_impl(vcls, vreg)
            if not func:
                raise TypeError(
                    f"No implementation found for '{cls.__qualname__}' from {vcls.__qualname__}")
        _dispatch_cache[(cls, vcls)] = func

    return func


def _function(_=None, *, ctx_name: str = 'ctx', cast_return: bool = False, keep_async: bool = True):
    def deco(func):
        nonlocal cast_return

        sig = inspect.signature(func)
        annons = get_type_hints(func)
        if 'return' not in annons:
            cast_return = False
        use_ctx = False
        if ctx_name in sig.parameters:
            ctx_type = annons.get(ctx_name)
            if (ctx_type == Optional[Context] or ctx_type == Context) \
                    and (sig.parameters[ctx_name].kind not in (
                    inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)):
                use_ctx = True
            else:
                raise TypeError(f"'{ctx_name}' argument conflict")

        def prolog(args, kwargs):
            if use_ctx:
                ctx = kwargs.get(ctx_name)
                if ctx is None:
                    ctx = kwargs[ctx_name] = Context()
            else:
                ctx = kwargs.pop(ctx_name, None)
                if ctx is None:
                    ctx = Context()
            ba = sig.bind(*args, **kwargs)
            for key, val in ba.arguments.items():
                if key == ctx_name:
                    continue
                if key in annons:
                    with ctx.traverse(key):
                        tp = annons[key]
                        if sig.parameters[key].kind == inspect.Parameter.VAR_POSITIONAL:
                            tp = Tuple[tp, ...]
                        elif sig.parameters[key].kind == inspect.Parameter.VAR_KEYWORD:
                            tp = Dict[Any, tp]
                        ba.arguments[key] = cast(tp, val, ctx=ctx)
            return ctx, ba

        def epilog(ctx, r):
            if cast_return:
                with ctx.traverse('return'):
                    r = cast(annons['return'], r, ctx=ctx)
            return r

        if asyncio.iscoroutinefunction(func) and keep_async:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                ctx, ba = prolog(args, kwargs)
                r = await func(*ba.args, **ba.kwargs)
                return epilog(ctx, r)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                ctx, ba = prolog(args, kwargs)
                r = func(*ba.args, **ba.kwargs)
                return epilog(ctx, r)

        wrapper._ctx = ctx_name

        return wrapper

    return deco if _ is None else deco(_)


def cast(cls: Type[_T], val, *, ctx: Context = None) -> _T:
    origin = get_origin(cls) or cls
    Ts = _get_type_args(cls)
    tp = val.__class__
    try:
        if not Ts and isinstance(val, origin) and tp is not bool:
            return val
    except:
        pass
    func = _dispatch(origin, tp)
    if ctx is None:
        ctx = Context()
    return func(origin, val, ctx, *Ts)


cast.register = _register
cast.dispatch = _dispatch
cast.function = _function


#
# Any
#


@cast.register
def _cast_Any_object(cls: Type[Any], val, ctx):
    return val


#
# object (fallback)
#


@cast.register
def _cast_object_object(cls: Type[object], val, ctx, *Ts):
    if Ts:
        raise NotImplementedError
    return cls(val)


#
# bool
#


@cast.register
def _cast_bool_int(cls: Type[bool], val: int, ctx):
    # special: val can be bool
    if isinstance(val, cls):
        return val

    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    if not ctx.lossy_conversion and not (val == 0 or val == 1):
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return cls(val)


@cast.register
def _cast_bool_str(cls: Type[bool], val: str, ctx):
    if not ctx.bool_strings:
        raise TypeError
    try:
        return cls(ctx.bool_strings[val.lower()])
    except KeyError:
        raise ValueError


#
# int
#


@cast.register
def _cast_int_object(cls: Type[int], val, ctx):
    # assume not isinstance(val, cls)
    r = cls(val)
    if not ctx.lossy_conversion and val.__class__(r) != val:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


@cast.register
def _cast_int_bool(cls: Type[int], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return val if cls is int else cls(val)


#
# float
#


@cast.register
def _cast_float_object(cls: Type[float], val, ctx):
    # assume not isinstance(val, cls)
    return cls(val)


@cast.register
def _cast_float_bool(cls: Type[float], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)


#
# complex
#


@cast.register
def _cast_complex_object(cls: Type[complex], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, (tuple, list)):
        r = cls(*val)
    else:
        r = cls(val)
    return r


@cast.register
def _cast_complex_bool(cls: Type[complex], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)


#
# str
#


@cast.register
def _cast_str_object(cls: Type[str], val, ctx):
    # assume not isinstance(val, cls)
    if ctx.strict_str:
        if not isinstance(val, (str, Number)):
            raise TypeError(f'ctx.strict_str={ctx.strict_str}')
    else:
        if val is None:
            raise TypeError(
                f"{cls.__qualname__} is required, but {val!r} is given")
    return cls(val)


@cast.register
def _cast_str_bytes(cls: Type[str], val: bytes, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


@cast.register
def _cast_str_bytearray(cls: Type[str], val: bytearray, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# bytes
#


@cast.register
def _cast_bytes_object(cls: Type[bytes], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, int):
        raise TypeError
    return cls(val)


@cast.register
def _cast_bytes_str(cls: Type[bytes], val: str, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# bytearray
#


@cast.register
def _cast_bytearray_object(cls: Type[bytearray], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, int):
        raise TypeError
    return cls(val)


@cast.register
def _cast_bytearray_str(cls: Type[bytearray], val: str, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# list
#

def _copy_list_object(r, it, ctx, T, i):
    for v in it:
        with ctx.traverse(i):
            r.append(cast(T, v, ctx=ctx))
        i += 1
    return r


@cast.register
def _cast_list_object(cls: Type[list], val, ctx, T=None):
    # assume T is not None or not isinstance(val, cls)
    if isinstance(val, Mapping):
        val = val.items()

    if T is None:
        return cls(val)

    if isinstance(val, cls):
        r = None
        it = iter(val)
        i = 0
        for v in it:
            with ctx.traverse(i):
                cv = cast(T, v, ctx=ctx)
                if cv is not v:
                    if i == 0:
                        r = cls()
                    else:
                        r = cls(itertools.islice(val, i))
                    r.append(cv)
                    break
                i += 1
        if r is None:
            return val
        else:
            return _copy_list_object(r, it, ctx, T, i + 1)
    else:
        return _copy_list_object(cls(), iter(val), ctx, T, 0)


#
# dict
#

def _copy_dict_object(r, it, ctx, KT, VT):
    for k, v in it:
        with ctx.traverse(k):
            r[cast(KT, k, ctx=ctx)] = cast(VT, v, ctx=ctx)
    return r


@cast.register
def _cast_dict_object(cls: Type[dict], val, ctx, K=None, V=None):
    if K is None:
        return cls(val)

    if isinstance(val, cls):
        r = None
        it = val.items()
        i = 0
        for k, v in it:
            with ctx.traverse(k):
                ck = cast(K, k, ctx=ctx)
                cv = cast(V, v, ctx=ctx)
                if ck is not k or cv is not v:
                    if i == 0:
                        r = cls()
                    else:
                        r = cls(itertools.islice(val.items(), i))
                    r[ck] = cv
                    break
                i += 1
        if r is None:
            return val
        else:
            return _copy_dict_object(r, it, ctx, K, V)
    else:
        if isinstance(val, Mapping):
            val = val.items()
        return _copy_dict_object(cls(), val, ctx, K, V)


#
# set
#

def _copy_set_object(r, it, ctx, T):
    for v in it:
        with ctx.traverse(v):
            r.add(cast(T, v, ctx=ctx))
    return r


@cast.register
def _cast_set_object(cls: Type[set], val, ctx, T=None):
    # assume T is not None or not isinstance(val, cls)
    if T is None:
        return cls(val)

    if isinstance(val, cls):
        r = None
        it = iter(val)
        i = 0
        for v in it:
            with ctx.traverse(v):
                cv = cast(T, v, ctx=ctx)
                if cv is not v:
                    if i == 0:
                        r = cls()
                    else:
                        # assume repeatable order
                        r = cls(itertools.islice(val, i))
                    r.add(cv)
                    break
                i += 1
        if r is None:
            return val
        else:
            return _copy_set_object(r, it, ctx, T)
    else:
        return _copy_set_object(cls(), iter(val), ctx, T)


#
# frozenset
#

def _copy_frozenset_object(r, cls, it, ctx, T):
    for v in it:
        with ctx.traverse(v):
            r.add(cast(T, v, ctx=ctx))
    return cls(r)


@cast.register
def _cast_frozenset_object(cls: Type[frozenset], val, ctx, T=None):
    # assume T is not None or not isinstance(val, cls)
    if T is None:
        return cls(val)

    if isinstance(val, cls):
        r = None
        it = iter(val)
        i = 0
        for v in it:
            with ctx.traverse(v):
                cv = cast(T, v, ctx=ctx)
                if cv is not v:
                    if i == 0:
                        r = {cv}
                    else:
                        # assume repeatable order
                        r = set(itertools.islice(val, i))
                        r.add(cv)
                    break
                i += 1
        if r is None:
            return val
        else:
            return _copy_frozenset_object(r, cls, it, ctx, T)
    else:
        return _copy_frozenset_object(set(), cls, iter(val), ctx, T)


#
# tuple
#

def _copy_homo_tuple_object(r, cls, it, ctx, T, i):
    for v in it:
        with ctx.traverse(i):
            r.append(cast(T, v, ctx=ctx))
        i += 1
    return cls(r)


def _copy_hetero_tuple_object(r, cls, it, ctx, i):
    for v, T in it:
        with ctx.traverse(i):
            r.append(cast(T, v, ctx=ctx))
        i += 1
    return cls(r)


@cast.register
def _cast_tuple_object(cls: Type[tuple], val, ctx, *Ts):
    # assume Ts or not isinstance(val, cls)
    if isinstance(val, Mapping):
        val = val.items()
    elif isinstance(val, complex):
        val = val.real, val.imag

    if not Ts:
        return cls(val)
    elif Ts[-1] == ...:
        T = Ts[0]
        if isinstance(val, cls):
            r = None
            it = iter(val)
            i = 0
            for v in it:
                with ctx.traverse(i):
                    cv = cast(T, v, ctx=ctx)
                    if cv is not v:
                        if i == 0:
                            r = [cv]
                        else:
                            r = list(itertools.islice(val, i))
                            r.append(cv)
                        break
                    i += 1
            if r is None:
                return val
            else:
                return _copy_homo_tuple_object(r, cls, it, ctx, T, i + 1)
        else:
            return _copy_homo_tuple_object([], cls, iter(val), ctx, T, 0)
    else:
        if Ts[0] == ():
            Ts = ()
        if isinstance(val, cls):
            if len(val) != len(Ts):
                raise TypeError('length mismatch')
            r = None
            it = zip(val, Ts)
            i = 0
            for v, T in it:
                with ctx.traverse(i):
                    cv = cast(T, v, ctx=ctx)
                    if cv is not v:
                        if i == 0:
                            r = [cv]
                        else:
                            r = list(itertools.islice(val, i))
                            r.append(cv)
                        break
                    i += 1
            if r is None:
                return val
            else:
                return _copy_hetero_tuple_object(r, cls, it, ctx, i + 1)
        else:
            r = []
            it = iter(val)
            for i, T in enumerate(Ts):
                with ctx.traverse(i):
                    try:
                        v = next(it)
                    except StopIteration:
                        raise TypeError('length mismatch')
                    r.append(cast(T, v, ctx=ctx))
            for _ in it:
                raise TypeError('length mismatch')
            return cls(r)


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


@cast.register
def _cast_Union_object(cls, val, ctx, *Ts) -> Union:
    vcls = val.__class__
    types = []  # [(kind, distance, index, type)]
    for i, T in enumerate(Ts):
        origin = get_origin(T) or T
        try:
            func = _dispatch(origin, vcls)
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
            return cast(T, val)
        except:
            continue
    else:
        raise TypeError("no match")


#
# datetime.datetime
#


@cast.register
def _cast_datetime_object(cls: Type[datetime.datetime], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, (int, float)):
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


ISO_DATE_HEAD = r'(?P<Y>\d{4})(-(?P<m>\d{1,2})(-(?P<D>\d{1,2})'
ISO_DATE_TAIL = r')?)?'
ISO_TIME = r'(?P<H>\d{1,2}):(?P<M>\d{1,2})(:(?P<S>\d{1,2}([.]\d*)?))?(?P<tzd>[+-](?P<tzh>\d{1,2}):(?P<tzm>\d{1,2})|Z)?'
ISO_DURATION = r'(?P<sgn>[+-])?P?((?P<W>\d+)[Ww])?((?P<D>\d+)[Dd])?T?((?P<H>\d+)[Hh])?((?P<M>\d+)[Mm])?((?P<S>\d+([.]\d*)?)[Ss]?)?'
ISO_PATTERN1 = re.compile(
    ISO_DATE_HEAD + r'([T ](' + ISO_TIME + r')?)?' + ISO_DATE_TAIL + '$')
ISO_PATTERN2 = re.compile(ISO_DATE_HEAD + ISO_DATE_TAIL + '$')
ISO_PATTERN3 = re.compile(ISO_TIME + '$')
ISO_PATTERN4 = re.compile(ISO_DURATION + '$')


def _parse_isotzinfo(m):
    if m.group('tzd'):
        if m.group('tzd') in ('Z', '+00:00', '-00:00'):
            tzinfo = datetime.timezone.utc
        else:
            offset = int(m.group('tzh')) * 60 + int(m.group('tzm'))
            if m.group('tzd').startswith('-'):
                offset = -offset
            tzinfo = datetime.timezone(datetime.timedelta(minutes=offset))
    else:
        tzinfo = None
    return tzinfo


def _parse_isotime(cls, m):
    hour, min, sec = m.group('H', 'M', 'S')
    hour = int(hour)
    min = int(min) if min else 0
    sec = float(sec) if sec else 0.0

    tzinfo = _parse_isotzinfo(m)
    return cls(hour, min, int(sec), int((sec % 1.0) * 1000000), tzinfo=tzinfo)


def _parse_isodate(cls, m):
    return datetime.date(*map(lambda x: 1 if x is None else int(x), m.group('Y', 'm', 'D')))


def _parse_isoduration(cls, m):
    sign, week, day, hour, min, sec = m.group('sgn', 'W', 'D', 'H', 'M', 'S')
    week = int(week) if week else 0
    day = int(day) if day else 0
    hour = int(hour) if hour else 0
    min = int(min) if min else 0
    sec = float(sec) if sec else 0.0

    td = cls(weeks=week, days=day, hours=hour, minutes=min, seconds=sec)
    return -td if sign == '-' else td


@cast.register
def _cast_datetime_str(cls: Type[datetime.datetime], val: str, ctx):
    if ctx.datetime_format == 'iso':
        m = ISO_PATTERN1.match(val.strip())
        if m is None:
            raise ValueError()

        date = _parse_isodate(datetime.date, m)

        if m.group('H'):
            time = _parse_isotime(datetime.time, m)
        else:
            time = datetime.time(tzinfo=_parse_isotzinfo(m))

        return cls.combine(date, time)
    elif ctx.datetime_format == 'timestamp':
        return cast(cls, float(val), ctx=ctx)
    elif ctx.datetime_format == 'http' or ctx.datetime_format == 'email':
        dt = parsedate_to_datetime(val.strip())
        if cls is not datetime.datetime:
            dt = cls.combine(dt.date(), dt.timetz())
        return dt
    else:
        return cls.strptime(val, ctx.datetime_format)


@cast.register
def _cast_float_datetime(cls: Type[float], val: datetime.datetime, ctx):
    return cls(val.timestamp())


@cast.register
def _cast_int_datetime(cls: Type[int], val: datetime.datetime, ctx):
    ts = val.timestamp()
    r = cls(ts)
    if not ctx.lossy_conversion and r != ts:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


WDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
MON = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


@cast.register
def _cast_str_datetime(cls: Type[str], val: datetime.datetime, ctx):
    if ctx.datetime_format == 'iso':
        r = val.isoformat()
        return cls(r[:-6] + 'Z') if r.endswith('+00:00') else cls(r)
    elif ctx.datetime_format == 'timestamp':
        if val.microsecond > 0:
            return cls(val.timestamp())
        else:
            return cls(int(val.timestamp()))
    elif ctx.datetime_format == 'http' or ctx.datetime_format == 'email':
        if ctx.datetime_format == 'http':
            if val.tzinfo and val.utcoffset() != datetime.timedelta():
                val = val.replace(
                    tzinfo=datetime.timezone.utc) - val.utcoffset()
            format = '%s, %%d %s %%Y %%H:%%M:%%S GMT'
        else:
            TZ = (' %%z' if val.utcoffset() != datetime.timedelta()
                  else ' GMT') if val.tzinfo else ''
            format = '%s, %%d %s %%Y %%H:%%M:%%S' + TZ
        format = format % (WDAY[val.weekday()], MON[val.month - 1])
        return cls(val.strftime(format))
    else:
        return cls(val.strftime(ctx.datetime_format))


#
# datetime.date
#


@cast.register
def _cast_date_object(cls: Type[datetime.date], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, datetime.datetime):  # datetime is subclass of date
        if not ctx.lossy_conversion and (val.tzinfo or val.time() != datetime.time()):
            raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
        return cls(val.year, val.month, val.day)
    elif isinstance(val, datetime.date):
        return cls(val.year, val.month, val.day)
    else:
        return cls(*val)


@cast.register
def _cast_date_str(cls: Type[datetime.date], val: str, ctx):
    if ctx.date_format == 'iso':
        m = ISO_PATTERN2.match(val.strip())
        if m is None:
            raise ValueError()
        return _parse_isodate(cls, m)
    else:
        dt = datetime.datetime.strptime(val, ctx.date_format)
        return cls(dt.year, dt.month, dt.day)


@cast.register
def _cast_str_date(cls: Type[str], val: datetime.date, ctx):
    if ctx.date_format == 'iso':
        return cls(val.isoformat())
    else:
        return cls(val.strftime(ctx.date_format))


#
# datetime.time
#


@cast.register
def _cast_time_object(cls: Type[datetime.time], val, ctx):
    # assume not isinstance(val, cls)
    if isinstance(val, datetime.time):
        return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
    elif isinstance(val, datetime.datetime):
        if not ctx.lossy_conversion:
            raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
        t = val.timetz()
        if t.__class__ is cls:
            return t
        return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
    else:
        return cls(*val)


@cast.register
def _cast_time_str(cls: Type[datetime.time], val: str, ctx):
    if ctx.time_format == 'iso':
        m = ISO_PATTERN3.match(val.strip())
        if m is None:
            raise ValueError()
        return _parse_isotime(cls, m)
    else:
        dt = datetime.datetime.strptime(val, ctx.time_format)
        return cls(dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=dt.tzinfo)


@cast.register
def _cast_str_time(cls: Type[str], val: datetime.time, ctx):
    if ctx.time_format == 'iso':
        return cls(val.isoformat())
    else:
        return cls(val.strftime(ctx.time_format))


#
# datetime.timedelta
#


@cast.register
def _cast_timedelta_object(cls: Type[datetime.timedelta], val, ctx):
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


@cast.register
def _cast_float_timedelta(cls: Type[float], val: datetime.timedelta, ctx):
    return cls(val.total_seconds())


@cast.register
def _cast_int_timedelta(cls: Type[int], val: datetime.timedelta, ctx):
    td = val.total_seconds()
    r = cls(td)
    if not ctx.lossy_conversion and r != td:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


@cast.register
def _cast_str_timedelta(cls: Type[str], val: datetime.timedelta, ctx):
    r = []
    if val.days < 0:
        r.append('-P')
        val = -val
    else:
        r.append('P')
    if val.days:
        r.append(f'{val.days}D')
    if val.seconds or val.microseconds:
        r.append('T')
        min, sec = divmod(val.seconds, 60)
        hour, min = divmod(min, 60)
        if hour:
            r.append(f'{hour}H')
        if min:
            r.append(f'{min}M')
        if val.microseconds:
            sec += val.microseconds / 1000000
        if sec:
            r.append(f'{sec}S')
    return cls(''.join(r))


#
# enum.Enum
#


@cast.register
def _cast_Enum_object(cls: Type[enum.Enum], val, ctx):
    # assume not isinstance(val, cls)
    return cls(val)


@cast.register
def _cast_Enum_str(cls: Type[enum.Enum], val: str, ctx):
    return getattr(cls, val)


@cast.register
def _cast_str_Enum(cls: Type[str], val: enum.Enum, ctx):
    return val.name


#
# enum.IntEnum
#


@cast.register
def _cast_IntEnum_int(cls: Type[enum.IntEnum], val: int, ctx):
    return cls(val)


@cast.register
def _cast_IntEnum_str(cls: Type[enum.IntEnum], val: str, ctx):
    return getattr(cls, val)


@cast.register
def _cast_str_IntEnum(cls: Type[str], val: enum.IntEnum, ctx):
    return val.name


#
# enum.Flag
#


@cast.register
def _cast_Flag_Flag(cls: Type[enum.Flag], val: enum.Flag, ctx):
    # assume not isinstance(val, cls)
    return cls(val)


@cast.register
def _cast_Flag_int(cls: Type[enum.Flag], val: int, ctx):
    return cls(val)


@cast.register
def _cast_int_Flag(cls: Type[int], val: enum.Flag, ctx):
    return cls(val.value)


@cast.register
def _cast_str_Flag(cls: Type[str], val: enum.Flag, ctx):
    raise TypeError


#
# enum.IntFlag
#


@cast.register
def _cast_IntFlag_int(cls: Type[enum.IntFlag], val: int, ctx):
    return cls(val)


@cast.register
def _cast_str_IntFlag(cls: Type[str], val: enum.IntFlag, ctx):
    raise TypeError


#
# typing.Literal
#


@cast.register
def _cast_Literal_object(cls, val, ctx, *literals) -> Literal:
    for literal in literals:
        if literal == val:
            return literal
    else:
        raise ValueError(f"One of {literals!r} required, but {val!r} is given")


#
# type
#

@cast.register
def _cast_type_type(cls, val: type, ctx, T=None) -> type:
    if T and T is not Any and not issubclass(val, T):
        raise TypeError
    return val


@cast.register
def _cast_type_str(cls, val: str, ctx, T=None) -> type:
    spec = val.rsplit('.', maxsplit=1)
    if len(spec) == 1:
        modname = 'builtins'
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
            spec = modname.rsplit('.', maxsplit=1)
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


@cast.register
def _cast_str_type(cls: Type[str], val: type, ctx):
    return f"{val.__module__}.{val.__qualname__}"
