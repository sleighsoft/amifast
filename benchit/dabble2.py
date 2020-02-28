from typing import NamedTuple, List
import statistics


class Stats(NamedTuple):
    times: List[float]

    def mean(self):
        """Computes the mean of a time series."""
        return statistics.mean(self.times)


t = Stats([0.1, 0.2])
print(t.mean())
