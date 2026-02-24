from datetime import time
import re

from .._typecast import Typecast, typecast
from .datetime import ISO_TIME, _parse_isotime

ISO_PATTERN = re.compile(ISO_TIME + "$")


@typecast.register
def time_from_str(typecast: Typecast, cls: type[time], val: str) -> time:
    m = ISO_PATTERN.match(val.strip())
    if m is None:
        raise TypeError()
    return _parse_isotime(cls, m)


@typecast.register
def time_from_time(typecast: Typecast, cls: type[time], val: time) -> time:
    # for custom time
    return cls(val.hour, val.minute, val.second, val.microsecond, tzinfo=val.tzinfo)
