from datetime import date, datetime, time, timezone

import pytest

from typeable import typecast


def test_str():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    with pytest.raises(TypeError):
        typecast(time, "1970-01-01T00:00:00.000Z")
    with pytest.raises(TypeError):
        typecast(time, "1970-01-01T")

    assert typecast(time, "00:00:00.000Z") == aware_epoch.timetz()
    assert typecast(time, "00:00:00.000+00:00") == aware_epoch.timetz()
    assert typecast(time, "00:00:00.000-00:00") == aware_epoch.timetz()
    assert typecast(time, "09:00:00.000+09:00") == aware_epoch.timetz()
    assert typecast(time, "00:00:00.000") == naive_epoch.time()
    assert typecast(time, "0:00:00.000") == naive_epoch.time()
    assert typecast(time, "00:0:00.000") == naive_epoch.time()
    assert typecast(time, "00:00:0.000") == naive_epoch.time()
    assert typecast(time, "00:00:0.") == naive_epoch.time()
    assert typecast(time, "00:00:0") == naive_epoch.time()
    assert typecast(time, "0:0") == naive_epoch.time()

    # empty string
    with pytest.raises(TypeError):
        typecast(time, "")
    with pytest.raises(TypeError):
        typecast(time, " ")


def test_datetime():
    dt = datetime.utcnow()  # naive
    with pytest.raises(TypeError):
        typecast(time, dt)


def test_date():
    with pytest.raises(TypeError):
        typecast(time, date(1970, 1, 1))


def test_time():
    t = time(12, 34, 56, 789)
    assert typecast(time, t) == t


def test_custom():
    class Time(time):
        pass

    t = datetime.utcnow().time()
    assert typecast(Time, t) == t
