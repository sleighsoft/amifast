import math
import os
import tempfile
import time

import pytest

from amifast import decorators
from amifast import dtypes
from amifast import format


def _function():
    time.sleep(0.0001)
    return -1


def _function_with_arg(a):
    time.sleep(a)


def _function_args_kwargs(a, b, c=0):
    time.sleep(a + b + c)


def test_benchit():
    result = decorators.benchit(repetitions=2)(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 2

    # With setup argument
    result = decorators.benchit(repetitions=2, setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 2

    # Function with argument
    result = decorators.benchit(repetitions=2)(_function_with_arg)(0.1)
    assert math.isclose(result.total, 0.2, abs_tol=0.01)

    # Function with argument
    result = decorators.benchit(repetitions=1)(_function_args_kwargs)(0.1, 0.2, c=0.3)
    assert math.isclose(result.total, 0.6, abs_tol=0.01)

    # Disabled by argument
    result = decorators.benchit(repetitions=2, enabled=False)(_function)()
    assert result == -1

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.benchit(repetitions=2)(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]

    # With @decorator
    @decorators.benchit(1)
    def _inner(a, b, c=0):
        time.sleep(a + b + c)

    result = _inner(0.1, 0.2, c=0.3)
    assert math.isclose(result.total, 0.6, abs_tol=0.01)


def test_single_shot():
    result = decorators.single_shot()(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    # With setup argument
    result = decorators.single_shot(setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions == 1

    # Function with argument
    result = decorators.single_shot()(_function_with_arg)(0.1)
    assert math.isclose(result.total, 0.1, abs_tol=0.01)

    # Function with argument
    result = decorators.single_shot()(_function_args_kwargs)(0.1, 0.2, c=0.3)
    assert math.isclose(result.total, 0.6, abs_tol=0.01)

    # Disabled by argument
    result = decorators.single_shot(enabled=False)(_function)()
    assert result == -1

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.single_shot()(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]

    # With @decorator
    @decorators.single_shot()
    def _inner(a, b, c=0):
        time.sleep(a + b + c)

    result = _inner(0.1, 0.2, c=0.3)
    assert math.isclose(result.total, 0.6, abs_tol=0.05)


def test_throughput():
    result = decorators.throughput()(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >= 1

    # With min_repetitions argument
    result = decorators.throughput(min_repetitions=5)(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >= 5

    # With setup argument
    result = decorators.throughput(min_repetitions=5, setup="gc.enable()")(_function)()
    assert isinstance(result, dtypes.Stats)
    assert result.repetitions >= 5

    # Function with argument
    result = decorators.throughput(min_repetitions=1)(_function_with_arg)(0.1)
    assert math.isclose(result.total, 0.1 * result.repetitions, abs_tol=0.01)

    # Function with argument
    result = decorators.throughput(min_repetitions=1)(_function_args_kwargs)(
        0.1, 0.2, c=0.3
    )
    assert math.isclose(result.total, 0.6 * result.repetitions, abs_tol=0.01)

    # Disabled by argument
    result = decorators.throughput(min_repetitions=5, enabled=False)(_function)()
    assert result == -1

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.throughput(min_repetitions=5)(_function)()
    assert result == -1
    del os.environ["ENABLE_BENCHMARKING"]

    # With @decorator
    @decorators.throughput(min_repetitions=1)
    def _inner(a, b, c=0):
        time.sleep(a + b + c)

    result = _inner(0.1, 0.2, c=0.3)
    assert math.isclose(result.total, 0.6 * result.repetitions, abs_tol=0.01)


def test_stats_as():
    stats = dtypes.Stats([i for i in range(20)], lambda x: x, 0)

    def _inner():
        return stats

    # CSV
    formatted = decorators.stats_as("csv")(_inner)()
    assert isinstance(formatted, format.CSV)

    formatted = decorators.stats_as(format.Format.CSV)(_inner)()
    assert isinstance(formatted, format.CSV)

    # Markdown
    formatted = decorators.stats_as("markdown")(_inner)()
    assert isinstance(formatted, format.Markdown)

    formatted = decorators.stats_as(format.Format.MARKDOWN)(_inner)()
    assert isinstance(formatted, format.Markdown)

    # JSON
    formatted = decorators.stats_as("json")(_inner)()
    assert isinstance(formatted, format.JSON)

    formatted = decorators.stats_as(format.Format.JSON)(_inner)()
    assert isinstance(formatted, format.JSON)

    # PLot
    try:
        import matplotlib

        formatted = decorators.stats_as("plot")(_inner)()
        assert isinstance(formatted, format.Plot)

        formatted = decorators.stats_as(format.Format.PLOT)(_inner)()
        assert isinstance(formatted, format.Plot)
    except ImportError:
        with pytest.raises(ImportError) as exc:
            decorators.stats_as("plot")(_inner)()
        assert "pip install matplotlib" in str(exc)

    with pytest.raises(TypeError) as exc:
        decorators.stats_as("csv")(lambda: 10)()
    assert "can only be used on" in str(exc)

    # Disabled by argument
    result = decorators.stats_as("csv", enabled=False)(_inner)()
    assert result == _inner()

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.stats_as("csv")(_inner)()
    assert result == _inner()
    del os.environ["ENABLE_BENCHMARKING"]

    # With @decorator
    @decorators.stats_as("csv")
    def _inner():
        return stats

    assert isinstance(_inner(), format.CSV)


def test_save():
    stats = dtypes.Stats([i for i in range(20)], lambda x: x, 0)

    with tempfile.TemporaryDirectory() as dir:
        available_formats = [f for f in format.Format][
            :-1
        ]  # TODO remove [:-1] when Plot is implemented
        for f in available_formats:
            formatted_stats = format.stats_as(stats, f)

            def _inner():
                return formatted_stats

            file = os.path.join(dir, f.value)
            result = decorators.save(file)(_inner)()
            assert result == formatted_stats
            assert os.path.exists(file)

    _inner = lambda: 10
    # Disabled by argument
    result = decorators.save("csv", enabled=False)(_inner)()
    assert result == _inner()

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"
    result = decorators.save("csv")(_inner)()
    assert result == _inner()
    del os.environ["ENABLE_BENCHMARKING"]

    # With @decorator
    with tempfile.TemporaryDirectory() as dir:
        file = os.path.join(dir, "decorator")

        formatted_stats = format.stats_as(stats, "csv")

        @decorators.save(file)
        def _inner():
            return formatted_stats

        assert _inner() == formatted_stats
        assert os.path.exists(file)


def test_validate():
    # TODO
    assert False


# TODO Add tests for nesting @stats_as -> @amifast
def test_decorator_chaining():
    def _inner():
        time.sleep(0.01)
        return -1

    # benchmarking
    benchit = decorators.benchit(1)(_inner)
    single_shot = decorators.single_shot()(_inner)
    throughput = decorators.throughput()(_inner)

    assert isinstance(benchit(), dtypes.Stats)
    assert isinstance(single_shot(), dtypes.Stats)
    assert isinstance(throughput(), dtypes.Stats)

    # stats_as + benchmarking
    benchit_as = decorators.stats_as("csv")(benchit)
    single_shot_as = decorators.stats_as("csv")(single_shot)
    throughput_as = decorators.stats_as("csv")(throughput)

    assert isinstance(benchit_as(), format.CSV)
    assert isinstance(single_shot_as(), format.CSV)
    assert isinstance(throughput_as(), format.CSV)

    # stats_as + benchmarking + save
    with tempfile.TemporaryDirectory() as dir:
        f1 = os.path.join(dir, "benchit")
        f2 = os.path.join(dir, "singleshot")
        f3 = os.path.join(dir, "throughput")

        benchit_as_save = decorators.save(f1)(benchit_as)
        single_shot_as_save = decorators.save(f2)(single_shot_as)
        throughput_as_save = decorators.save(f3)(throughput_as)

        benchit_as_save()
        single_shot_as_save()
        throughput_as_save()

        assert os.path.exists(f1)
        assert os.path.exists(f2)
        assert os.path.exists(f3)

    # @stats_as before benchmarking
    with pytest.raises(TypeError) as exc:
        decorators.stats_as("csv")(_inner)()
    assert "@stats_as can only be used" in str(exc)

    with pytest.raises(TypeError) as exc:
        decorators.stats_as("csv")(_inner)()
    assert "@stats_as can only be used" in str(exc)

    with pytest.raises(TypeError) as exc:
        decorators.stats_as("csv")(_inner)()
    assert "@stats_as can only be used" in str(exc)

    # @save before @stats_as
    with pytest.raises(TypeError) as exc:
        decorators.save("none")(benchit)()
    assert "@save can only be used" in str(exc)

    with pytest.raises(TypeError) as exc:
        decorators.save("none")(single_shot)()
    assert "@save can only be used" in str(exc)

    with pytest.raises(TypeError) as exc:
        decorators.save("none")(throughput)()
    assert "@save can only be used" in str(exc)

    # Disabled by environment
    os.environ["ENABLE_BENCHMARKING"] = "0"

    benchit = decorators.benchit(1)(_inner)
    single_shot = decorators.single_shot()(_inner)
    throughput = decorators.throughput()(_inner)
    assert benchit() == -1
    assert single_shot() == -1
    assert throughput() == -1

    benchit_as = decorators.stats_as("csv")(benchit)
    single_shot_as = decorators.stats_as("csv")(single_shot)
    throughput_as = decorators.stats_as("csv")(throughput)
    assert benchit() == -1
    assert single_shot() == -1
    assert throughput() == -1

    assert decorators.save("none")(benchit_as)() == -1
    assert decorators.save("none")(single_shot_as)() == -1
    assert decorators.save("none")(throughput_as)() == -1

    del os.environ["ENABLE_BENCHMARKING"]
