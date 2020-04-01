"""
benchit: simple powerful benchmarking with Python
"""
from . import decorators
from . import dtypes
from . import format
from .bench import benchit
from .bench import single_shot
from .bench import throughput
from .config import main

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
    "dtypes",
    "format",
    "decorators",
    "main",
    "__version__",
]
