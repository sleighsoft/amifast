import sys
import timeit

from dtypes import Stats


def benchit(fn, repetitions, setup="pass") -> Stats:
    """Bechmarks a function a number of times and returns a time series in seconds.

    **Note**: By default, `benchit()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    **Note**: It’s tempting to calculate mean and standard deviation from
    the result vector and report these. However, this is not very useful.
    In a typical case, the lowest value gives a lower bound for how fast
    the machine can run the given code snippet; higher values in the
    result vector are typically not caused by variability in Python’s
    speed, but by other processes interfering with the timing accuracy.
    So the min() of the result is probably the only number you should be
    interested in. After that, you should look at the entire vector and
    apply common sense rather than statistics.

    Args:
        fn (function): Function to benchmark.
        repetitions (int): Number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".

    Returns:
        dtypes.Stats(
            times: A list of length `repetitions` containing benchmark times in seconds.
        )
    """
    timer = timeit.Timer(stmt=fn, setup=setup)
    times = timer.repeat(repetitions, 1)
    return Stats(times)


def single_shot(fn, setup="pass") -> Stats:
    """Measures how long a single method execution takes to
    run. This is good to test how it performs under a cold start.

    **Note**: By default, `single_shot()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    Args:
        fn (function): Function to benchmark.
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".

    Returns:
        dtypes.Stats(
            times: Time in seconds to run `fn` (length=1).
        )
    """
    return benchit(fn, 1, setup=setup)


def throughput(fn, min_repetitions=1, setup="pass") -> Stats:
    """Measures the number of operations per second, meaning the
    number of times per second the benchmark method could be executed by
    computing the throughput as the number of repetitions divided by the sum of
    all method execution times.

    Runs `fn` for at least `min_repetitions` or 1.0 seconds.

    **Note**: Accurate measurements can only be obtained when `min_repetitions`
    is set to a large value. Otherwise scheduling or CPU load can influence the
    runtime of the function.

    **Note**: By default, `throughput()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    Args:
        fn (function): Function to benchmark.
        min_repetitions (int, optional): Minimum number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".

    Returns:
        dtypes.Stats(
            times: A list containing benchmark times in seconds.
        )
    """
    timer = timeit.Timer(stmt=fn, setup=setup)
    total_time = 0.0
    repetitions = 0
    times = []
    while total_time < 1.0 or repetitions < min_repetitions:
        time = timer.timeit(1)
        total_time += time
        repetitions += 1
        times.append(time)
    return Stats(times)


# TODO Checkout what https://github.com/python/pyperformance does to benchmark
# https://pyperf.readthedocs.io/en/latest/api.html

# TODO Checkout cProfile.Profile() vs timeit
# https://github.com/python-recsys/benchy/blob/master/benchy/benchmark.py#L58


# TODO Add support for memory benchmarks (memit)
# https://github.com/pythonprofilers/memory_profiler
# https://jakevdp.github.io/PythonDataScienceHandbook/01.07-timing-and-profiling.html
