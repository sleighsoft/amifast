import time
import math
import random

from benchit import bench
from benchit import dtypes


TOLERANCE = 1e-1


def time_fn(n=0.0001):
    def inner():
        time.sleep(n)

    return inner


def test_benchit():
    result = bench.benchit(fn=time_fn(), repetitions=10)
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 10

    bench.benchit(fn=time_fn(), repetitions=1, setup="gc.enable()")


def test_single_shot():
    result = bench.single_shot(fn=time_fn())
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    bench.single_shot(fn=time_fn(), setup="gc.enable()")


def test_throughput():
    sleep = 0.1

    result = bench.throughput(fn=time_fn(sleep))
    assert isinstance(result, dtypes.Stats)
    assert result.total >= 1.0
    assert math.isclose(result.throughput, 1.0 / sleep, rel_tol=TOLERANCE)

    min_repetitions = 20
    result = bench.throughput(fn=time_fn(sleep), min_repetitions=min_repetitions)
    assert isinstance(result, dtypes.Stats)
    assert result.total >= 1.0
    assert result.repetitions >= min_repetitions
    assert math.isclose(result.throughput, 1.0 / sleep, rel_tol=TOLERANCE)

    bench.throughput(fn=time_fn(), setup="gc.enable()")
