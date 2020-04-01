import inspect
import math
import statistics
import sys
import time
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TextIO
from typing import Tuple
from typing import Union

from amifast.utils import cached_property


class TimeUnit(Enum):
    """Unit of time.

    One of:
    - nanoseconds
    - microseconds
    - milliseconds
    - seconds
    - minutes
    - hours
    - days
    """

    NS = 1
    US = 2
    MS = 3
    S = 4
    M = 5
    H = 6
    D = 7


class Stats(object):
    """Stats object created by benchmarking functions.

    Stores:

        - The benchmarking times.
        - The number of performed warmup runs.
        - The function `name`.
        - The `file` the function is defined in.
        - The `line` at which the function starts.
        - A `timestamp` of when this object was created.

    Has the following statistics:

        - raw_times
        - times
        - repetitions
        - total
        - mean
        - std
        - std_outliers
        - throughput
        - throughput_min
        - minimum | percentile_0th
        - percentile_5th
        - percentile_25th
        - median | percentile_50th
        - percentile_75th
        - percentile_95th
        - maximum | percentile_100th

    Has the following metadata:

        - timestamp
        - warmups
        - function_name
        - function
        - setup
        - file
        - line
        - function_args
        - function_kwargs
        - unit

    It supports seamless conversion between different time units:

        - ns
        - us
        - ms
        - s
        - m
        - h
        - d

    Args:
        times (List[float]): A list of benchmarking times in seconds.
        function (Callable): The benchmarked function.
        warmups (int): Number of warmups.
        setup (Union[str, Callable]): Setup performed before the function was benchmarked.
        timestamp (Optional[float]): A timestamp of when this benchmark was performed. Defaults to `time.time()`.
        fn_args (Optional[Tuple[Any, ...]], optional): Positional arguments passed to `fn`. Defaults to None.
        fn_kwargs (Optional[Dict[str, Any]], optional): Keyword arguments passed to `fn`. Defaults to None.
    """

    def __init__(
        self,
        times: List[float],
        function: Union[Callable, str],
        warmups: int,
        setup: Union[str, Callable] = "pass",
        timestamp: Optional[float] = None,
        fn_args: Optional[Tuple[Any, ...]] = None,
        fn_kwargs: Optional[Dict[str, Any]] = None,
    ):
        if warmups >= len(times):
            raise ValueError(
                f"warmups >= len(times)={len(times)} ! No timing data will be available."
            )
        self._times = times
        self._warmups = warmups
        self._setup = setup
        self._function = function
        if callable(function):
            self._name = function.__name__
            if inspect.isbuiltin(function):
                self._file = None
                self._line = None
            else:
                self._file = inspect.getsourcefile(function)
                try:
                    self._line = inspect.getsourcelines(function)[1]
                except OSError:
                    self._line = None
        else:
            self._name = None
            self._file = None
            self._line = None
        self._timestamp = time.time() if timestamp is None else timestamp
        self._function_args = fn_args
        self._function_kwargs = fn_kwargs

        self._unit = TimeUnit.S

    @property
    def raw_times(self):
        """Benchmarking times, including the warmup runs.

        Not used for statistics. See self.times instead.
        """
        return self._times

    @property
    def times(self) -> List[float]:
        """Benchmarking times without the warmup runs.

        All statistics are calculated using this.
        """
        return self.raw_times[self.warmups :]

    @property
    def warmups(self) -> int:
        """Number of performed warmup runs."""
        return self._warmups

    @property
    def function_name(self) -> Optional[str]:
        """The name of the benchmarked function.

        Only available if `function` is callable.
        """
        return self._name

    @property
    def function(self) -> Union[Callable, str]:
        """The benchmarked function."""
        return self._function

    @cached_property
    def function_str(self) -> str:
        """The string representation of the benchmarked function."""
        fn = self.function
        if callable(fn):
            # Remove "at <address>"
            fn = str(fn)
            fn = fn[: fn.find(" at ")] + ">"
        return fn

    @property
    def function_args(self) -> Optional[Tuple[Any, ...]]:
        """Positional arguments passed to `function`."""
        return self._function_args

    @property
    def function_kwargs(self) -> Optional[Dict[str, Any]]:
        """Keyword arguments passed to `function`."""
        return self._function_kwargs

    @property
    def setup(self) -> Union[Callable, str]:
        """The setup function run once before each call to `function`."""
        return self._setup

    @property
    def unit(self) -> TimeUnit:
        """Time unit."""
        return self._unit

    @property
    def file(self) -> Optional[str]:
        """The filename of the file where the function is defined in.

        Only available if `function` is callable.
        """
        return self._file

    @property
    def line(self) -> Optional[int]:
        """The line at which the function is defined in `file`.

        Only available if `function` is callable.
        """
        return self._line

    @property
    def timestamp(self) -> float:
        """A `timestamp` of when this object was created."""
        return self._timestamp

    @cached_property
    def minimum(self) -> float:
        """The minimum of this time series."""
        return min(self.times)

    @cached_property
    def maximum(self) -> float:
        """The maximum of this time series."""
        return max(self.times)

    @cached_property
    def mean(self) -> float:
        """The mean of this time series."""
        return statistics.mean(self.times)

    @cached_property
    def std(self) -> float:
        """The standard deviation of this time series."""
        if self.repetitions < 2:
            return 0.0

        return statistics.stdev(self.times)

    @cached_property
    def median(self) -> float:
        """The median of this time series."""
        return statistics.median(self.times)

    @cached_property
    def std_outliers(self) -> int:
        """Counts the number of standard deviation outliers of this time series."""
        std = self.std
        mean = self.mean
        quartile0 = mean - std
        quartile4 = mean + std
        count = 0
        for t in self.times:
            if t < quartile0 or t > quartile4:
                count += 1
        return count

    @cached_property
    def repetitions(self) -> int:
        """Return the number of entries in this time series."""
        return len(self.times)

    @cached_property
    def total(self) -> float:
        """The total amount of time in this time series."""
        return sum(self.times)

    @cached_property
    def throughput(self) -> float:
        """The number of operations per second in this time series
        using the number of repetitions and the total runtime.

        Note: This is `math.nan` if `total==0`.
        """
        if self.total == 0.0:
            return math.nan

        return self.repetitions / self.total

    @cached_property
    def throughput_min(self) -> float:
        """The number of operations per second in this time series
        using the minimum runtime over all runs.

        Note: This is `math.nan` if `minimum==0`.
        """
        if self.minimum == 0.0:
            return math.nan

        return 1.0 / self.minimum

    def _percentile(self, p):
        if not isinstance(p, float) or not (0.0 <= p <= 1.0):
            raise ValueError("p must be a float in the range [0.0; 1.0]")

        times = sorted(self.times)
        k = (len(times) - 1) * p
        f = int(math.floor(k))
        c = int(math.ceil(k))
        if f != c:
            # weighted percentile
            d0 = times[f] * (c - k)
            d1 = times[c] * (k - f)
            return d0 + d1
        else:
            return times[int(k)]

    @property
    def percentile_0th(self):
        """The 0th percentile. Identical to the minimum."""
        return self.minimum

    @cached_property
    def percentile_5th(self):
        """The 5th percentile."""
        return self._percentile(0.05)

    @cached_property
    def percentile_25th(self):
        """The 25th percentile."""
        return self._percentile(0.25)

    @property
    def percentile_50th(self):
        """The 50th percentile. Identical to the median."""
        return self.median

    @cached_property
    def percentile_75th(self):
        """The 75th percentile."""
        return self._percentile(0.75)

    @cached_property
    def percentile_95th(self):
        """The 95th percentile."""
        return self._percentile(0.95)

    @property
    def percentile_100th(self):
        """The 100th percentile. Identical to the maximum."""
        return self.maximum

    def validate(self, file: Optional[TextIO] = sys.stdout) -> List[str]:
        """Validates the bechmark times.

        Checks for:
        - Large standard deviation compared to mean (>10%)
        - Minimum timing less than 1ms

        Args:
            file (Optional[TextIO], optional): A file-like object to print warnings
                to. Defaults to sys.stdout.

        Returns:
            List[str]: A list of all warnings. Empty, if no warnings.
        """
        # TODO Improve
        # - Overall small number of values
        warnings = []
        if len(self.times) >= 2:
            # Large standard deviation compared to mean
            std = self.std()
            mean = self.mean()
            percent = std * 100.0 / mean
            if percent >= 10.0:
                warnings.append(
                    f"the standard deviation ({std}) is {percent}% of the mean ({mean})"
                )

        min_in_ms = self._conversion_fn(TimeUnit.MS)(self.minimum())
        if min_in_ms < 1.0:
            # Minimum timing less than 1ms
            warnings.append(f"the mininum timing ({min_in_ms}) was less than 1ms")

        if warnings and file:
            print("WARNING: the benchmark result may be unstable", file=file)
            for warning in warnings:
                print(f"- {warning}", file=file)

        return warnings

    def to_nanoseconds(self):
        """Converts `self.time` from the current `self.unit` to nanoseconds.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.NS:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.NS)(t) for t in self._times]
            self._unit = TimeUnit.NS

    def to_microseconds(self):
        """Converts `self.time` from the current `self.unit` to microseconds.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.US:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.US)(t) for t in self._times]
            self._unit = TimeUnit.US

    def to_milliseconds(self):
        """Converts `self.time` from the current `self.unit` to milliseconds.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.MS:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.MS)(t) for t in self._times]
            self._unit = TimeUnit.MS

    def to_seconds(self):
        """Converts `self.time` from the current `self.unit` to seconds.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.S:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.S)(t) for t in self._times]
            self._unit = TimeUnit.S

    def to_minutes(self):
        """Converts `self.time` from the current `self.unit` to minutes.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.M:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.M)(t) for t in self._times]
            self._unit = TimeUnit.M

    def to_hours(self):
        """Converts `self.time` from the current `self.unit` to hours.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.H:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.H)(t) for t in self._times]
            self._unit = TimeUnit.H

    def to_days(self):
        """Converts `self.time` from the current `self.unit` to days.

        Note: This invalidates all cached_properties!
        """
        if self.unit != TimeUnit.D:
            self._invalidate_cache()
            self._times = [self._conversion_fn(TimeUnit.D)(t) for t in self._times]
            self._unit = TimeUnit.D

    def _conversion_fn(self, target, unit=None) -> Callable[[float], float]:
        """Determines the conversion between `self.unit` and `target`.

        Args:
            target (str): The target time unit. One of `[ns, us, ms, s, m, h, d]`.
            unit (str, optional): The unit to convert to. If None, uses `self.unit`.

        Returns:
            Callable[[float], float]: A function that converts a time from `unit` to `target`.
        """
        unit = unit if unit else self.unit
        if unit == TimeUnit.NS:
            if target == TimeUnit.US:
                return lambda x: x / 1e3
            elif target == TimeUnit.MS:
                return lambda x: x / 1e6
            elif target == TimeUnit.S:
                return lambda x: x / 1e9
            elif target == TimeUnit.M:
                return lambda x: x / (60 * 1e9)
            elif target == TimeUnit.H:
                return lambda x: x / (60 * 60 * 1e9)
            elif target == TimeUnit.D:
                return lambda x: x / (24 * 60 * 60 * 1e9)
        elif unit == TimeUnit.US:
            if target == TimeUnit.NS:
                return lambda x: x * 1e3
            elif target == TimeUnit.MS:
                return lambda x: x / 1e3
            elif target == TimeUnit.S:
                return lambda x: x / 1e6
            elif target == TimeUnit.M:
                return lambda x: x / (60 * 1e6)
            elif target == TimeUnit.H:
                return lambda x: x / (60 * 60 * 1e6)
            elif target == TimeUnit.D:
                return lambda x: x / (24 * 60 * 60 * 1e6)
        elif unit == TimeUnit.MS:
            if target == TimeUnit.NS:
                return lambda x: x * 1e6
            elif target == TimeUnit.US:
                return lambda x: x * 1e3
            elif target == TimeUnit.S:
                return lambda x: x / 1e3
            elif target == TimeUnit.M:
                return lambda x: x / (60 * 1e3)
            elif target == TimeUnit.H:
                return lambda x: x / (60 * 60 * 1e3)
            elif target == TimeUnit.D:
                return lambda x: x / (24 * 60 * 60 * 1e3)
        elif unit == TimeUnit.S:
            if target == TimeUnit.NS:
                return lambda x: x * 1e9
            elif target == TimeUnit.US:
                return lambda x: x * 1e6
            elif target == TimeUnit.MS:
                return lambda x: x * 1e3
            elif target == TimeUnit.M:
                return lambda x: x / 60
            elif target == TimeUnit.H:
                return lambda x: x / (60 * 60)
            elif target == TimeUnit.D:
                return lambda x: x / (24 * 60 * 60)
        elif unit == TimeUnit.M:
            if target == TimeUnit.NS:
                return lambda x: x * 60 * 1e9
            elif target == TimeUnit.US:
                return lambda x: x * 60 * 1e6
            elif target == TimeUnit.MS:
                return lambda x: x * 60 * 1e3
            elif target == TimeUnit.S:
                return lambda x: x * 60
            elif target == TimeUnit.H:
                return lambda x: x / 60
            elif target == TimeUnit.D:
                return lambda x: x / (24 * 60)
        elif unit == TimeUnit.H:
            if target == TimeUnit.NS:
                return lambda x: x * 60 * 60 * 1e9
            elif target == TimeUnit.US:
                return lambda x: x * 60 * 60 * 1e6
            elif target == TimeUnit.MS:
                return lambda x: x * 60 * 60 * 1e3
            elif target == TimeUnit.S:
                return lambda x: x * 60 * 60
            elif target == TimeUnit.M:
                return lambda x: x * 60
            elif target == TimeUnit.D:
                return lambda x: x / 24
        elif unit == TimeUnit.D:
            if target == TimeUnit.NS:
                return lambda x: x * 24 * 60 * 60 * 1e9
            elif target == TimeUnit.US:
                return lambda x: x * 24 * 60 * 60 * 1e6
            elif target == TimeUnit.MS:
                return lambda x: x * 24 * 60 * 60 * 1e3
            elif target == TimeUnit.S:
                return lambda x: x * 24 * 60 * 60
            elif target == TimeUnit.M:
                return lambda x: x * 24 * 60
            elif target == TimeUnit.H:
                return lambda x: x * 24
        else:
            raise ValueError(f"unit has an incorrect type: {unit}")

    def _invalidate_cache(self):
        """Invalidates all cached_properties."""
        if "minimum" in self.__dict__:
            del self.__dict__["minimum"]
        if "maximum" in self.__dict__:
            del self.__dict__["maximum"]
        if "mean" in self.__dict__:
            del self.__dict__["mean"]
        if "std" in self.__dict__:
            del self.__dict__["std"]
        if "median" in self.__dict__:
            del self.__dict__["median"]
        if "std_outliers" in self.__dict__:
            del self.__dict__["std_outliers"]
        if "repetitions" in self.__dict__:
            del self.__dict__["repetitions"]
        if "total" in self.__dict__:
            del self.__dict__["total"]
        if "throughput" in self.__dict__:
            del self.__dict__["throughput"]
        if "throughput_min" in self.__dict__:
            del self.__dict__["throughput_min"]
        if "percentile_5th" in self.__dict__:
            del self.__dict__["percentile_5th"]
        if "percentile_25th" in self.__dict__:
            del self.__dict__["percentile_25th"]
        if "percentile_75th" in self.__dict__:
            del self.__dict__["percentile_75th"]
        if "percentile_95th" in self.__dict__:
            del self.__dict__["percentile_95th"]

    # TODO Print a summary / __repr__


class Benchmark(object):
    """Container for `SystemStatistics` as well as multiple `Stats`."""

    # TODO Add data structure that combines SystemStatistics with multiple Stats,
    # potentially from various functions.
    # StatsTimeline
