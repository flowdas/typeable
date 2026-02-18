from datetime import date, datetime, time, timedelta, timezone

import pytest

from typeable import localcontext, typecast

#
# datetime
#


def test_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # int, float
    for T in (int, float):
        t = T(0)
        assert typecast(datetime, t) == aware_epoch
        with localcontext(naive_timestamp=True):
            assert typecast(datetime, t) == naive_epoch

    # str - iso
    with pytest.raises(ValueError):
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

    # str - timestamp
    with localcontext(datetime_format="timestamp") as ctx:
        assert typecast(datetime, "0") == aware_epoch
        ctx.naive_timestamp = True
        assert typecast(datetime, "0") == naive_epoch

    # str - http & email
    with localcontext() as ctx:
        for format in ("http", "email"):
            ctx.datetime_format = format
            expected = datetime(
                2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9))
            )
            assert typecast(datetime, "Mon, 07 Mar 2016 00:04:24 +0900") == expected

    # str - stptime
    with localcontext(datetime_format=r"%Y-%m-%dT%H:%M:%S.%f%z"):
        assert typecast(datetime, "1970-01-01T00:00:00.000000+0000") == aware_epoch

    # empty string
    with pytest.raises(ValueError):
        typecast(datetime, "")
    with pytest.raises(ValueError):
        typecast(datetime, " ")

    # None
    with pytest.raises(TypeError):
        typecast(datetime, None)

    # date
    d = date(1970, 1, 1)
    assert typecast(datetime, d) == naive_epoch

    # time
    with pytest.raises(TypeError):
        typecast(datetime, time())

    # datetime
    dt = datetime.utcnow()  # naive
    assert typecast(datetime, dt) == dt

    dt = datetime.now(timezone.utc)  # aware
    assert typecast(datetime, dt) == dt

    # custom datetime
    class DT1(datetime):
        pass

    class DT2(datetime):
        pass

    assert typecast(DT1, DT2.today()).__class__ is DT1

    with localcontext(datetime_format="http"):
        expected = DT1(2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9)))
        assert typecast(DT1, "Mon, 07 Mar 2016 00:04:24 +0900") == expected


def test_float_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert typecast(float, naive_epoch) == naive_epoch.timestamp()
    assert typecast(float, aware_epoch) == 0


def test_int_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert typecast(int, naive_epoch) == naive_epoch.timestamp()
    assert typecast(int, aware_epoch) == 0

    with localcontext(lossy_conversion=False):
        assert typecast(int, naive_epoch) == naive_epoch.timestamp()
        with pytest.raises(ValueError):
            typecast(int, datetime(1970, 1, 1, 0, 0, 0, 1))


def test_bool_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)

    with pytest.raises(TypeError):
        typecast(bool, naive_epoch)


def test_str_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # iso
    assert typecast(str, naive_epoch) == naive_epoch.isoformat()
    assert typecast(str, aware_epoch) == "1970-01-01T00:00:00Z"

    # http
    dt = datetime(2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9)))
    with localcontext(datetime_format="http"):
        assert typecast(str, dt) == "Sun, 06 Mar 2016 15:04:24 GMT"
        assert (
            typecast(str, datetime(2016, 3, 7, 0, 4, 24))
            == "Mon, 07 Mar 2016 00:04:24 GMT"
        )

    # email
    with localcontext(datetime_format="email"):
        assert typecast(str, dt) == "Mon, 07 Mar 2016 00:04:24 +0900"

    # timestamp
    with localcontext(datetime_format="timestamp"):
        assert typecast(str, naive_epoch) == str(int(naive_epoch.timestamp()))
        assert typecast(str, aware_epoch) == "0"
        oneus = naive_epoch.replace(microsecond=1)
        assert typecast(str, oneus) == str(oneus.timestamp())

    # strftime
    with localcontext(datetime_format="=%Y-%m-%dT%H:%M:%S.%f%z="):
        assert typecast(str, aware_epoch) == "=1970-01-01T00:00:00.000000+0000="


#
# date
#


def test_date():
    # int, float
    for T in (int, float):
        t = T(0)
        with pytest.raises(TypeError):
            typecast(date, t)

    # str - iso
    with pytest.raises(ValueError):
        typecast(date, "1970-01-01T00:00:00.000Z")
    with pytest.raises(ValueError):
        typecast(date, "1970-01-01T")

    assert typecast(date, "1970-01-01") == date(1970, 1, 1)
    assert typecast(date, "1969-12-31") == date(1969, 12, 31)
    assert typecast(date, "1970-1-01") == date(1970, 1, 1)
    assert typecast(date, "1970-01-1") == date(1970, 1, 1)
    assert typecast(date, "1970-1-1") == date(1970, 1, 1)
    assert typecast(date, " 1970-1-1 ") == date(1970, 1, 1)

    # str - stptime
    with localcontext(datetime_format=r"%Y-%m-%d"):
        assert typecast(date, "1970-01-01") == date(1970, 1, 1)

    # empty string
    with pytest.raises(ValueError):
        typecast(date, "")
    with pytest.raises(ValueError):
        typecast(date, " ")

    # None
    with pytest.raises(TypeError):
        typecast(date, None)

    # datetime
    dt = datetime.utcnow()  # naive
    assert typecast(date, dt) == dt

    # time
    with pytest.raises(TypeError):
        typecast(date, time())

    # date
    d = date(1970, 1, 1)
    assert typecast(date, d) == d

    # custom date
    class Date(date):
        pass

    dt = datetime.utcnow()
    with localcontext(lossy_conversion=True):
        assert typecast(Date, dt) == dt.date()

    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            typecast(Date, dt.replace(tzinfo=timezone.utc))

    class Date2(date):
        pass

    dt = Date2.today()
    assert typecast(Date, dt) == dt


def test_bool_from_date():
    d = date(1970, 1, 1)

    with pytest.raises(TypeError):
        typecast(bool, d)


def test_str_from_date():
    d = date(1970, 1, 1)

    # iso
    assert typecast(str, d) == "1970-01-01"

    # strftime
    with localcontext(date_format=r"=%Y-%m-%d="):
        assert typecast(str, d) == "=1970-01-01="


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
            typecast(time, t)

    # str - iso
    with pytest.raises(ValueError):
        typecast(time, "1970-01-01T00:00:00.000Z")
    with pytest.raises(ValueError):
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

    # str - stptime
    with localcontext(time_format=r"%H:%M:%S.%f"):
        assert typecast(time, "12:34:56.000789") == time(12, 34, 56, 789)

    # empty string
    with pytest.raises(ValueError):
        typecast(time, "")
    with pytest.raises(ValueError):
        typecast(time, " ")

    # None
    with pytest.raises(TypeError):
        typecast(time, None)

    # datetime
    dt = datetime.utcnow()  # naive
    with localcontext(lossy_conversion=True):
        assert typecast(time, dt) == dt.time()
    with localcontext(lossy_conversion=False):
        with pytest.raises(ValueError):
            typecast(time, dt)

    dt = datetime.now(timezone.utc)  # aware
    with localcontext(lossy_conversion=True):
        assert typecast(time, dt) == dt.timetz()

    # date
    with pytest.raises(TypeError):
        typecast(time, date(1970, 1, 1))

    # time
    t = time(12, 34, 56, 789)
    assert typecast(time, t) == t

    # custom time
    class Time(time):
        pass

    t = datetime.utcnow().time()
    assert typecast(Time, t) == t

    dt = datetime.utcnow()  # naive
    with localcontext(lossy_conversion=True):
        assert typecast(Time, dt) == dt.time()


def test_bool_from_time():
    t = time(12, 34, 56, 789)

    with pytest.raises(TypeError):
        typecast(bool, t)


def test_str_from_time():
    t = time(12, 34, 56, 789)

    # iso
    assert typecast(str, t) == "12:34:56.000789"

    # strftime
    with localcontext(time_format=r"=%H:%M:%S.%f%z="):
        assert typecast(str, t) == "=12:34:56.000789="


#
# timedelta
#


def test_timedelta():
    # int, float
    for T in (int, float):
        td = timedelta(days=12, hours=9, minutes=36, seconds=7)
        assert typecast(timedelta, T(td.total_seconds())) == td

    # str
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)
    assert typecast(timedelta, "P12DT9H36M7S") == td
    assert typecast(timedelta, "+P12DT9H36M7S") == td
    assert typecast(timedelta, "-P12DT9H36M7S") == -td
    assert typecast(timedelta, "P12DT34567S") == td
    assert typecast(timedelta, "PT1071367S") == td
    assert typecast(timedelta, "-PT1071367S") == -td

    assert typecast(timedelta, "12DT9H36M7S") == td
    assert typecast(timedelta, "+12DT9H36M7S") == td
    assert typecast(timedelta, "-12DT9H36M7S") == -td
    assert typecast(timedelta, "12DT34567S") == td
    assert typecast(timedelta, "T1071367S") == td
    assert typecast(timedelta, "-T1071367S") == -td

    assert typecast(timedelta, "12D9H36M7S") == td
    assert typecast(timedelta, "+12D9H36M7S") == td
    assert typecast(timedelta, "-12D9H36M7S") == -td
    assert typecast(timedelta, "12D34567S") == td
    assert typecast(timedelta, "1071367S") == td
    assert typecast(timedelta, "-1071367S") == -td

    assert typecast(timedelta, "12D9H36M7") == td
    assert typecast(timedelta, "+12D9H36M7") == td
    assert typecast(timedelta, "-12D9H36M7") == -td
    assert typecast(timedelta, "12D34567") == td
    assert typecast(timedelta, "1071367") == td
    assert typecast(timedelta, "-1071367") == -td

    assert typecast(timedelta, "12w") == timedelta(weeks=12)

    assert typecast(timedelta, "") == timedelta()

    with pytest.raises(ValueError):
        typecast(timedelta, "x")

    # None
    with pytest.raises(TypeError):
        typecast(timedelta, None)

    # timedelta
    td = timedelta()
    assert typecast(timedelta, td) == td

    # custom timedelta
    class TimeDelta(timedelta):
        pass

    td = timedelta()
    assert typecast(TimeDelta, td) == td


def test_float_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert typecast(float, td) == td.total_seconds()


def test_int_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert typecast(int, td) == int(td.total_seconds())

    with localcontext(lossy_conversion=False):
        assert typecast(int, td) == int(td.total_seconds())
        td = timedelta(days=12, hours=9, minutes=36, seconds=7, microseconds=1)
        with pytest.raises(ValueError):
            typecast(int, td)


def test_bool_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    with pytest.raises(TypeError):
        typecast(bool, td)


def test_str_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert typecast(str, td) == "P12DT9H36M7S"
    assert typecast(str, -td) == "-P12DT9H36M7S"

    td = timedelta(hours=9, seconds=7)
    assert typecast(str, td) == "PT9H7S"
    assert typecast(str, -td) == "-PT9H7S"

    td = timedelta(days=12)
    assert typecast(str, td) == "P12D"
    assert typecast(str, -td) == "-P12D"

    td = timedelta(days=12, seconds=7, microseconds=1)
    assert typecast(str, td) == "P12DT7.000001S"
    assert typecast(str, -td) == "-P12DT7.000001S"

    td = timedelta(days=12, seconds=60)
    assert typecast(str, td) == "P12DT1M"
    assert typecast(str, -td) == "-P12DT1M"
