from datetime import timedelta

import pytest

from typeable import typecast


def test_timedelta():
    td = timedelta()
    assert typecast(timedelta, td) == td


def test_str():
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

    with pytest.raises(TypeError):
        typecast(timedelta, "x")


def test_custom():
    # custom timedelta
    class TimeDelta(timedelta):
        pass

    td = timedelta()
    assert typecast(TimeDelta, td) == td
