import inspect
import math
import statistics
import time

import pytest

from amifast import dtypes


def _make_runtime_function():
    exec("def f_runtime_function(a): pass")
    return locals()["f_runtime_function"]


def _inner():
    pass


def test_stats_statistics():
    times = [0.0]
    t = dtypes.Stats(times, _inner, 0)
    assert t.raw_times == times
    assert t.times == times
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

    times = [0.1, 0.2, 0.3, 0.4, 0.5]
    t = dtypes.Stats(times, _inner, 0)
    assert t.raw_times == times
    assert t.times == times
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
    with pytest.raises(ValueError) as exc:
        t._percentile(2)
    assert "must be a float" in str(exc)
    with pytest.raises(ValueError):
        t._percentile(1.2)
    assert "must be a float" in str(exc)

    # With warmups
    times = [0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    warmups = 2
    t = dtypes.Stats(times, _inner, warmups)
    assert t.raw_times == times
    assert t.times == times[warmups:]
    assert t.minimum == 0.1
    assert t.maximum == 0.5
    assert t.mean == 0.3
    assert t.std == 0.15811388300841897
    assert t.median == 0.3
    assert t.std_outliers == 2
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


def test_stats_metadata():
    # defaults
    start = time.time()
    t = dtypes.Stats([10, 20], None, 0)
    assert t.setup == "pass"
    assert start <= t.timestamp <= time.time()
    assert t.function_args == None
    assert t.function_kwargs == None
    assert t.file == None
    assert t.line == None
    assert t.warmups == 0
    assert t.unit == dtypes.TimeUnit.S

    # function
    t = dtypes.Stats([10, 20], _inner, 1)
    assert t.function_name == _inner.__name__
    assert t.file == inspect.getsourcefile(_inner)
    assert isinstance(t.line, int)
    assert t.warmups == 1

    t = dtypes.Stats([10, 20], _inner, 0, timestamp=start)
    assert t.timestamp == start

    # inbuilt function
    t = dtypes.Stats([10, 20], max, 0)
    assert t.function_name == max.__name__
    assert t.file == None
    assert t.line == None
    assert t.function == max

    # function string
    fn = "lambda: 10"
    t = dtypes.Stats([10], fn, 0)
    assert t.file == None
    assert t.function_name == None
    assert t.line == None
    assert t.function == fn

    # runtime function
    fn = _make_runtime_function()
    t = dtypes.Stats([10], fn, 0)
    assert t.file == "<string>"
    assert t.function_name == fn.__name__
    assert t.line == None
    assert t.function == fn

    # args and kwargs
    args = (1, 2)
    kwargs = {1: 2, 3: 4}
    t = dtypes.Stats([10], _inner, 0, fn_args=args, fn_kwargs=kwargs)
    assert t.function_args == args
    assert t.function_kwargs == kwargs

    with pytest.raises(ValueError) as exc:
        dtypes.Stats([1, 2, 3], None, 3)
    assert "No timing data" in str(exc)


def test_stats_time_conversion():
    """Note: This checks for general sanity and does not run all combinations
    of time conversions right now."""
    times = [60, 120]
    t = dtypes.Stats(times, lambda x: x, 0)
    # nanoseconds
    t.to_nanoseconds()
    assert t.unit == dtypes.TimeUnit.NS
    assert times[0] * 1e9 == t.times[0]
    assert times[1] * 1e9 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # microseconds
    t.to_microseconds()
    assert t.unit == dtypes.TimeUnit.US
    assert times[0] * 1e6 == t.times[0]
    assert times[1] * 1e6 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # milliseconds
    t.to_milliseconds()
    assert t.unit == dtypes.TimeUnit.MS
    assert times[0] * 1e3 == t.times[0]
    assert times[1] * 1e3 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # seconds
    t.to_seconds()
    assert t.times == times
    # minutes
    t.to_minutes()
    assert t.unit == dtypes.TimeUnit.M
    assert times[0] / 60 == t.times[0]
    assert times[1] / 60 == t.times[1]
    t.to_seconds()
    assert t.times == times
    # hours
    t.to_hours()
    assert t.unit == dtypes.TimeUnit.H
    assert times[0] / (60 * 60) == t.times[0]
    assert times[1] / (60 * 60) == t.times[1]
    t.to_seconds()
    assert t.times == times
    # days
    t.to_days()
    assert t.unit == dtypes.TimeUnit.D
    assert times[0] / (24 * 60 * 60) == t.times[0]
    assert times[1] / (24 * 60 * 60) == t.times[1]
    t.to_seconds()
    assert t.times == times

    # nanoseconds to hours
    t.to_nanoseconds()
    t.to_hours()
    assert t.times[0] == times[0] * 1e9 / (60 * 60 * 1e9)
    assert t.times[1] == times[1] * 1e9 / (60 * 60 * 1e9)

    # With warmup
    t = dtypes.Stats(times, lambda x: x, 1)
    # nanoseconds
    t.to_nanoseconds()
    assert t.unit == dtypes.TimeUnit.NS
    assert times[0] * 1e9 == t.raw_times[0]
    assert times[1] * 1e9 == t.times[0]


def test_stats_cache():
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

    t = dtypes.Stats([1.0], lambda x: x, 0)
    # Nothing cached yet
    for p in properties:
        assert p not in t.__dict__

    # Access all cached_properties to cache them
    for p in properties:
        getattr(t, p)

    # Cached
    for p in properties:
        assert p in t.__dict__

    # This should invalidate cache
    t.to_nanoseconds()

    # Nothing cached again
    for p in properties:
        assert p not in t.__dict__


def test_benchmark():
    # TODO
    assert False
