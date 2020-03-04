import pytest
import math
import statistics
import time
import inspect

import dtypes


def test_stats():
    t = dtypes.Stats([0.0])
    assert t.minimum == 0.0
    assert t.minimum == 0.0
    assert t.maximum == 0.0
    assert t.mean == 0.0
    assert t.median == 0.0
    assert t.repetitions == 1
    assert t.total == 0.0
    assert t.std == 0.0
    assert t.std_outliers == 0
    assert math.isnan(t.throughput)
    assert math.isnan(t.throughput_min)
    assert t.percentile_0th == 0.0
    assert t.percentile_0th == t.minimum
    assert t.percentile_5th == 0.0
    assert t.percentile_25th == 0.0
    assert t.percentile_50th == 0.0
    assert t.percentile_50th == t.median
    assert t.percentile_75th == 0.0
    assert t.percentile_95th == 0.0
    assert t.percentile_100th == 0.0
    assert t.percentile_100th == t.maximum

    t = dtypes.Stats([0.1, 0.2, 0.3, 0.4, 0.5])
    assert t.minimum == 0.1
    assert t.maximum == 0.5
    assert t.mean == 0.3
    assert t.std == 0.15811388300841897
    assert t.median == 0.3
    assert t.std_outliers == 2
    assert isinstance(t.std_outliers, int)
    assert t.repetitions == 5
    assert t.total == 1.5
    assert t.throughput == 3 + 1 / 3
    assert t.throughput_min == 10.0
    assert t.percentile_0th == 0.1
    assert t.percentile_0th == t.minimum
    assert math.isclose(t.percentile_5th, 0.12)
    assert t.percentile_25th == 0.2
    assert t.percentile_50th == 0.3
    assert t.percentile_50th == t.median
    assert t.percentile_75th == 0.4
    assert t.percentile_95th == 0.48
    assert t.percentile_100th == 0.5
    assert t.percentile_100th == t.maximum

    with pytest.raises(AttributeError):
        t.times = [10]
    with pytest.raises(ValueError):
        t._percentile(2)
    with pytest.raises(ValueError):
        t._percentile(1.2)


def test_stats_time_conversion():
    """Note: This checkf for general sanity and does not run all combinations
    of time conversions right now."""
    times = [60, 120]
    t = dtypes.Stats(times)
    # nanoseconds
    t.to_nanoseconds()
    assert times[0] * 1e9 == t.times[0]
    assert times[1] * 1e9 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # microseconds
    t.to_microseconds()
    assert times[0] * 1e6 == t.times[0]
    assert times[1] * 1e6 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # milliseconds
    t.to_milliseconds()
    assert times[0] * 1e3 == t.times[0]
    assert times[1] * 1e3 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # seconds
    t.to_seconds()
    assert t.times == times
    # minutes
    t.to_minutes()
    assert times[0] / 60 == t.times[0]
    assert times[1] / 60 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # hours
    t.to_hours()
    assert times[0] / (60 * 60) == t.times[0]
    assert times[1] / (60 * 60) == t.times[1]
    t.to_seconds()
    assert t.times == times
    # days
    t.to_days()
    assert times[0] / (24 * 60 * 60) == t.times[0]
    assert times[1] / (24 * 60 * 60) == t.times[1]
    t.to_seconds()
    assert t.times == times

    # nanoseconds to hours
    t.to_nanoseconds()
    t.to_hours()
    assert t.times[0] == times[0] * 1e9 / (60 * 60 * 1e9)
    assert t.times[1] == times[1] * 1e9 / (60 * 60 * 1e9)


def test_stats_cache():
    t = dtypes.Stats([1.0])
    t.minimum
    t.minimum
    t.maximum
    t.mean
    t.median
    t.repetitions
    t.total
    t.std
    t.std_outliers
    t.throughput
    t.throughput_min
    t.percentile_0th
    t.percentile_0th
    t.percentile_5th
    t.percentile_25th
    t.percentile_50th
    t.percentile_50th
    t.percentile_75th
    t.percentile_95th
    t.percentile_100th
    t.percentile_100th

    properties = [
        "mean",
        "std",
        "std_outliers",
        "repetitions",
        "total",
        "throughput",
        "throughput_min",
        "minimum",
        "percentile_5th",
        "percentile_25th",
        "median",
        "percentile_75th",
        "percentile_95th",
        "maximum",
    ]
    for p in properties:
        assert p in t.__dict__
    t.to_nanoseconds()
    for p in properties:
        assert p not in t.__dict__


def test_functionstats():
    def _inner():
        pass

    start = time.time()
    t = dtypes.FunctionStats([10, 20], _inner)
    assert t.name == _inner.__name__
    assert start <= t.timestamp <= time.time()
    assert t.file == inspect.getsourcefile(_inner)
    assert isinstance(t.line, int)

    # inbuilt
    t = dtypes.FunctionStats([10, 20], max)
    assert t.name == max.__name__
    assert t.file == None
    assert t.line == None
