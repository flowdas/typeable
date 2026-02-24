from datetime import date, datetime, time, timezone

import pytest

from typeable import typecast


def test_str():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    with pytest.raises(TypeError):
        typecast(datetime, "1970-01-01T00:00:00.000Z #")

    assert typecast(datetime, "1970-01-01T00:00:00.000Z") == aware_epoch
    assert typecast(datetime, "1970-01-01T00:00:00.000+00:00") == aware_epoch
    assert typecast(datetime, "1970-01-01T00:00:00.000-00:00") == aware_epoch
    assert typecast(datetime, "1970-01-01T09:00:00.000+09:00") == aware_epoch
    assert typecast(datetime, "1969-12-31T15:00:00.000-09:00") == aware_epoch
    assert typecast(datetime, "1970-01-01T00:00:00.000") == naive_epoch
    assert typecast(datetime, "1970-1-01T00:00:00.000") == naive_epoch
    assert typecast(datetime, "1970-01-1T00:00:00.000") == naive_epoch
    assert typecast(datetime, "1970-01-01T0:00:00.000") == naive_epoch
    assert typecast(datetime, "1970-01-01T00:0:00.000") == naive_epoch
    assert typecast(datetime, "1970-01-01T00:00:0.000") == naive_epoch
    assert typecast(datetime, "1970-01-01T00:00:0.") == naive_epoch
    assert typecast(datetime, "1970-01-01T00:00:0") == naive_epoch
    assert typecast(datetime, "1970-1-1T0:0") == naive_epoch
    assert typecast(datetime, "1970-1-1 0:0") == naive_epoch
    assert typecast(datetime, "1970-1-1T") == naive_epoch
    assert typecast(datetime, "1970-1-1") == naive_epoch
    assert typecast(datetime, " 1970-1-1 ") == naive_epoch

    # empty string
    with pytest.raises(TypeError):
        typecast(datetime, "")
    with pytest.raises(TypeError):
        typecast(datetime, " ")


def test_date():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    d = date(1970, 1, 1)
    assert typecast(datetime, d) == naive_epoch


def test_time():
    with pytest.raises(TypeError):
        typecast(datetime, time())


def test_datetime():
    dt = datetime.utcnow()  # naive
    assert typecast(datetime, dt) == dt

    dt = datetime.now(timezone.utc)  # aware
    assert typecast(datetime, dt) == dt


def test_custom():
    class DT1(datetime):
        pass

    class DT2(datetime):
        pass

    assert typecast(DT1, DT2.today()).__class__ is DT1
