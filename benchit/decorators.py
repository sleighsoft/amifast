from functools import wraps
import os

import dtypes
import bench
import format


def benchit(repetitions, setup="pass", enabled=True):
    """Decorator for `bench.benchit()`."""

    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            stats = bench.benchit(function, repetitions, setup, *args, **kwargs)
            return dtypes.FunctionStats(stats, function)

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def single_shot(setup="pass", enabled=True):
    """Decorator for `bench.single_shot()`."""

    def inner(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            stats = bench.single_shot(function, setup, *args, **kwargs)
            return dtypes.FunctionStats(stats, function)

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def throughput(min_repetitions=1, setup="pass", enabled=True):
    """Decorator for `bench.throughput()`."""

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
