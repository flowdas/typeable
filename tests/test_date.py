from datetime import date, datetime, time

import pytest

from typeable import typecast


def test_str():
    with pytest.raises(TypeError):
        typecast(date, "1970-01-01T00:00:00.000Z")
    with pytest.raises(TypeError):
        typecast(date, "1970-01-01T")

    assert typecast(date, "1970-01-01") == date(1970, 1, 1)
    assert typecast(date, "1969-12-31") == date(1969, 12, 31)
    assert typecast(date, "1970-1-01") == date(1970, 1, 1)
    assert typecast(date, "1970-01-1") == date(1970, 1, 1)
    assert typecast(date, "1970-1-1") == date(1970, 1, 1)
    assert typecast(date, " 1970-1-1 ") == date(1970, 1, 1)

    # empty string
    with pytest.raises(TypeError):
        typecast(date, "")
    with pytest.raises(TypeError):
        typecast(date, " ")


def test_datetime():
    dt = datetime.utcnow()  # naive
    with pytest.raises(TypeError):
        assert typecast(date, dt) is None


def test_time():
    with pytest.raises(TypeError):
        typecast(date, time())


def test_date():
    d = date(1970, 1, 1)
    assert typecast(date, d) == d


def test_custom():
    class Date(date):
        pass

    class Date2(date):
        pass

    dt = Date2.today()
    assert typecast(Date, dt) == dt
