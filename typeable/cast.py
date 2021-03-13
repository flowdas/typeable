# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import os
import cmath
from contextlib import contextmanager
import datetime
from email.utils import parsedate_to_datetime
import inspect
import math
import re
import sys
import weakref
from abc import get_cache_token
from collections.abc import (
    Mapping,
)
from functools import _find_impl
from numbers import Real, Number
from inspect import (
    signature,
)
from .typing import (
    Any,
    ForwardRef,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    _RECURSIVE_GUARD,
)

from .context import Context

__all__ = [
    'cast',
    'declare',
]

#
# declare
#


@contextmanager
def declare(name):
    ref = ForwardRef(name)
    yield ref
    frame = inspect.currentframe().f_back.f_back
    try:
        if _RECURSIVE_GUARD:
            ref._evaluate(frame.f_globals, frame.f_locals, set())
        else:
            ref._evaluate(frame.f_globals, frame.f_locals)
    finally:
        del frame

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
                if _RECURSIVE_GUARD:
                    evaled[i] = arg._evaluate(None, None, frozenset())
                else:
                    evaled[i] = arg._evaluate(None, None)
                changed = True
        except TypeError:
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


def cast(cls: Type[_T], val, *, ctx: Context = None) -> _T:
    origin = get_origin(cls) or cls
    func = _dispatch(origin, val.__class__)
    if ctx is None:
        ctx = Context()
    return func(origin, val, ctx, *_get_type_args(cls))


cast.register = _register
cast.dispatch = _dispatch


#
# object (fallback)
#


@cast.register
def _cast_object_object(cls: Type[object], val, ctx, *Ts):
    if cls is object:
        if isinstance(val, object):
            return object()
        raise TypeError
    return cls(val)

#
# None
#


@cast.register
def _cast_None_object(cls: Type[None], val, ctx):
    if val is None:
        return None
    raise TypeError(f"{val!r} is not None")

#
# bool
#


@cast.register
def _cast_bool_int(cls: Type[bool], val: int, ctx):
    if isinstance(val, bool):
        return cls(val)
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
    if ctx.lossy_conversion or isinstance(val, int) or not isinstance(val, Real):
        return cls(val)
    r = cls(val)
    if r != val:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


@cast.register
def _cast_int_bool(cls: Type[int], val: bool, ctx):
    if not ctx.bool_is_int:
        raise TypeError(f'ctx.bool_is_int={ctx.bool_is_int}')
    return cls(val)

#
# float
#


@cast.register
def _cast_float_object(cls: Type[float], val, ctx):
    if ctx.accept_nan:
        return cls(val)
    r = cls(val)
    if not math.isfinite(r):
        raise ValueError(f'ctx.accept_nan={ctx.accept_nan}')
    return r


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
    if ctx.accept_nan:
        return cls(val)
    r = cls(val)
    if not cmath.isfinite(r):
        raise ValueError(f'ctx.accept_nan={ctx.accept_nan}')
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
    if isinstance(val, int):
        raise TypeError
    return cls(val)


@cast.register
def _cast_bytearray_str(cls: Type[bytearray], val: str, ctx):
    return cls(val, encoding=ctx.bytes_encoding, errors=ctx.encoding_errors)


#
# list
#


@cast.register
def _cast_list_object(cls: Type[list], val, ctx, T=None):
    if isinstance(val, Mapping):
        val = val.items()
    if T is None:
        return cls(val)
    else:
        r = cls()
        for i, v in enumerate(val):
            with ctx.traverse(i):
                r.append(cast(T, v, ctx=ctx))
        return r

#
# dict
#


@cast.register
def _cast_dict_object(cls: Type[dict], val, ctx, K=None, V=None):
    if K is None:
        return cls(val)
    else:
        if isinstance(val, Mapping):
            val = val.items()
        r = cls()
        for k, v in val:
            with ctx.traverse(k):
                r[cast(K, k, ctx=ctx)] = cast(V, v, ctx=ctx)
        return r

#
# set
#


@cast.register
def _cast_set_object(cls: Type[set], val, ctx, T=None):
    if T is None:
        return cls(val)
    else:
        r = cls()
        for v in val:
            with ctx.traverse(v):
                r.add(cast(T, v, ctx=ctx))
        return r

#
# frozenset
#


@cast.register
def _cast_set_object(cls: Type[frozenset], val, ctx, T=None):
    if T is None:
        return cls(val)
    else:
        r = set()
        for v in val:
            with ctx.traverse(v):
                r.add(cast(T, v, ctx=ctx))
        return cls(r)

#
# tuple
#


@cast.register
def _cast_tuple_object(cls: Type[tuple], val, ctx, *Ts):
    if isinstance(val, Mapping):
        val = val.items()
    if not Ts:
        return cls(val)
    elif Ts[-1] == ...:
        r = []
        for i, v in enumerate(val):
            with ctx.traverse(i):
                r.append(cast(Ts[0], v, ctx=ctx))
        return cls(r)
    else:
        if Ts[0] == ():
            Ts = ()
        r = []
        it = iter(val)
        for i, T in enumerate(Ts):
            with ctx.traverse(i):
                try:
                    v = next(it)
                except StopIteration:
                    raise TypeError('length mismatch')
                r.append(cast(T, v, ctx=ctx))
        try:
            with ctx.traverse(len(Ts)):
                next(it)
                raise TypeError('length mismatch')
        except StopIteration:
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

    return len(m1) + len(m2) - 2*n


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
    if issubclass(cls, bool):
        raise TypeError
    ts = val.timestamp()
    r = cls(ts)
    if ctx.lossy_conversion:
        return r
    if r != ts:
        raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
    return r


WDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
MON = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


@cast.register
def _cast_str_datetime(cls: Type[str], val: datetime.datetime, ctx):
    if ctx.datetime_format == 'iso':
        r = val.isoformat()
        return cls(r[:-6]+'Z') if r.endswith('+00:00') else cls(r)
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
    if isinstance(val, datetime.time):
        return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
    elif isinstance(val, datetime.datetime):
        if not ctx.lossy_conversion:
            raise ValueError(f'ctx.lossy_conversion={ctx.lossy_conversion}')
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
    if issubclass(cls, bool):
        raise TypeError
    td = val.total_seconds()
    r = cls(td)
    if ctx.lossy_conversion:
        return r
    if r != td:
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
