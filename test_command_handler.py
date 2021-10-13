import datetime
import numpy as np
from command_handler import pretty_delta, shorten_name


def generate_range(start, max):
    # precision is down to 10e-6 of second
    return np.linspace(start, max-10e-6, 100)


def test_pretty_delta():
    # january 1 2021 at midnight
    now = datetime.datetime(2021, 1, 1)

    one_sec = 1
    one_min = 60
    one_hour = 60*60
    one_day = 24*60*60

    for seconds in generate_range(0, 2*one_sec):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == "just now"

    for seconds in generate_range(2*one_sec, one_min):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == f"{int(seconds)} seconds ago"

    for seconds in generate_range(one_min, 2*one_min):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == "1 minute ago"

    for seconds in generate_range(2*one_min, one_hour):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == f"{int(seconds)//60} minutes ago"

    for seconds in generate_range(one_hour, 2*one_hour):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == "1 hour ago"

    for seconds in generate_range(2*one_hour, one_day):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == f"{int(seconds)//(60*60)} hours ago"

    for seconds in generate_range(one_day, 2*one_day):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == f"1 day ago"

    for seconds in generate_range(2*one_day, 14*one_day):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now) == f"{int(seconds)//(24*60*60)} days ago"

    for seconds in generate_range(14*one_day, 60*one_day):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now).startswith("on ")
        assert len(pretty_delta(date, now).split(" ")) == 3

    for seconds in generate_range(60*one_day, 1000*one_day):
        date = now - datetime.timedelta(seconds=seconds)
        assert pretty_delta(date, now).startswith("on ")
        assert len(pretty_delta(date, now).split(" ")) == 4

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 1, 3)
    print(now - date)
    assert pretty_delta(date, now) == f"2 days ago"

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 10, 1)
    assert pretty_delta(date, now) == f"on January 01, 2021"

    date = datetime.datetime(2021, 1, 1)
    now = datetime.datetime(2021, 2, 1)
    assert pretty_delta(date, now) == f"on January 01"
    assert pretty_delta(now, date) == "in the future?"

def test_shorten_name():
    assert shorten_name("abc") == "abc"
    test_str = "0123456789"
    assert shorten_name(test_str, 6) == "012..."
    assert shorten_name(test_str, 9) == "012345..."
    assert shorten_name(test_str, 10) == "0123456789"