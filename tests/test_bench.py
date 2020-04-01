import math
import random
import time

from benchit import bench
from benchit import dtypes


TOLERANCE = 1e-1


def _fn():
    time.sleep(0.0001)


def _fn_args(a, b, *, c=0):
    time.sleep(a)
    time.sleep(b)
    time.sleep(c)


def test_benchit():
    result = bench.benchit(fn=_fn, repetitions=10)
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 10

    bench.benchit(fn=_fn, repetitions=1, setup="gc.enable()")

    # fmt: off
    assert bench.benchit(_fn_args, 1, fn_args=(0.1, 0.2)).total >= 0.25
    assert bench.benchit(_fn_args, 1, fn_args=(0.1,), fn_kwargs={"b": 0.2}).total >= 0.25
    assert bench.benchit(_fn_args, 1, fn_kwargs={"a": 0.1, "b": 0.2}).total >= 0.25
    assert bench.benchit(_fn_args, 1, fn_kwargs={"a": 0.1, "b": 0.2, "c": 0.1}).total >= 0.35
    # fmt: on


def test_single_shot():
    result = bench.single_shot(fn=_fn)
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    bench.single_shot(fn=_fn, setup="gc.enable()")

    # fmt: off
    assert bench.single_shot(_fn_args, fn_args=(0.1, 0.2)).total >= 0.25
    assert bench.single_shot(_fn_args, fn_args=(0.1,), fn_kwargs={"b": 0.2}).total >= 0.25
    assert bench.single_shot(_fn_args, fn_kwargs={"a": 0.1, "b": 0.2}).total >= 0.25
    assert bench.single_shot(_fn_args, fn_kwargs={"a": 0.1, "b": 0.2, "c": 0.1}).total >= 0.35
    # fmt: on


def test_throughput():
    sleep_time = 0.1

    def sleep():
        time.sleep(sleep_time)

    result = bench.throughput(fn=sleep)
    assert isinstance(result, dtypes.Stats)
    assert result.total >= 1.0
    assert math.isclose(result.throughput, 1.0 / sleep_time, rel_tol=TOLERANCE)
    assert len(result.raw_times) == len(result.times) + 1

    min_repetitions = 20
    result = bench.throughput(fn=sleep, min_repetitions=min_repetitions)
    assert isinstance(result, dtypes.Stats)
    assert result.total >= 1.0
    assert result.repetitions >= min_repetitions
    assert math.isclose(result.throughput, 1.0 / sleep_time, rel_tol=TOLERANCE)

    bench.throughput(fn=_fn, setup="gc.enable()")

    # fmt: off
    assert bench.throughput(_fn_args, 1, fn_args=(0.1, 0.2)).throughput > 3.3
    assert bench.throughput(_fn_args, 1, fn_args=(0.1,), fn_kwargs={"b": 0.2}).throughput > 3.3
    assert bench.throughput(_fn_args, 1, fn_kwargs={"a": 0.1, "b": 0.2}).throughput > 3.3
    assert bench.throughput(_fn_args, 1, fn_kwargs={"a": 0.1, "b": 0.2, "c": 0.1}).throughput > 2.0
    # fmt: on
