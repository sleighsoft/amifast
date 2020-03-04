import statistics
import math
import inspect
import time
from typing import List, NamedTuple, Dict, Callable

from utils import cached_property


class Stats(object):
    """General Stats object created by benchmarking functions.
    
    Has the following statistics:
        * mean
        * std
        * std_outliers
        * repetitions
        * total
        * throughput
        * throughput_min
        * minimum | percentile_0th
        * percentile_5th
        * percentile_25th
        * median | percentile_50th
        * percentile_75th
        * percentile_95th
        * maximum | percentile_100th

    It supports seamless conversion between different time units:
        * ns
        * us
        * ms
        * s
        * m
        * h
        * d
    """

    def __init__(self, times: List[float]):
        """Create a Stats object given timing results from a benchmarking run.
        
        Args:
            times (List[float]): A list of benchmarking times in seconds.
        """
        self._times = times
        self._unit = "s"

    @property
    def times(self) -> List[float]:
        """Benchmarking times."""
        return self._times

    @property
    def unit(self):
        """Time unit. One of [ns, us, ms, s, m, h, d]."""
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
        using the number of repetitions and the total runtime.
        
        Note: This is `math.nan` if `total==0`.
        """
        if self.total == 0:
            return math.nan

        return self.repetitions / self.total

    @cached_property
    def throughput_min(self) -> float:
        """Computes the number of operations per second in this time series
        using the minimum runtime over all runs.
        
        Note: This is `math.nan` if `minimum==0`.
        """
        if self.minimum == 0:
            return math.nan

        return 1.0 / self.minimum

    def _percentile(self, p):
        if not isinstance(p, float) or not (0.0 <= p <= 1.0):
            raise ValueError("p must be a float in the range [0.0; 1.0]")

        times = sorted(self._times)
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

    def to_nanoseconds(self):
        """Converts `self.time` from the current `self.unit` to nanoseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "ns":
            self._invalidate_cache()
            self._times = [self._conversion_fn("ns")(t) for t in self._times]
            self._unit = "ns"

    def to_microseconds(self):
        """Converts `self.time` from the current `self.unit` to microseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "us":
            self._invalidate_cache()
            self._times = [self._conversion_fn("us")(t) for t in self._times]
            self._unit = "us"

    def to_milliseconds(self):
        """Converts `self.time` from the current `self.unit` to milliseconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "ms":
            self._invalidate_cache()
            self._times = [self._conversion_fn("ms")(t) for t in self._times]
            self._unit = "ms"

    def to_seconds(self):
        """Converts `self.time` from the current `self.unit` to seconds.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "s":
            self._invalidate_cache()
            self._times = [self._conversion_fn("s")(t) for t in self._times]
            self._unit = "s"

    def to_minutes(self):
        """Converts `self.time` from the current `self.unit` to minutes.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "m":
            self._invalidate_cache()
            self._times = [self._conversion_fn("m")(t) for t in self._times]
            self._unit = "m"

    def to_hours(self):
        """Converts `self.time` from the current `self.unit` to hours.
        
        Note: This invalidates all cached_properties!
        """
        if self.unit != "h":
            self._invalidate_cache()
            self._times = [self._conversion_fn("h")(t) for t in self._times]
            self._unit = "h"

    def to_days(self):
        """Converts `self.time` from the current `self.unit` to days.
        
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


class FunctionStats(Stats):
    """Adds additional statistics about the benchmarked function.

    Added properties are:
        - The function `name`.
        - The `file` the function is defined in.
        - The `line` at which the function starts.
        - A `timestamp` of when this object was created.

    Usually created by the benchmarking decorators in `decorators`.
    """

    def __init__(self, times_or_stats, function, timestamp=None):
        if isinstance(times_or_stats, Stats):
            times_or_stats = times_or_stats.times
        super().__init__(times_or_stats)
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
