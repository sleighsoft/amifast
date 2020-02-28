import stats


def test_to_nanoseconds():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_nanoseconds(times)
    assert all([n == t * 1000000000 for t, n in zip(times, nano)])


def test_to_microseconds():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_microseconds(times)
    assert all([n == t * 1000000 for t, n in zip(times, nano)])


def test_to_milliseconds():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_milliseconds(times)
    assert all([n == t * 1000 for t, n in zip(times, nano)])


def test_to_minutes():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_minutes(times)
    assert all([n == t / 60 for t, n in zip(times, nano)])


def test_to_hours():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_hours(times)
    assert all([n == t / 3600 for t, n in zip(times, nano)])


def test_to_days():
    times = [10, 20, 30, 40, 50, 55.5, 60.1]
    nano = stats.to_days(times)
    assert all([n == t / 86400 for t, n in zip(times, nano)])
