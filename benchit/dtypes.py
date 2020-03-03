import statistics
import math
import inspect
import time
from typing import List, NamedTuple, Dict, Callable

from benchit.utils import cached_property


class Stats(object):
    """General Stats object created by benchmarking functions."""

    def __init__(self, times: List[float]):
        """Create a Stats object for timing results from a benchmarking run.
        
        Args:
            times (List[float]): A list of benchmarking times in seconds.
        """
        self._times = times
        self._unit = "s"

    @property
    def times(self) -> List[float]:
        return self._times

    @property
    def unit(self):
        return self._unit

    @cached_property
    def minimum(self) -> float:
        """Computes the minimum of this time series."""
        return min(self._times)

    @cached_property
    def maximum(self) -> float:
        """Computes the maximum of this time series."""
        return max(self._times)

    @cached_property
    def mean(self) -> float:
        """Computes the mean of this time series."""
        return statistics.mean(self._times)

    @cached_property
    def std(self) -> float:
        """Computes the standard deviation of this time series."""
        if self.repetitions < 2:
            return 0.0

        return statistics.stdev(self._times)

    @cached_property
    def median(self) -> float:
        """Computes the median of this time series."""
        return statistics.median(self._times)

    @cached_property
    def std_outliers(self) -> int:
        """Counts the number of standard deviation outliers of this time series."""
        std = self.std
        mean = self.mean
        quartile0 = mean - std
        quartile4 = mean + std
        count = 0
        for t in self._times:
            if t < quartile0 or t > quartile4:
                count += 1
        return count

    @cached_property
    def repetitions(self) -> int:
        """Return the number of entries in this time series."""
        return len(self._times)

    @cached_property
    def total(self) -> float:
        """Computes the total amount of time in this time series."""
        return sum(self._times)

    @cached_property
    def throughput(self) -> float:
        """Computes the number of operations per second in this time series
        using the number of repetitions and the total runtime."""
        if self.total == 0:
            return math.nan

        return self.repetitions / self.total

    @cached_property
    def throughput_min(self) -> float:
        """Computes the number of operations per second in this time series
        using the minimum runtime over all runs."""
        if self.minimum == 0:
            return math.nan

        return 1.0 / self.minimum

    # TODO Add percentiles 0,5,25 (Q1),50 (median),75 (Q3),95,100

    def to_nanoseconds(self):
        """Converts self.time from seconds to nanoseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "ns":
            self._invalidate_cache()
            self._times = [self._conversion_fn("ns")(t) for t in self._times]
            self._unit = "ns"

    def to_microseconds(self):
        """Converts self.time from seconds to microseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "us":
            self._invalidate_cache()
            self._times = [self._conversion_fn("us")(t) for t in self._times]
            self._unit = "us"

    def to_milliseconds(self):
        """Converts self.time from seconds to milliseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "ms":
            self._invalidate_cache()
            self._times = [self._conversion_fn("ms")(t) for t in self._times]
            self._unit = "ms"

    def to_minutes(self):
        """Converts self.time from seconds to minutes.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "m":
            self._invalidate_cache()
            self._times = [self._conversion_fn("m")(t) for t in self._times]
            self._unit = "m"

    def to_hours(self):
        """Converts self.time from seconds to hours.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "h":
            self._invalidate_cache()
            self._times = [self._conversion_fn("h")(t) for t in self._times]
            self._unit = "h"

    def to_days(self):
        """Converts self.time from seconds to days.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "d":
            self._invalidate_cache()
            self._times = [self._conversion_fn("d")(t) for t in self._times]
            self._unit = "d"

    def _conversion_fn(self, target) -> Callable[[float], float]:
        """Determines the conversion between `self.unit` and `target`.
        
        Args:
            target (str): The target time unit. One of `[ns, us, ms, s, m, h, d]`.
        
        Returns:
            Callable[[float], float]: A function that converts self.float from`self.unit` to `targe
            
            Note: This invalidates all cached_properties!
            t`.
        """
        if self.unit == "ns":
            if target == "us":
                return lambda x: x / 1e3
            elif target == "ms":
                return lambda x: x / 1e6
            elif target == "s":
                return lambda x: x / 1e9
            elif target == "m":
                return lambda x: x / (60 * 1e9)
            elif target == "h":
                return lambda x: x / (60 * 60 * 1e9)
            elif target == "d":
                return lambda x: x / (24 * 60 * 60 * 1e9)
        elif self.unit == "us":
            if target == "ns":
                return lambda x: x * 1e3
            elif target == "ms":
                return lambda x: x / 1e3
            elif target == "s":
                return lambda x: x / 1e6
            elif target == "m":
                return lambda x: x / (60 * 1e6)
            elif target == "h":
                return lambda x: x / (60 * 60 * 1e6)
            elif target == "d":
                return lambda x: x / (24 * 60 * 60 * 1e6)
        elif self.unit == "ms":
            if target == "ns":
                return lambda x: x * 1e6
            elif target == "us":
                return lambda x: x * 1e3
            elif target == "s":
                return lambda x: x / 1e3
            elif target == "m":
                return lambda x: x / (60 * 1e3)
            elif target == "h":
                return lambda x: x / (60 * 60 * 1e3)
            elif target == "d":
                return lambda x: x / (24 * 60 * 60 * 1e3)
        elif self.unit == "s":
            if target == "ns":
                return lambda x: x * 1e9
            elif target == "us":
                return lambda x: x * 1e6
            elif target == "ms":
                return lambda x: x * 1e3
            elif target == "m":
                return lambda x: x / 60
            elif target == "h":
                return lambda x: x / (60 * 60)
            elif target == "d":
                return lambda x: x / (24 * 60 * 60)
        elif self.unit == "m":
            if target == "ns":
                return lambda x: x * 60 * 1e9
            elif target == "us":
                return lambda x: x * 60 * 1e6
            elif target == "ms":
                return lambda x: x * 60 * 1e3
            elif target == "s":
                return lambda x: x * 60
            elif target == "h":
                return lambda x: x / 60
            elif target == "d":
                return lambda x: x / (24 * 60)
        elif self.unit == "h":
            if target == "ns":
                return lambda x: x * 60 * 60 * 1e9
            elif target == "us":
                return lambda x: x * 60 * 60 * 1e6
            elif target == "ms":
                return lambda x: x * 60 * 60 * 1e3
            elif target == "s":
                return lambda x: x * 60 * 60
            elif target == "m":
                return lambda x: x * 60
            elif target == "d":
                return lambda x: x / 24
        elif self.unit == "d":
            if target == "ns":
                return lambda x: x * 24 * 60 * 60 * 1e9
            elif target == "us":
                return lambda x: x * 24 * 60 * 60 * 1e6
            elif target == "ms":
                return lambda x: x * 24 * 60 * 60 * 1e3
            elif target == "s":
                return lambda x: x * 24 * 60 * 60
            elif target == "m":
                return lambda x: x * 24 * 60
            elif target == "h":
                return lambda x: x * 24

    def _invalidate_cache(self):
        """Invalidates all cached_properties."""
        del self.__dict__["minimum"]
        del self.__dict__["maximum"]
        del self.__dict__["mean"]
        del self.__dict__["std"]
        del self.__dict__["median"]
        del self.__dict__["std_outliers"]
        del self.__dict__["repetitions"]
        del self.__dict__["total"]
        del self.__dict__["throughput"]
        del self.__dict__["throughput_min"]


class FunctionStats(Stats):
    """Adds additional statistics about the benchmarked function.

    Added properties are:
        - The function `name`.
        - The `file` the function is defined in.
        - The `line` at which the function starts.
        - A `timestamp` of when this object was created.

    Usually created by the benchmarking decorators in `decorators`.
    """

    def __init__(self, times, function, timestamp=None):
        if isinstance(times, Stats):
            times = times.times
        super().__init__(times)
        self._name = function.__name__
        if inspect.isbuiltin(function):
            self._file = None
            self._line = None
        else:
            self._file = inspect.getsourcefile(function)
            self._line = inspect.getsourcelines(function)[1]
        self._timestamp = time.time() if timestamp is None else timestamp

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def file(self) -> str:
        return self._file

    @property
    def line(self) -> int:
        return self._line


class SystemStatistics(NamedTuple):
    """Container class for various system statistics: Hardware, OS, Python,
    Installed Packages."""

    # Hardware
    bits: str
    machine_type: str
    processor: str
    processor_brand: str
    processor_architecture: str
    # OS
    platform_string: str
    # Python
    python_implementation: str
    python_version: str
    python_compiler: str
    python_build_no: str
    python_build_date: str
    python_branch: str
    python_revision: str
    # Packages
    python_installed_packages: Dict[str, str]


# TODO Add data structure that combines SystemStatistics with multiple Stats, potentially from various functions.
# StatsTimeline


class Benchmark(object):
    """Container for `SystemStatistics` as well as multiple `Stats`."""
