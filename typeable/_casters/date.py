from datetime import date, datetime
import re

from .._typecast import Typecast, typecast
from .datetime import ISO_DATE_HEAD, ISO_DATE_TAIL, _parse_isodate

ISO_DATE = re.compile(ISO_DATE_HEAD + ISO_DATE_TAIL + "$")


@typecast.register
def date_from_str(typecast: Typecast, cls: type[date], val: str) -> date:
    m = ISO_DATE.match(val.strip())
    if m is None:
        raise TypeError()
    return _parse_isodate(cls, m)


@typecast.register
def date_from_date(typecast: Typecast, cls: type[date], val: date) -> date:
    # for custom date
    return cls(val.year, val.month, val.day)


typecast.forbid(date, datetime)
