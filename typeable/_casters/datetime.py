from datetime import date, datetime, time, timedelta, timezone
import re

from .._typecast import Typecast, typecast


ISO_DATE_HEAD = r"(?P<Y>\d{4})(-(?P<m>\d{1,2})(-(?P<D>\d{1,2})"
ISO_DATE_TAIL = r")?)?"
ISO_TIME = r"(?P<H>\d{1,2}):(?P<M>\d{1,2})(:(?P<S>\d{1,2}([.]\d*)?))?(?P<tzd>[+-](?P<tzh>\d{1,2}):(?P<tzm>\d{1,2})|Z)?"
ISO_DATE_TIME = re.compile(
    ISO_DATE_HEAD + r"([T ](" + ISO_TIME + r")?)?" + ISO_DATE_TAIL + "$"
)


def _parse_isotzinfo(m):
    if m.group("tzd"):
        if m.group("tzd") in ("Z", "+00:00", "-00:00"):
            tzinfo = timezone.utc
        else:
            offset = int(m.group("tzh")) * 60 + int(m.group("tzm"))
            if m.group("tzd").startswith("-"):
                offset = -offset
            tzinfo = timezone(timedelta(minutes=offset))
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
    return date(*map(lambda x: 1 if x is None else int(x), m.group("Y", "m", "D")))


@typecast.register
def datetime_from_str(typecast: Typecast, cls: type[datetime], val: str) -> datetime:
    m = ISO_DATE_TIME.match(val.strip())
    if m is None:
        raise TypeError()

    d = _parse_isodate(date, m)

    if m.group("H"):
        t = _parse_isotime(time, m)
    else:
        t = time(tzinfo=_parse_isotzinfo(m))

    return cls.combine(d, t)


@typecast.register
def datetime_from_date(typecast: Typecast, cls: type[datetime], val: date) -> datetime:
    if isinstance(val, datetime):
        # for custom datetime
        return cls.combine(val.date(), val.timetz())
    return cls.combine(val, time())
