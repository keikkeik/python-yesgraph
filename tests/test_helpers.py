from datetime import datetime

from yesgraph import format_date


def test_format_date():
    # leaves strings untouched (should be in ISO-8601)
    assert format_date('2015-03-19T13:37:00') == '2015-03-19T13:37:00'
    assert format_date('not a date') == 'not a date'  # ...but this isn't checked on the API client side (!)

    # leaves ints untouched (will be interpreted as a Unix timestamp)
    assert format_date(1426772220) == 1426772220

    # Python datetimes will be nicely formatted as an ISO-8601 date
    now = datetime(2015, 3, 19, 13, 37, 0)
    assert format_date(now) == '2015-03-19T13:37:00'
