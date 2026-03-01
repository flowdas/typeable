from collections.abc import Iterable, Mapping
from datetime import date, datetime, time, timedelta
from enum import Enum, Flag

from .._typecast import JsonValue, Typecast, traverse, typecast


@typecast.register
def JsonValue_from_Mapping(
    typecast: Typecast, cls: type[JsonValue], val: Mapping
) -> JsonValue:
    return typecast(dict[str, JsonValue], val)  # type: ignore


@typecast.register
def JsonValue_from_Iterable(
    typecast: Typecast, cls: type[JsonValue], val: Iterable
) -> JsonValue:
    patch = {}
    for i, v in enumerate(val):
        with traverse(i):
            cv = typecast(JsonValue, v)
            if cv is not v:
                patch[i] = cv
    if patch:
        val = list(patch.get(i, v) for i, v in enumerate(val))
    if not isinstance(val, (list, tuple)):
        val = list(val)
    return val  # type: ignore


@typecast.register
def JsonValue_from_object(
    typecast: Typecast, cls: type[JsonValue], val: object
) -> JsonValue:
    return typecast(dict[str, JsonValue], val)  # type: ignore


@typecast.register
def JsonValue_from_datetime(typecast: Typecast, cls: type[JsonValue], val: datetime):
    r = val.isoformat()
    return r[:-6] + "Z" if r.endswith("+00:00") else r


@typecast.register
def JsonValue_from_date(typecast: Typecast, cls: type[JsonValue], val: date):
    return val.isoformat()


@typecast.register
def JsonValue_from_time(typecast: Typecast, cls: type[JsonValue], val: time):
    return val.isoformat()


@typecast.register
def JsonValue_from_timedelta(typecast: Typecast, cls: type[JsonValue], val: timedelta):
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
    return "".join(r)


@typecast.register
def JsonValue_from_type(typecast: Typecast, cls: type[JsonValue], val: type):
    if val.__module__ == "builtins":
        return val.__qualname__
    return f"{val.__module__}.{val.__qualname__}"


@typecast.register
def JsonValue_from_Enum(typecast: Typecast, cls: type[JsonValue], val: Enum):
    return typecast(JsonValue, val.value)


@typecast.register
def JsonValue_from_Flag(typecast: Typecast, cls: type[JsonValue], val: Flag):
    # Python 3.11 부터 Flag 는 Iterable 이다.
    # 무한 루프 방지용 캐스터를 등록한다.
    return typecast(JsonValue, val.value)
