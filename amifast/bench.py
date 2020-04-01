import timeit
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from amifast.dtypes import Stats


def _wrap_function_if_callable(
    fn: Union[str, Callable], args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {},
) -> Union[str, Callable]:
    """Wraps a function call with its `args` and `kwargs` into a lambda if
    either is provided. If `fn` is not callable simply returns it.

    Used to properly handle functions with arguments.

    Args:
        fn (function): Function to wrap into a lambda
        args (Tuple[Any, ...]): Positional arguments passed to `fn`. Defaults to `()`.
        kwargs (Dict[str, Any]): Keyword arguments passed to `fn`. Defaults to `{}`.

    Returns:
        Union[str, Callable]: A wrapped function call or `fn`.
    """
    if callable(fn) and (args or kwargs):
        return lambda: fn(*args, **kwargs)
    else:
        return fn


def benchit(
    fn: Union[Callable, str],
    repetitions: int,
    setup: Union[Callable, str] = "pass",
    warmups: int = 1,
    fn_args: Tuple[Any, ...] = (),
    fn_kwargs: Dict[str, Any] = {},
) -> Stats:
    """Bechmarks a function a number of times and returns a time series in seconds.

    **Note**: By default, `benchit()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    **Note**: If `fn` is a function and `fn_args` or `fn_kwargs` are provided the
    call to `fn` will be wrapped into a lambda with `lambda: fn(*fn_args, **fn_kwargs)`.
    This might add a very small overhead.

    Args:
        fn (Union[Callable, str]): Function to benchmark.
        repetitions (int): Number of times to benchmark function.
        setup (Union[Callable, str], optional): A function to run once before each call to `fn`. Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard. Defaults to 1.
        fn_args (Tuple[Any, ...], optional): Positional arguments passed to `fn`. Defaults to `()`.
        fn_kwargs (Dict[str, Any], optional): Keyword arguments passed to `fn`. Defaults to `{}`.

    Returns:
        dtypes.Stats: Benchmarking stats.
    """
    fn = _wrap_function_if_callable(fn, fn_args, fn_kwargs)
    timer = timeit.Timer(stmt=fn, setup=setup)
    times = timer.repeat(repetitions + warmups, 1)
    return Stats(times, fn, warmups, setup=setup, fn_args=fn_args, fn_kwargs=fn_kwargs)


def single_shot(
    fn: Union[Callable, str],
    setup: Union[Callable, str] = "pass",
    warmups: int = 0,
    fn_args: Tuple[Any, ...] = (),
    fn_kwargs: Dict[str, Any] = {},
) -> Stats:
    """Measures how long a single function execution takes to
    run. This is good to test how a function performs under a cold start.

    **Note**: By default, `single_shot()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    **Note**: If `fn` is a function and `fn_args` or `fn_kwargs` are provided the
    call to `fn` will be wrapped into a lambda with `lambda: fn(*fn_args, **fn_kwargs)`.
    This might add a very small overhead.

    Args:
        fn (Union[Callable, str]): Function to benchmark.
        setup (Union[Callable, str], optional): A function to run once before each call to `fn`. Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard. Defaults to 0.
        fn_args (Tuple[Any, ...], optional): Positional arguments passed to `fn`. Defaults to `()`.
        fn_kwargs (Dict[str, Any], optional): Keyword arguments passed to `fn`. Defaults to `{}`.

    Returns:
        dtypes.Stats: Benchmarking stats.
    """
    return benchit(
        fn, 1, setup=setup, warmups=warmups, fn_args=fn_args, fn_kwargs=fn_kwargs
    )


def throughput(
    fn: Union[Callable, str],
    min_repetitions: int = 1,
    setup: Union[Callable, str] = "pass",
    warmups: int = 1,
    fn_args: Tuple[Any, ...] = (),
    fn_kwargs: Dict[str, Any] = {},
) -> Stats:
    """Similar to `benchit`, but runs `fn` for at least `min_repetitions` or 1.0
    seconds. Useful to measure the throughput of a function. Meaning the
    number of times per second the function can be executed by
    computing the throughput as the number of repetitions divided by the sum of
    all function execution times.

    **Note**: Accurate measurements can only be obtained when the function either
    runs many times within a single second or when `min_repetitions` is set to a
    large value. Otherwise scheduling or CPU load can influence the
    runtime of the function.

    **Note**: By default, `throughput()` temporarily turns off garbage collection
    during the timing. The advantage of this approach is that it makes
    independent timings more comparable. The disadvantage is that GC may
    be an important component of the performance of the function being measured.
    If so, GC can be re-enabled with `setup=gc.enable()`.

    **Note**: If `fn` is a function and `fn_args` or `fn_kwargs` are provided the
    call to `fn` will be wrapped into a lambda with `lambda: fn(*fn_args, **fn_kwargs)`.
    This might add a very small overhead.

    Args:
        fn (Union[Callable, str]): Function to benchmark.
        min_repetitions (int, optional): Minimum number of times to benchmark function.
        setup (Union[Callable, str], optional): A function to run once before each call to `fn`. Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard. Defaults to 1.
        fn_args (Tuple[Any, ...], optional): Positional arguments passed to `fn`. Defaults to `()`.
        fn_kwargs (Dict[str, Any], optional): Keyword arguments passed to `fn`. Defaults to `{}`.

    Returns:
        dtypes.Stats: Benchmarking stats.
    """
    fn = _wrap_function_if_callable(fn, fn_args, fn_kwargs)
    timer = timeit.Timer(stmt=fn, setup=setup)
    warmup_count = 0
    total_time = 0.0
    repetitions = 0
    times = []
    while total_time < 1.0 or repetitions < min_repetitions:
        time = timer.timeit(1)
        times.append(time)
        if warmup_count < warmups:
            warmup_count += 1
            continue
        total_time += time
        repetitions += 1
    return Stats(times, fn, warmups, setup=setup, fn_args=fn_args, fn_kwargs=fn_kwargs)


# TODO Checkout what https://github.com/python/pyperformance does to benchmark
# https://pyperf.readthedocs.io/en/latest/api.html
# https://github.com/vstinner/pyperf
# https://hackage.haskell.org/package/criterion
#  http://www.serpentine.com/criterion/tutorial.html

# TODO Add support for memory benchmarks (memit)
# https://github.com/pythonprofilers/memory_profiler
# https://jakevdp.github.io/PythonDataScienceHandbook/01.07-timing-and-profiling.html
