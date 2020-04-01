import csv
import io
import json
import os
import pathlib
from abc import ABC
from abc import abstractmethod
from collections import OrderedDict
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from benchit import dtypes

try:
    import matplotlib.pyplot as plt
except:
    plt = None

_STATS_MAPPING = OrderedDict(
    [
        ("Repetitions", "repetitions"),
        ("Total Time", "total"),
        ("Mean", "mean"),
        ("Std", "std"),
        ("Std Outliers", "std_outliers"),
        ("Throughput", "throughput"),
        ("Throughput (Min)", "throughput_min"),
        ("Min", "minimum"),
        ("5th Percentile", "percentile_5th"),
        ("25th Percentile", "percentile_25th"),
        ("Median", "median"),
        ("75th Percentile", "percentile_75th"),
        ("95th Percentile", "percentile_95th"),
        ("Max", "maximum"),
    ]
)  # Mapping of human readable name to dtypes.Stats property

_METDATA_MAPPING = OrderedDict(
    [
        ("Timestamp", "timestamp"),
        ("Warmups", "warmups"),
        ("Name", "function_name"),
        ("Function", "function_str"),
        ("Setup", "setup"),
        ("File", "file"),
        ("Line", "line"),
        ("Args", "function_args"),
        ("Kwargs", "function_kwargs"),
        ("Unit", "unit"),
    ]
)  # Mapping of human readable name to dtypes.Stats property


class Format(Enum):
    """Enum of supported formatting types"""

    # Entries are duplicated to allow access by Format['markdown']
    # while retaining the upper case naming throughout the code.
    MARKDOWN = "markdown"
    markdown = "markdown"
    CSV = "csv"
    csv = "csv"
    JSON = "json"
    json = "json"
    PLOT = "plot"
    plot = "plot"

    @classmethod
    def to_enum(cls, str_or_format: Union[str, "Format"]) -> "Format":
        """Converts a `str` or `Format` to a `Format`.

        Args:
            str_or_format (Union[str, Format]): A string or `Format` to be
                converted into a `Format` enum.

        Raises:
            ValueError: If a string is passed that is not part of `Format`.

        Returns:
            Format: `str_or_format` if it already is of type `Format` else
                a `Format[str_or_format]` object.
        """
        if isinstance(str_or_format, Format):
            return str_or_format
        elif any(f.value == str_or_format for f in Format):
            return Format[str_or_format]
        else:
            raise ValueError(
                f"Unsupported format: {str_or_format}. "
                f"Only supports Format or one of: {[f.value for f in Format]}"
                " in UPPER or lower case."
            )


class FormattedStats(ABC):
    """Base class for formatting implementations of benchmarking results.

    Args:
        stats (dtypes.Stats): A benchmarking result.

    Raises:
        TypeError: If `stats` is not of type `dtypes.Stats`.
    """

    def __init__(self, stats: dtypes.Stats):
        if not isinstance(stats, dtypes.Stats):
            raise TypeError(f"stats has to be of type dtypes.Stats")
        self._stats: dtypes.Stats = stats

    @property
    def stats(self) -> dtypes.Stats:
        return self._stats

    @abstractmethod
    def resource(self):
        """Returns a formatted version of `stats`."""
        pass

    @abstractmethod
    def save(self, file: Union[str, pathlib.Path]) -> None:
        """Saves `resource` to a file."""
        pass


class Markdown(FormattedStats):
    """Formats `dtypes.Stats` to Markdown.

    Args:
        stats (dtypes.Stats): A benchmarking result.

    Raises:
        TypeError: If `stats` is not of type `dtypes.Stats`.
    """

    def __init__(self, stats: dtypes.Stats):
        super().__init__(stats)

        template = "| {} " * len(_METDATA_MAPPING) + "|"
        self._metadata_header = template.format(*_METDATA_MAPPING.keys())
        row = [getattr(stats, v) for v in _METDATA_MAPPING.values()]
        self._metadata_row = template.format(*row)

        template = "| {} " * len(_STATS_MAPPING) + "|"
        self._data_header = template.format(*_STATS_MAPPING.keys())
        row = [getattr(stats, v) for v in _STATS_MAPPING.values()]
        self._data_row = template.format(*row)

    def resource(self, append: bool = False) -> str:
        """Get `stats` formatted as Markdown.

        Args:
            append (bool, optional): If True, the Markdown will not include a header.
                Defaults to False.

        Returns:
            str: `stats` formatted as Markdown.
        """
        result = ""
        if not append:
            result += f"{self._metadata_header}{self._data_header[1:]}" + os.linesep
            result += (
                "| --- " * (len(_METDATA_MAPPING) + len(_STATS_MAPPING))
                + "|"
                + os.linesep
            )

        result += f"{self._metadata_row}{self._data_row[1:]}" + os.linesep

        return result

    def save(self, file: Union[str, pathlib.Path], append: bool = True) -> None:
        """Save formatted stats to a file.

        Args:
            file (Union[str, pathlib.Path]): The output file.
            append (bool, optional): If True, append the stats as a row to `file`
                if `file` already exists. If `file` does not exist, a new one will
                be created. Defaults to True.

        Raises:
            FileExistsError: If `append` is `False` but `file` already exists.
        """
        if not append and os.path.exists(file):
            raise FileExistsError(f"{file} already exists but 'append' is set to False")

        mode = "a" if append else "w"
        if append and not os.path.exists(file):
            mode = "w"
            append = False

        with open(file, mode, newline="") as f:
            f.write(self.resource(append))


class CSV(FormattedStats):
    """Formats `dtypes.Stats` to CSV.

    Args:
        stats (dtypes.Stats): A benchmarking result.

    Raises:
        TypeError: If `stats` is not of type `dtypes.Stats`.
    """

    def __init__(self, stats: dtypes.Stats):
        super().__init__(stats)

        self._metadata_header = _METDATA_MAPPING.keys()
        self._metadata_row = [getattr(stats, v) for v in _METDATA_MAPPING.values()]

        self._data_header = _STATS_MAPPING.keys()
        self._data_row = [getattr(stats, v) for v in _STATS_MAPPING.values()]

    def resource(self, append: bool = False) -> str:
        """Get `stats` formatted as CSV.

        Args:
            append (bool, optional): If True, the CSV will not include a header.
                Defaults to False.

        Returns:
            str: `stats` formatted as CSV.
        """
        csv_str = io.StringIO(newline="")

        writer = csv.writer(csv_str)

        if not append:
            writer.writerow(list(self._metadata_header) + list(self._data_header))

        writer.writerow(list(self._metadata_row) + list(self._data_row))

        return csv_str.getvalue()

    def save(self, file: Union[str, pathlib.Path], append: bool = True) -> None:
        """Save formatted stats to a file.

        Args:
            file (Union[str, pathlib.Path]): The output file.
            append (bool, optional): If True, append the stats as a row to `file`
                if `file` already exists. If `file` does not exist, a new one will
                be created. Defaults to True.

        Raises:
            FileExistsError: If `append` is `False` but `file` already exists.
        """
        if not append and os.path.exists(file):
            raise FileExistsError(
                f"{file} already exists but 'append' is set to False."
            )

        mode = "a" if append else "w"
        if append and not os.path.exists(file):
            mode = "w"
            append = False

        with open(file, mode, newline="") as f:
            f.write(self.resource(append))


class JSON(FormattedStats):
    """Formats `dtypes.Stats` to JSON.

    Args:
        stats (dtypes.Stats): A benchmarking result.

    Raises:
        TypeError: If `stats` is not of type `dtypes.Stats`.
    """

    def __init__(self, stats: dtypes.Stats):
        super().__init__(stats)

        self._metadata_header = _METDATA_MAPPING.keys()
        self._metadata_row = []
        for v in _METDATA_MAPPING.values():
            v = getattr(stats, v)
            if not isinstance(v, (str, float, bool, int)):
                # Turn non-trivial objects into their string representation
                v = str(v)
            self._metadata_row.append(v)

        self._data_header = _STATS_MAPPING.keys()
        self._data_row = [getattr(stats, v) for v in _STATS_MAPPING.values()]

    def resource(self, append: bool = False) -> Dict[str, Any]:
        """Get `stats` formatted as a JSON serializable dictionary.

        Args:
            append (bool, optional): If True, the dictionary will only be
                `{"metadata": ..., "data": ...}`. Defaults to False.

        Returns:
            Dict[str, Any]: `stats` formatted as a JSON serializable dictionary.
                In the form of `{"runs": [{"metadata": ..., "data": ...}]}`.
        """
        metadata = {
            header: row
            for (header, row) in zip(self._metadata_header, self._metadata_row)
        }

        data = {header: row for (header, row) in zip(self._data_header, self._data_row)}

        run = {"metadata": metadata, "data": data}

        if append:
            return run
        else:
            return {"runs": [run]}

    def save(self, file: Union[str, pathlib.Path], append: bool = True) -> None:
        """Save formatted stats to a file.

        Args:
            file (Union[str, pathlib.Path]): The output file.
            append (bool, optional): If True, append the stats to `file` under
                `runs: []` if `file` already exists. If `file` does not exist,
                a new one will be created. Defaults to True.

        Raises:
            FileExistsError: If `append` is `False` but `file` already exists.
        """
        if not append and os.path.exists(file):
            raise FileExistsError(f"{file} already exists but 'append' is set to False")

        if append and not os.path.exists(file):
            append = False

        if append:
            with open(file, "r") as f:
                old_data = json.load(f)
                old_data["runs"].append(self.resource(True))
            with open(file, "w", newline="") as f:
                f.write(json.dumps(old_data))
        else:
            with open(file, "w", newline="") as f:
                f.write(json.dumps(self.resource()))


class Plot(FormattedStats):
    """Formats `dtypes.Stats` to a variety of matplotlib plots.

    Args:
        stats (dtypes.Stats): A benchmarking result.

    Raises:
        TypeError: If `stats` is not of type `dtypes.Stats`.
    """

    def __init__(self, stats: dtypes.Stats, **kwargs):
        if plt is None:
            raise ImportError(
                "Matplotlib is not installed. Cannot use plot backend! Run "
                '"pip install maptlotlib" to use it.'
            )
        super().__init__(stats)
        # TODO
        self._fig = plt.Figure()

    def resource(self) -> plt.Figure:
        return self._fig

    def save(self, file: Union[str, pathlib.Path], metadata: bool = True) -> None:
        # TODO
        pass


def stats_as(
    stats: dtypes.Stats, style: Union[str, Format], **kwargs: Dict[str, Any]
) -> FormattedStats:
    style = Format.to_enum(style)
    if style is Format.CSV:
        return stats_as_csv(stats, **kwargs)
    elif style is Format.markdown:
        return stats_as_markdown(stats, **kwargs)
    elif style is Format.JSON:
        return stats_as_json(stats, **kwargs)
    elif style is Format.PLOT:
        return stats_as_plot(stats, **kwargs)


def stats_as_csv(stats: dtypes.Stats, **kwargs: Dict[str, Any]) -> CSV:
    return CSV(stats, **kwargs)


def stats_as_markdown(stats: dtypes.Stats, **kwargs: Dict[str, Any]) -> Markdown:
    return Markdown(stats, **kwargs)


def stats_as_json(stats: dtypes.Stats, **kwargs: Dict[str, Any]) -> JSON:
    return JSON(stats, **kwargs)


# TODO Maybe separate this from other formats and put into visualize.py
def stats_as_plot(stats: dtypes.Stats, **kwargs: Dict[str, Any]) -> Plot:
    if plt is not None:
        # TODO Checkout other projects to gather useful plots for time series data
        return Plot(stats)
    else:
        raise ImportError(
            "Matplotlib is not installed. Cannot use plot backend! Run "
            '"pip install maptlotlib" to use it.'
        )
