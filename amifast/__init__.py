"""
amifast: simple powerful benchmarking with Python
"""
from amifast import decorators
from amifast import dtypes
from amifast import format
from amifast.bench import benchit
from amifast.bench import single_shot
from amifast.bench import throughput
from amifast.config import main
from amifast.decorators import benchit as d_benchit
from amifast.decorators import save as d_save
from amifast.decorators import single_shot as d_single_shot
from amifast.decorators import stats_as as d_stats_as
from amifast.decorators import throughput as d_throughput
from amifast.decorators import validate as d_validate
from amifast.format import stats_as


try:
    from amifast._version import version as __version__
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
