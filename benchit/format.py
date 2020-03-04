import io
import csv
import os

from dtypes import Stats

_STATS_HEADER = [
    "Min",
    "Max",
    "Mean",
    "Median",
    "Std",
    "Std Outliers",
    "Repetitions",
    "Total Time",
    "Throughput",
    "Throughput (Min)",
]


def stats_as(stats: Stats, style: str = "csv", **kwargs):
    if style == "csv":
        return stats_as_csv(stats, **kwargs)
    elif style == "markdown":
        return stats_as_markdown(stats, **kwargs)
    elif style == "plot":
        return stats_as_plot(stats, **kwargs)
    else:
        raise ValueError(
            f"Unsupported conversion style: {style}. "
            "Only support [csv, markdown, plot]."
        )


def stats_as_csv(stats: Stats, header: bool = True, **kwargs) -> str:
    csv_str = io.StringIO()

    writer = csv.writer(csv_str, **kwargs)

    if isinstance(stats, Stats):
        if header:
            writer.writerow(_STATS_HEADER)

        row = [
            stats.minimum,
            stats.maximum,
            stats.mean,
            stats.median,
            stats.std,
            stats.std_outliers,
            stats.repetitions,
            stats.total,
            stats.throughput,
            stats.throughput_min,
        ]
        writer.writerow(row)

    else:
        raise TypeError(f"stats has to be of type dtypes.Stats")

    return csv_str.getvalue()


def stats_as_markdown(stats: Stats, header: bool = True, **kwargs) -> str:
    md_str = io.StringIO()

    if isinstance(stats, Stats):
        if header:
            header = "| " + " | ".join(_STATS_HEADER) + " |"
            header_length = len(_STATS_HEADER)
            md_str.write(header + os.linesep)
            md_str.write("|" + ": --- :|" * header_length + os.linesep)

        row = (
            f"| {stats.minimum} | {stats.maximum} | {stats.mean} | {stats.median} | "
            f"{stats.std} | {stats.std_outliers} | {stats.repetitions} | "
            f"{stats.total} | {stats.throughput} | {stats.throughput_min} |"
        )
        md_str.write(row + os.linesep)
    else:
        raise TypeError(f"stats has to be of type dtypes.Stats")

    return md_str.getvalue()


# TODO Maybe separate this from other formats and put into visualize.py
def stats_as_plot(stats: Stats, **kwargs):
    try:
        import matplotlib.pyplot as plt

        # TODO Checkout other projects to gather useful plots
        return plt.Figure()
    except Exception:
        raise ImportError(
            "Matplotlib is not installed. Cannot use plot backend! Run "
            '"pip install maptlotlib" to use.'
        )
