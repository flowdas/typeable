from datetime import datetime, date, time, timedelta, timezone

import pytest

from typeable import deepcast, localcontext


#
# datetime
#


def test_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # int, float
    for T in (int, float):
        t = T(0)
        assert deepcast(datetime, t) == aware_epoch
        with localcontext(naive_timestamp=True):
            assert deepcast(datetime, t) == naive_epoch

    # str - iso
    with pytest.raises(ValueError):
        deepcast(datetime, "1970-01-01T00:00:00.000Z #")
    assert deepcast(datetime, "1970-01-01T00:00:00.000Z") == aware_epoch
    assert deepcast(datetime, "1970-01-01T00:00:00.000+00:00") == aware_epoch
    assert deepcast(datetime, "1970-01-01T00:00:00.000-00:00") == aware_epoch
    assert deepcast(datetime, "1970-01-01T09:00:00.000+09:00") == aware_epoch
    assert deepcast(datetime, "1969-12-31T15:00:00.000-09:00") == aware_epoch
    assert deepcast(datetime, "1970-01-01T00:00:00.000") == naive_epoch
    assert deepcast(datetime, "1970-1-01T00:00:00.000") == naive_epoch
    assert deepcast(datetime, "1970-01-1T00:00:00.000") == naive_epoch
    assert deepcast(datetime, "1970-01-01T0:00:00.000") == naive_epoch
    assert deepcast(datetime, "1970-01-01T00:0:00.000") == naive_epoch
    assert deepcast(datetime, "1970-01-01T00:00:0.000") == naive_epoch
    assert deepcast(datetime, "1970-01-01T00:00:0.") == naive_epoch
    assert deepcast(datetime, "1970-01-01T00:00:0") == naive_epoch
    assert deepcast(datetime, "1970-1-1T0:0") == naive_epoch
    assert deepcast(datetime, "1970-1-1 0:0") == naive_epoch
    assert deepcast(datetime, "1970-1-1T") == naive_epoch
    assert deepcast(datetime, "1970-1-1") == naive_epoch
    assert deepcast(datetime, " 1970-1-1 ") == naive_epoch

    # str - timestamp
    with localcontext(datetime_format="timestamp") as ctx:
        assert deepcast(datetime, "0") == aware_epoch
        ctx.naive_timestamp = True
        assert deepcast(datetime, "0") == naive_epoch

    # str - http & email
    with localcontext() as ctx:
        for format in ("http", "email"):
            ctx.datetime_format = format
            expected = datetime(
                2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9))
            )
            assert deepcast(datetime, "Mon, 07 Mar 2016 00:04:24 +0900") == expected

    # str - stptime
    with localcontext(datetime_format=r"%Y-%m-%dT%H:%M:%S.%f%z"):
        assert deepcast(datetime, "1970-01-01T00:00:00.000000+0000") == aware_epoch

    # empty string
    with pytest.raises(ValueError):
        deepcast(datetime, "")
    with pytest.raises(ValueError):
        deepcast(datetime, " ")

    # None
    with pytest.raises(TypeError):
        deepcast(datetime, None)

    # date
    d = date(1970, 1, 1)
    assert deepcast(datetime, d) == naive_epoch

    # time
    with pytest.raises(TypeError):
        deepcast(datetime, time())

    # datetime
    dt = datetime.utcnow()  # naive
    assert deepcast(datetime, dt) == dt

    dt = datetime.now(timezone.utc)  # aware
    assert deepcast(datetime, dt) == dt

    # custom datetime
    class DT1(datetime):
        pass

    class DT2(datetime):
        pass

    assert deepcast(DT1, DT2.today()).__class__ is DT1

    with localcontext(datetime_format="http"):
        expected = DT1(2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9)))
        assert deepcast(DT1, "Mon, 07 Mar 2016 00:04:24 +0900") == expected


def test_float_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert deepcast(float, naive_epoch) == naive_epoch.timestamp()
    assert deepcast(float, aware_epoch) == 0


def test_int_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert deepcast(int, naive_epoch) == naive_epoch.timestamp()
    assert deepcast(int, aware_epoch) == 0

    with localcontext(lossy_conversion=False):
        assert deepcast(int, naive_epoch) == naive_epoch.timestamp()
        with pytest.raises(ValueError):
            deepcast(int, datetime(1970, 1, 1, 0, 0, 0, 1))


def test_bool_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)

    with pytest.raises(TypeError):
        deepcast(bool, naive_epoch)


def test_str_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # iso
    assert deepcast(str, naive_epoch) == naive_epoch.isoformat()
    assert deepcast(str, aware_epoch) == "1970-01-01T00:00:00Z"

    # http
    dt = datetime(2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9)))
    with localcontext(datetime_format="http"):
        assert deepcast(str, dt) == "Sun, 06 Mar 2016 15:04:24 GMT"
        assert (
            deepcast(str, datetime(2016, 3, 7, 0, 4, 24))
            == "Mon, 07 Mar 2016 00:04:24 GMT"
        )

    # email
    with localcontext(datetime_format="email"):
        assert deepcast(str, dt) == "Mon, 07 Mar 2016 00:04:24 +0900"

    # timestamp
    with localcontext(datetime_format="timestamp"):
        assert deepcast(str, naive_epoch) == str(int(naive_epoch.timestamp()))
        assert deepcast(str, aware_epoch) == "0"
        oneus = naive_epoch.replace(microsecond=1)
        assert deepcast(str, oneus) == str(oneus.timestamp())

    # strftime
    with localcontext(datetime_format="=%Y-%m-%dT%H:%M:%S.%f%z="):
        assert deepcast(str, aware_epoch) == "=1970-01-01T00:00:00.000000+0000="


#
# date
#


def test_date():
    # int, float
    for T in (int, float):
        t = T(0)
        with pytest.raises(TypeError):
            deepcast(date, t)

    # str - iso
    with pytest.raises(ValueError):
        deepcast(date, "1970-01-01T00:00:00.000Z")
    with pytest.raises(ValueError):
        deepcast(date, "1970-01-01T")

    assert deepcast(date, "1970-01-01") == date(1970, 1, 1)
    assert deepcast(date, "1969-12-31") == date(1969, 12, 31)
    assert deepcast(date, "1970-1-01") == date(1970, 1, 1)
    assert deepcast(date, "1970-01-1") == date(1970, 1, 1)
    assert deepcast(date, "1970-1-1") == date(1970, 1, 1)
    assert deepcast(date, " 1970-1-1 ") == date(1970, 1, 1)

    # str - stptime
    with localcontext(datetime_format=r"%Y-%m-%d"):
        assert deepcast(date, "1970-01-01") == date(1970, 1, 1)

    # empty string
    with pytest.raises(ValueError):
        deepcast(date, "")
    with pytest.raises(ValueError):
        deepcast(date, " ")

    # None
    with pytest.raises(TypeError):
        deepcast(date, None)

    # datetime
    dt = datetime.utcnow()  # naive
    assert deepcast(date, dt) == dt

    # time
    with pytest.raises(TypeError):
        deepcast(date, time())

    # date
    d = date(1970, 1, 1)
    assert deepcast(date, d) == d

    # custom date
    class Date(date):
        pass

    dt = datetime.utcnow()
    assert deepcast(Date, dt) == dt.date()

    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            deepcast(Date, dt.replace(tzinfo=timezone.utc))

    class Date2(date):
        pass

    dt = Date2.today()
    assert deepcast(Date, dt) == dt


def test_bool_from_date():
    d = date(1970, 1, 1)

    with pytest.raises(TypeError):
        deepcast(bool, d)


def test_str_from_date():
    d = date(1970, 1, 1)

    # iso
    assert deepcast(str, d) == "1970-01-01"

    # strftime
    with localcontext(date_format=r"=%Y-%m-%d="):
        assert deepcast(str, d) == "=1970-01-01="


#
# time
#


def test_time():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # int, float
    for T in (int, float):
        t = T(0)
        with pytest.raises(TypeError):
            deepcast(time, t)

    # str - iso
    with pytest.raises(ValueError):
        deepcast(time, "1970-01-01T00:00:00.000Z")
    with pytest.raises(ValueError):
        deepcast(time, "1970-01-01T")

    assert deepcast(time, "00:00:00.000Z") == aware_epoch.timetz()
    assert deepcast(time, "00:00:00.000+00:00") == aware_epoch.timetz()
    assert deepcast(time, "00:00:00.000-00:00") == aware_epoch.timetz()
    assert deepcast(time, "09:00:00.000+09:00") == aware_epoch.timetz()
    assert deepcast(time, "00:00:00.000") == naive_epoch.time()
    assert deepcast(time, "0:00:00.000") == naive_epoch.time()
    assert deepcast(time, "00:0:00.000") == naive_epoch.time()
    assert deepcast(time, "00:00:0.000") == naive_epoch.time()
    assert deepcast(time, "00:00:0.") == naive_epoch.time()
    assert deepcast(time, "00:00:0") == naive_epoch.time()
    assert deepcast(time, "0:0") == naive_epoch.time()

    # str - stptime
    with localcontext(time_format=r"%H:%M:%S.%f"):
        assert deepcast(time, "12:34:56.000789") == time(12, 34, 56, 789)

    # empty string
    with pytest.raises(ValueError):
        deepcast(time, "")
    with pytest.raises(ValueError):
        deepcast(time, " ")

    # None
    with pytest.raises(TypeError):
        deepcast(time, None)

    # datetime
    dt = datetime.utcnow()  # naive
    assert deepcast(time, dt) == dt.time()
    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            deepcast(time, dt)

    dt = datetime.now(timezone.utc)  # aware
    assert deepcast(time, dt) == dt.timetz()

    # date
    with pytest.raises(TypeError):
        deepcast(time, date(1970, 1, 1))

    # time
    t = time(12, 34, 56, 789)
    assert deepcast(time, t) == t

    # custom time
    class Time(time):
        pass

    t = datetime.utcnow().time()
    assert deepcast(Time, t) == t

    dt = datetime.utcnow()  # naive
    assert deepcast(Time, dt) == dt.time()


def test_bool_from_time():
    t = time(12, 34, 56, 789)

    with pytest.raises(TypeError):
        deepcast(bool, t)


def test_str_from_time():
    t = time(12, 34, 56, 789)

    # iso
    assert deepcast(str, t) == "12:34:56.000789"

    # strftime
    with localcontext(time_format=r"=%H:%M:%S.%f%z="):
        assert deepcast(str, t) == "=12:34:56.000789="


#
# timedelta
#


def test_timedelta():
    # int, float
    for T in (int, float):
        td = timedelta(days=12, hours=9, minutes=36, seconds=7)
        assert deepcast(timedelta, T(td.total_seconds())) == td

    # str
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)
    assert deepcast(timedelta, "P12DT9H36M7S") == td
    assert deepcast(timedelta, "+P12DT9H36M7S") == td
    assert deepcast(timedelta, "-P12DT9H36M7S") == -td
    assert deepcast(timedelta, "P12DT34567S") == td
    assert deepcast(timedelta, "PT1071367S") == td
    assert deepcast(timedelta, "-PT1071367S") == -td

    assert deepcast(timedelta, "12DT9H36M7S") == td
    assert deepcast(timedelta, "+12DT9H36M7S") == td
    assert deepcast(timedelta, "-12DT9H36M7S") == -td
    assert deepcast(timedelta, "12DT34567S") == td
    assert deepcast(timedelta, "T1071367S") == td
    assert deepcast(timedelta, "-T1071367S") == -td

    assert deepcast(timedelta, "12D9H36M7S") == td
    assert deepcast(timedelta, "+12D9H36M7S") == td
    assert deepcast(timedelta, "-12D9H36M7S") == -td
    assert deepcast(timedelta, "12D34567S") == td
    assert deepcast(timedelta, "1071367S") == td
    assert deepcast(timedelta, "-1071367S") == -td

    assert deepcast(timedelta, "12D9H36M7") == td
    assert deepcast(timedelta, "+12D9H36M7") == td
    assert deepcast(timedelta, "-12D9H36M7") == -td
    assert deepcast(timedelta, "12D34567") == td
    assert deepcast(timedelta, "1071367") == td
    assert deepcast(timedelta, "-1071367") == -td

    assert deepcast(timedelta, "12w") == timedelta(weeks=12)

    assert deepcast(timedelta, "") == timedelta()

    with pytest.raises(ValueError):
        deepcast(timedelta, "x")

    # None
    with pytest.raises(TypeError):
        deepcast(timedelta, None)

    # timedelta
    td = timedelta()
    assert deepcast(timedelta, td) == td

    # custom timedelta
    class TimeDelta(timedelta):
        pass

    td = timedelta()
    assert deepcast(TimeDelta, td) == td


def test_float_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert deepcast(float, td) == td.total_seconds()


def test_int_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert deepcast(int, td) == int(td.total_seconds())

    with localcontext(lossy_conversion=False):
        assert deepcast(int, td) == int(td.total_seconds())
        td = timedelta(days=12, hours=9, minutes=36, seconds=7, microseconds=1)
        with pytest.raises(ValueError):
            deepcast(int, td)


def test_bool_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    with pytest.raises(TypeError):
        deepcast(bool, td)


def test_str_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert deepcast(str, td) == "P12DT9H36M7S"
    assert deepcast(str, -td) == "-P12DT9H36M7S"

    td = timedelta(hours=9, seconds=7)
    assert deepcast(str, td) == "PT9H7S"
    assert deepcast(str, -td) == "-PT9H7S"

    td = timedelta(days=12)
    assert deepcast(str, td) == "P12D"
    assert deepcast(str, -td) == "-P12D"

    td = timedelta(days=12, seconds=7, microseconds=1)
    assert deepcast(str, td) == "P12DT7.000001S"
    assert deepcast(str, -td) == "-P12DT7.000001S"

    td = timedelta(days=12, seconds=60)
    assert deepcast(str, td) == "P12DT1M"
    assert deepcast(str, -td) == "-P12DT1M"
