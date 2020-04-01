"""
benchit: simple powerful benchmarking with Python
"""
from benchit import decorators
from benchit import dtypes
from benchit import format
from benchit.bench import benchit
from benchit.bench import single_shot
from benchit.bench import throughput
from benchit.config import main
from benchit.decorators import benchit as d_benchit
from benchit.decorators import save as d_save
from benchit.decorators import single_shot as d_single_shot
from benchit.decorators import stats_as as d_stats_as
from benchit.decorators import throughput as d_throughput
from benchit.decorators import validate as d_validate
from benchit.format import stats_as


try:
    from ._version import version as __version__
except ImportError:
    # broken installation, we don't even try
    # unknown only works because we do poor mans version compare
    __version__ = "unknown"

__all__ = [
    "benchit",
    "throughput",
    "single_shot",
    "stats_as",
    "d_benchit",
    "d_throughput",
    "d_single_shot",
    "d_stats_as",
    "d_save",
    "d_validate",
    "dtypes",
    "format",
    "decorators",
    "main",
    "__version__",
]
