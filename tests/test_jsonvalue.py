from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from typeable import JsonValue, localcontext, typecast


def test_embedded():
    data = {"a": ["0", True, 2, 3.14], "b": range(4)}
    expected = {"a": ["0", True, 2, 3.14], "b": [0, 1, 2, 3]}
    assert typecast(JsonValue, data) == expected


def test_simple():
    assert typecast(JsonValue, None) is None
    assert typecast(JsonValue, True) is True
    assert typecast(JsonValue, False) is False
    assert typecast(JsonValue, 123) == 123
    assert typecast(JsonValue, 123.456) == 123.456
    assert typecast(JsonValue, "hello") == "hello"
    assert typecast(JsonValue, "") == ""
    assert typecast(JsonValue, []) == []
    assert typecast(JsonValue, {}) == {}
    assert typecast(JsonValue, ()) == ()


def test_Iterable():
    assert typecast(JsonValue, range(4)) == [0, 1, 2, 3]


def test_dataclass():
    @dataclass
    class X:
        i: int

    x = X(i=3)
    v = [x]
    assert typecast(JsonValue, x) == {"i": 3}
    assert typecast(JsonValue, v) == [{"i": 3}]


def test_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert typecast(JsonValue, naive_epoch) == naive_epoch.isoformat()
    assert typecast(JsonValue, aware_epoch) == "1970-01-01T00:00:00Z"


def test_date():
    d = date(1970, 1, 1)

    assert typecast(JsonValue, d) == "1970-01-01"


def test_time():
    t = time(12, 34, 56, 789)

    assert typecast(JsonValue, t) == "12:34:56.000789"


def test_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert typecast(JsonValue, td) == "P12DT9H36M7S"
    assert typecast(JsonValue, -td) == "-P12DT9H36M7S"

    td = timedelta(hours=9, seconds=7)
    assert typecast(JsonValue, td) == "PT9H7S"
    assert typecast(JsonValue, -td) == "-PT9H7S"

    td = timedelta(days=12)
    assert typecast(JsonValue, td) == "P12D"
    assert typecast(JsonValue, -td) == "-P12D"

    td = timedelta(days=12, seconds=7, microseconds=1)
    assert typecast(JsonValue, td) == "P12DT7.000001S"
    assert typecast(JsonValue, -td) == "-P12DT7.000001S"

    td = timedelta(days=12, seconds=60)
    assert typecast(JsonValue, td) == "P12DT1M"
    assert typecast(JsonValue, -td) == "-P12DT1M"
