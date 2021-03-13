# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from datetime import datetime, date, time, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    skip_zoneinfo = False
except ImportError:
    skip_zoneinfo = True

import pytest

from typeable import *

#
# datetime
#


def test_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # int, float
    for T in (int, float):
        t = T(0)
        assert cast(datetime, t) == aware_epoch
        assert cast(datetime, t, ctx=Context(
            naive_timestamp=True)) == naive_epoch

    # str - iso
    with pytest.raises(ValueError):
        cast(datetime, '1970-01-01T00:00:00.000Z #')
    assert cast(datetime, '1970-01-01T00:00:00.000Z') == aware_epoch
    assert cast(datetime, '1970-01-01T00:00:00.000+00:00') == aware_epoch
    assert cast(datetime, '1970-01-01T00:00:00.000-00:00') == aware_epoch
    assert cast(datetime, '1970-01-01T09:00:00.000+09:00') == aware_epoch
    assert cast(datetime, '1969-12-31T15:00:00.000-09:00') == aware_epoch
    assert cast(datetime, '1970-01-01T00:00:00.000') == naive_epoch
    assert cast(datetime, '1970-1-01T00:00:00.000') == naive_epoch
    assert cast(datetime, '1970-01-1T00:00:00.000') == naive_epoch
    assert cast(datetime, '1970-01-01T0:00:00.000') == naive_epoch
    assert cast(datetime, '1970-01-01T00:0:00.000') == naive_epoch
    assert cast(datetime, '1970-01-01T00:00:0.000') == naive_epoch
    assert cast(datetime, '1970-01-01T00:00:0.') == naive_epoch
    assert cast(datetime, '1970-01-01T00:00:0') == naive_epoch
    assert cast(datetime, '1970-1-1T0:0') == naive_epoch
    assert cast(datetime, '1970-1-1 0:0') == naive_epoch
    assert cast(datetime, '1970-1-1T') == naive_epoch
    assert cast(datetime, '1970-1-1') == naive_epoch
    assert cast(datetime, ' 1970-1-1 ') == naive_epoch

    # str - timestamp
    assert cast(datetime, '0', ctx=Context(
        datetime_format='timestamp')) == aware_epoch
    assert cast(datetime, '0', ctx=Context(
        datetime_format='timestamp', naive_timestamp=True)) == naive_epoch

    # str - http & email
    for format in ('http', 'email'):
        ctx = Context(datetime_format=format)
        expected = datetime(2016, 3, 7, 0, 4, 24,
                            tzinfo=timezone(timedelta(hours=9)))
        assert cast(datetime, 'Mon, 07 Mar 2016 00:04:24 +0900',
                    ctx=ctx) == expected

    # str - stptime
    ctx = Context(datetime_format=r'%Y-%m-%dT%H:%M:%S.%f%z')
    assert cast(datetime, '1970-01-01T00:00:00.000000+0000',
                ctx=ctx) == aware_epoch

    # empty string
    with pytest.raises(ValueError):
        cast(datetime, '')
    with pytest.raises(ValueError):
        cast(datetime, ' ')

    # None
    with pytest.raises(TypeError):
        cast(datetime, None)

    # date
    d = date(1970, 1, 1)
    assert cast(datetime, d) == naive_epoch

    # time
    with pytest.raises(TypeError):
        cast(datetime, time())

    # datetime
    dt = datetime.utcnow()  # naive
    assert cast(datetime, dt) == dt

    dt = datetime.now(timezone.utc)  # aware
    assert cast(datetime, dt) == dt


def test_float_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert cast(float, naive_epoch) == naive_epoch.timestamp()
    assert cast(float, aware_epoch) == 0


def test_int_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    assert cast(int, naive_epoch) == naive_epoch.timestamp()
    assert cast(int, aware_epoch) == 0


def test_bool_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)

    with pytest.raises(TypeError):
        cast(bool, naive_epoch)


def test_str_from_datetime():
    naive_epoch = datetime(1970, 1, 1, 0, 0)
    aware_epoch = naive_epoch.replace(tzinfo=timezone.utc)

    # iso
    assert cast(str, naive_epoch) == naive_epoch.isoformat()
    assert cast(str, aware_epoch) == '1970-01-01T00:00:00Z'

    # http
    dt = datetime(2016, 3, 7, 0, 4, 24, tzinfo=timezone(timedelta(hours=9)))
    ctx = Context(datetime_format='http')
    assert cast(str, dt, ctx=ctx) == 'Sun, 06 Mar 2016 15:04:24 GMT'

    # email
    ctx = Context(datetime_format='email')
    assert cast(str, dt, ctx=ctx) == 'Mon, 07 Mar 2016 00:04:24 +0900'

    # timestamp
    ctx = Context(datetime_format='timestamp')
    assert cast(str, naive_epoch, ctx=ctx) == str(int(naive_epoch.timestamp()))
    assert cast(str, aware_epoch, ctx=ctx) == '0'

    # strftime
    ctx = Context(datetime_format=r'=%Y-%m-%dT%H:%M:%S.%f%z=')
    assert cast(str, aware_epoch,
                ctx=ctx) == '=1970-01-01T00:00:00.000000+0000='

#
# date
#


def test_date():
    # int, float
    for T in (int, float):
        t = T(0)
        with pytest.raises(TypeError):
            cast(date, t)

    # str - iso
    with pytest.raises(ValueError):
        cast(date, '1970-01-01T00:00:00.000Z')
    with pytest.raises(ValueError):
        cast(date, '1970-01-01T')

    assert cast(date, '1970-01-01') == date(1970, 1, 1)
    assert cast(date, '1969-12-31') == date(1969, 12, 31)
    assert cast(date, '1970-1-01') == date(1970, 1, 1)
    assert cast(date, '1970-01-1') == date(1970, 1, 1)
    assert cast(date, '1970-1-1') == date(1970, 1, 1)
    assert cast(date, ' 1970-1-1 ') == date(1970, 1, 1)

    # str - stptime
    ctx = Context(date_format=r'%Y-%m-%d')
    assert cast(date, '1970-01-01', ctx=ctx) == date(1970, 1, 1)

    # empty string
    with pytest.raises(ValueError):
        cast(date, '')
    with pytest.raises(ValueError):
        cast(date, ' ')

    # None
    with pytest.raises(TypeError):
        cast(date, None)

    # datetime
    ctx = Context(lossy_conversion=False)

    dt = datetime.utcnow()  # naive
    if dt.microsecond == 0:
        dt = dt.replace(microsecond=1)
    assert cast(date, dt) == dt.date()
    with pytest.raises(ValueError):
        cast(date, dt, ctx=ctx)
    assert cast(date, datetime(1970, 1, 1, 0, 0), ctx=ctx) == date(1970, 1, 1)

    dt = datetime.now(timezone.utc)  # aware
    assert cast(date, dt) == dt.date()
    with pytest.raises(ValueError):
        cast(date, dt, ctx=ctx)

    # time
    with pytest.raises(TypeError):
        cast(date, time())

    # date
    d = date(1970, 1, 1)
    assert cast(date, d) == d


def test_bool_from_date():
    d = date(1970, 1, 1)

    with pytest.raises(TypeError):
        cast(bool, d)


def test_str_from_date():
    d = date(1970, 1, 1)

    # iso
    assert cast(str, d) == '1970-01-01'

    # strftime
    ctx = Context(date_format=r'=%Y-%m-%d=')
    assert cast(str, d, ctx=ctx) == '=1970-01-01='

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
            cast(time, t)

    # str - iso
    with pytest.raises(ValueError):
        cast(time, '1970-01-01T00:00:00.000Z')
    with pytest.raises(ValueError):
        cast(time, '1970-01-01T')

    assert cast(time, '00:00:00.000Z') == aware_epoch.timetz()
    assert cast(time, '00:00:00.000+00:00') == aware_epoch.timetz()
    assert cast(time, '00:00:00.000-00:00') == aware_epoch.timetz()
    assert cast(time, '09:00:00.000+09:00') == aware_epoch.timetz()
    assert cast(time, '00:00:00.000') == naive_epoch.time()
    assert cast(time, '0:00:00.000') == naive_epoch.time()
    assert cast(time, '00:0:00.000') == naive_epoch.time()
    assert cast(time, '00:00:0.000') == naive_epoch.time()
    assert cast(time, '00:00:0.') == naive_epoch.time()
    assert cast(time, '00:00:0') == naive_epoch.time()
    assert cast(time, '0:0') == naive_epoch.time()

    # str - stptime
    ctx = Context(time_format=r'%H:%M:%S.%f')
    assert cast(time, '12:34:56.000789', ctx=ctx) == time(12, 34, 56, 789)

    # empty string
    with pytest.raises(ValueError):
        cast(time, '')
    with pytest.raises(ValueError):
        cast(time, ' ')

    # None
    with pytest.raises(TypeError):
        cast(time, None)

    # datetime
    ctx = Context(lossy_conversion=False)

    dt = datetime.utcnow()  # naive
    assert cast(time, dt) == dt.time()
    with pytest.raises(ValueError):
        cast(time, dt, ctx=ctx)

    dt = datetime.now(timezone.utc)  # aware
    assert cast(time, dt) == dt.timetz()

    # date
    with pytest.raises(TypeError):
        cast(time, date(1970, 1, 1))

    # time
    t = time(12, 34, 56, 789)
    assert cast(time, t) == t


def test_bool_from_time():
    t = time(12, 34, 56, 789)

    with pytest.raises(TypeError):
        cast(bool, t)


def test_str_from_time():
    t = time(12, 34, 56, 789)

    # iso
    assert cast(str, t) == '12:34:56.000789'

    # strftime
    ctx = Context(time_format=r'=%H:%M:%S.%f%z=')
    assert cast(str, t, ctx=ctx) == '=12:34:56.000789='

#
# timedelta
#


def test_timedelta():
    # int, float
    for T in (int, float):
        td = timedelta(days=12, hours=9, minutes=36, seconds=7)
        assert cast(timedelta, T(td.total_seconds())) == td

    # str
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)
    assert cast(timedelta, 'P12DT9H36M7S') == td
    assert cast(timedelta, '+P12DT9H36M7S') == td
    assert cast(timedelta, '-P12DT9H36M7S') == -td
    assert cast(timedelta, 'P12DT34567S') == td
    assert cast(timedelta, 'PT1071367S') == td
    assert cast(timedelta, '-PT1071367S') == -td

    assert cast(timedelta, '12DT9H36M7S') == td
    assert cast(timedelta, '+12DT9H36M7S') == td
    assert cast(timedelta, '-12DT9H36M7S') == -td
    assert cast(timedelta, '12DT34567S') == td
    assert cast(timedelta, 'T1071367S') == td
    assert cast(timedelta, '-T1071367S') == -td

    assert cast(timedelta, '12D9H36M7S') == td
    assert cast(timedelta, '+12D9H36M7S') == td
    assert cast(timedelta, '-12D9H36M7S') == -td
    assert cast(timedelta, '12D34567S') == td
    assert cast(timedelta, '1071367S') == td
    assert cast(timedelta, '-1071367S') == -td

    assert cast(timedelta, '12D9H36M7') == td
    assert cast(timedelta, '+12D9H36M7') == td
    assert cast(timedelta, '-12D9H36M7') == -td
    assert cast(timedelta, '12D34567') == td
    assert cast(timedelta, '1071367') == td
    assert cast(timedelta, '-1071367') == -td

    assert cast(timedelta, '12w') == timedelta(weeks=12)

    assert cast(timedelta, '') == timedelta()

    # None
    with pytest.raises(TypeError):
        cast(timedelta, None)

    # timedelta
    td = timedelta()
    assert cast(timedelta, td) == td


def test_float_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert cast(float, td) == td.total_seconds()


def test_int_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert cast(int, td) == int(td.total_seconds())


def test_bool_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    with pytest.raises(TypeError):
        cast(bool, td)


def test_str_from_timedelta():
    td = timedelta(days=12, hours=9, minutes=36, seconds=7)

    assert cast(str, td) == 'P12DT9H36M7S'
    assert cast(str, -td) == '-P12DT9H36M7S'

    td = timedelta(hours=9, seconds=7)
    assert cast(str, td) == 'PT9H7S'
    assert cast(str, -td) == '-PT9H7S'

    td = timedelta(days=12)
    assert cast(str, td) == 'P12D'
    assert cast(str, -td) == '-P12D'
