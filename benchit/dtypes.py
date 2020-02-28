import statistics
import math
import inspect
import time
from typing import List, NamedTuple, Dict

from utils import cached_property


class Stats(object):
    """General Stats object created by benchmarking functions."""

    def __init__(self, times: List[float]):
        self._times = times

    @property
    def times(self) -> List[float]:
        return self._times

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


class FunctionStats(Stats):
    """Adds additional statistics about the benchmarked function.

    Usually created by the benchmarking decorators.
    """

    def __init__(self, times, function):
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
        self._timestamp = time.time()

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
    bits: str
    machine_type: str
    platform_string: str
    processor: str
    processor_brand: str
    processor_architecture: str
    python_impl: str
    python_version: str
    python_packages: Dict[str, str]