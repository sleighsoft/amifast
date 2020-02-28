import pytest
import math
import statistics
import time

from dtypes import Stats, FunctionStats


def test_stats():
    t = Stats([0.0])
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

    t = Stats([0.1, 0.2, 0.3, 0.4, 0.5])
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

    with pytest.raises(AttributeError):
        t.times = [10]


def test_functionstats():
    pass
