import os
import pathlib
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import TextIO
from typing import Union

from amifast import bench
from amifast import dtypes
from amifast import format


def benchit(
    repetitions: int,
    setup: Union[Callable, str] = "pass",
    warmups: int = 1,
    enabled: bool = True,
) -> Union[Callable, dtypes.Stats]:
    """Decorator for `bench.benchit()`.

    Args:
        repetitions (int): Number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`.
            Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard.
            Defaults to 1.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True
             Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.

    Returns:
        Union[Callable, dtypes.Stats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.Stats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            stats = bench.benchit(
                function,
                repetitions,
                setup,
                warmups,
                fn_args=args,
                fn_kwargs=wrapper_kwargs,
            )
            return stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def single_shot(
    setup: Union[Callable, str] = "pass", warmups: int = 1, enabled: bool = True
) -> Union[Callable, dtypes.Stats]:
    """Decorator for `bench.single_shot()`.

    Args:
        setup (str, optional): A function to run once before each call to `fn`.
            Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard.
            Defaults to 1.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.
            Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.

    Returns:
        Union[Callable, dtypes.Stats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.Stats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            stats = bench.single_shot(
                function, setup, warmups, fn_args=args, fn_kwargs=wrapper_kwargs
            )
            return stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def throughput(
    min_repetitions=1, setup="pass", warmups: int = 1, enabled=True
) -> Union[Callable, dtypes.Stats]:
    """Decorator for `bench.throughput()`.

    Args:
        min_repetitions (int, optional): Minimum number of times to benchmark function.
        setup (str, optional): A function to run once before each call to `fn`.
            Defaults to "pass".
        warmups (int, optional): The number of initial repetitions to discard.
            Defaults to 1.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.
            Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.

    Returns:
        Union[Callable, dtypes.Stats]: If `enabled`, applies the wrapper
            which will benchmark the function and return a `dtypes.Stats` object.
            If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            stats = bench.throughput(
                function,
                min_repetitions,
                setup,
                warmups,
                fn_args=args,
                fn_kwargs=wrapper_kwargs,
            )
            return stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def stats_as(
    style: str, enabled: bool = True, **kwargs: Dict[str, Any]
) -> Union[Callable, format.FormattedStats]:
    """Decorator for `format.stats_as()`.

    Args:
        style (str): Format of the benchmarking result. One of: csv, markdown, plot.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.
            Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.
        **kwargs (Dict[str, Any], optional): Additional arguments passed to `stats_as()`.

    Raises:
        TypeError: If wrapped function does not return a `dtypes.Stats` object.

    Returns:
        Union[Callable, format.FormattedStats]: If `enabled`, applies the wrapper
            which will format the result of a benchmarking decorator into the
            appropriate style. If False, this will be a no-op which returns the
            wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            result = function(*args, **wrapper_kwargs)

            if not isinstance(result, dtypes.Stats):
                raise TypeError(
                    f"@stats_as can only be used on functions that return dtypes.Stats. "
                    "Note: @stats_as should always be declared before a benchmarking "
                    "decorator such as @amifast, @single_shot, @throughput!"
                )

            formatted_stats = format.stats_as(result, style=style, **kwargs)

            return formatted_stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def save(
    file: Union[str, pathlib.Path], enabled: bool = True, **kwargs,
) -> Union[Callable, format.FormattedStats]:
    """Decorator for `format.FormattedStats.save()`.

    Args:
        file (Union[str, pathlib.Path]): Filename where stats will be saved.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.
            Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.
        **kwargs (Dict[str, Any], optional): Additional arguments passed to `save()`.

    Raises:
        TypeError: If wrapped function does not return a `format.FormattedStats` object.

    Returns:
        Union[Callable, format.FormattedStats]: If `enabled`, applies the wrapper
            which will save the formatted benchmarking results and returns the
            `format.FormattedStats` again. If False, this will be a no-op which
            returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            formatted_stats = function(*args, **wrapper_kwargs)

            if not isinstance(formatted_stats, format.FormattedStats):
                raise TypeError(
                    f"@save can only be used on functions that return format.FormattedStats. "
                    "Note: @save should always be declared before @stats_as!"
                )

            formatted_stats.save(file, **kwargs)

            return formatted_stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner


def validate(
    file: TextIO, enabled: bool = True, **kwargs,
) -> Union[Callable, dtypes.Stats]:
    """Decorator for `dtypes.Stats.validate()`.

    Args:
        file (TextIO): An I/O stream for text such as returned by `open()`.
        enabled (bool, optional): Enable or disable the wrapper. Defaults to True.
            Note: The wrapper is also disabled if `ENV['ENABLE_BENCHMARKING'] == 0`.
        **kwargs (Dict[str, Any], optional): Additional arguments passed to `validate()`.

    Raises:
        TypeError: If wrapped function does not return a `dtypes.Stats` object.

    Returns:
        Union[Callable, dtypes.Stats]: If `enabled`, applies the wrapper
            which validate the benchmarking results and returns the `dtypes.Stats`
            object. If False, this will be a no-op which returns the wrapped function.
    """

    def inner(function):
        @wraps(function)
        def wrapper(*args, **wrapper_kwargs):
            stats = function(*args, **wrapper_kwargs)

            if not isinstance(stats, dtypes.Stats):
                raise TypeError(
                    f"@validate can only be used on functions that return dtypes.Stats. "
                    "Note: @validate should always be declared before a benchmarking "
                    "decorator such as @amifast, @single_shot, @throughput or any "
                    "other decorator that returns dtypes.Stats!"
                )

            stats.validate(**kwargs)

            return stats

        if os.getenv("ENABLE_BENCHMARKING", None) == "0" or not enabled:
            wrapper = function

        return wrapper

    return inner
