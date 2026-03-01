from datetime import timedelta
import re

from .._typecast import Typecast, typecast

ISO_DURATION = re.compile(
    r"(?P<sgn>[+-])?P?((?P<W>\d+)[Ww])?((?P<D>\d+)[Dd])?T?((?P<H>\d+)[Hh])?((?P<M>\d+)[Mm])?((?P<S>\d+([.]\d*)?)[Ss]?)?$"
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


@typecast.register
def timedelta_from_str(typecast: Typecast, cls: type[timedelta], val: str) -> timedelta:
    m = ISO_DURATION.match(val.strip())
    if m is None:
        raise TypeError()
    return _parse_isoduration(cls, m)


@typecast.register
def timedelta_from_timedelta(
    typecast: Typecast, cls: type[timedelta], val: timedelta
) -> timedelta:
    # for custom timedelta
    return cls(days=val.days, seconds=val.seconds, microseconds=val.microseconds)
