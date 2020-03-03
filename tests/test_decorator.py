import os
import time

from benchit import decorators
from benchit import dtypes


def _function():
    time.sleep(0.0001)
    return -1


def test_benchit():
    result = decorators.benchit(repetitions=2)(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 2

    result = decorators.benchit(repetitions=2, setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 2

    result = decorators.benchit(repetitions=2, setup="gc.enable()", enabled=False)(
        _function
    )()
    assert result == -1

    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.benchit(repetitions=2, setup="gc.enable()")(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]


def test_single_shot():
    result = decorators.single_shot()(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    result = decorators.single_shot(setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    result = decorators.single_shot(setup="gc.enable()", enabled=False)(_function)()
    assert result == -1

    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.single_shot(setup="gc.enable()")(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]


def test_throughput():
    result = decorators.throughput()(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >=1

    result = decorators.throughput(min_repetitions=5)(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >= 5

    result = decorators.throughput(min_repetitions=5, setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >= 5

    result = decorators.throughput(
        min_repetitions=5, setup="gc.enable()", enabled=False
    )(_function)()
    assert result == -1

    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.throughput(min_repetitions=5, setup="gc.enable()")(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]


def test_stats_as():
    # TODO Test
    pass
