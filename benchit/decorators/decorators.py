import os
from functools import wraps
from typing import Callable
from typing import Union

import bench
import dtypes
import format


def benchit(
    repetitions, setup="pass", enabled=True
) -> Union[Callable, dtypes.FunctionStats]:
    """Decorator for `bench.benchit()`.

    Args:
        repetitions (int): Number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.

    Returns:
        Union[Callable, dtypes.FunctionStats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.FunctionStats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            stats = bench.benchit(function, repetitions, setup, *args, **kwargs)
            return dtypes.FunctionStats(stats, function)

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def single_shot(setup="pass", enabled=True) -> Union[Callable, dtypes.FunctionStats]:
    """Decorator for `bench.single_shot()`.

    Args:
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.

    Returns:
        Union[Callable, dtypes.FunctionStats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.FunctionStats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            stats = bench.single_shot(function, setup, *args, **kwargs)
            return dtypes.FunctionStats(stats, function)

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def throughput(
    min_repetitions=1, setup="pass", enabled=True
) -> Union[Callable, dtypes.FunctionStats]:
    """Decorator for `bench.throughput()`.

    Args:
        min_repetitions (int, optional): Minimum number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`. Defaults to "pass".
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.

    Returns:
        Union[Callable, dtypes.FunctionStats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.FunctionStats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            stats = bench.throughput(function, min_repetitions, setup, *args, **kwargs)
            return dtypes.FunctionStats(stats, function)

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def stats_as(style, **kwargs):
    """Decorator for `format.stats_as()`."""

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            result = function(*args, **wrapper_kwargs)

            if not isinstance(result, dtypes.Stats):
                raise TypeError(
                    f"@stats_as can only be used on functions that return dtypes.Stats"
                )

            formatted_times = format.stats_as(result, style=style, **kwargs)

            return formatted_times

        return wrapper

    return inner
