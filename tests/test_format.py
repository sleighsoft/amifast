import random
import pytest

import format
import dtypes
import os


def _test_csv(csv, header):
    assert isinstance(csv, str)
    splits = csv.split(os.linesep)
    if header:
        assert len(splits) == 3
        header, row, _ = splits
        assert len(header.split(",")) == len(format._STATS_HEADER)
        assert all([(h in header) for h in format._STATS_HEADER])
        assert len(row.split(",")) == len(format._STATS_HEADER)
    else:
        assert len(splits) == 2
        row, _ = splits
        assert all([(h not in row) for h in format._STATS_HEADER])
        assert len(row.split(",")) == len(format._STATS_HEADER)


def test_stats_as_csv():
    stats = dtypes.Stats([random.random() for _ in range(20)])

    # dtypes.Stats - With header
    csv = format.stats_as_csv(stats)
    _test_csv(csv, header=True)

    # dtypes.Stats - No header
    csv = format.stats_as_csv(stats, header=False)
    _test_csv(csv, header=False)

    stats = dtypes.FunctionStats(stats, lambda x: x)

    # dtypes.FunctionStats - With header
    csv = format.stats_as_csv(stats)
    _test_csv(csv, header=True)

    # dtypes.FunctionStats - No header
    csv = format.stats_as_csv(stats, header=False)
    _test_csv(csv, header=False)

    with pytest.raises(TypeError):
        format.stats_as_csv([1.0])


def _test_markdown(markdown, header):
    assert isinstance(markdown, str)
    splits = markdown.split(os.linesep)[:-1]
    if header:
        assert len(splits) == 3
        header, header_separator, row = splits
        header = [h.strip() for h in header.split("|")]
        assert all([(h in header) for h in format._STATS_HEADER])
        assert "|" + ": --- :|" * len(format._STATS_HEADER) == header_separator
        assert len(row.split("|")[1:-1]) == len(format._STATS_HEADER)
    else:
        assert len(splits) == 1
        row = splits[0]
        row = row.split("|")
        assert all([(h not in row) for h in format._STATS_HEADER])
        assert len(row[1:-1]) == len(format._STATS_HEADER)


def test_stats_as_markdown():
    stats = dtypes.Stats([random.random() for _ in range(20)])

    # dtypes.Stats - With header
    markdown = format.stats_as_markdown(stats)
    _test_markdown(markdown, header=True)

    # dtypes.Stats - No header
    markdown = format.stats_as_markdown(stats, header=False)
    _test_markdown(markdown, header=False)

    stats = dtypes.FunctionStats(stats, lambda x: x)

    # dtypes.FunctionStats - With header
    markdown = format.stats_as_markdown(stats)
    _test_markdown(markdown, header=True)

    # dtypes.FunctionStats - No header
    markdown = format.stats_as_markdown(stats, header=False)
    _test_markdown(markdown, header=False)

    with pytest.raises(TypeError):
        format.stats_as_markdown([1.0])


def test_stats_as():
    stats = dtypes.Stats([random.random() for _ in range(20)])

    # dtypes.Stats - With header
    csv = format.stats_as(stats, "csv", header=True)
    _test_csv(csv, header=True)

    # dtypes.Stats - No  header
    csv = format.stats_as(stats, "csv", header=False)
    _test_csv(csv, header=False)

    # dtypes.Stats - With header
    markdown = format.stats_as(stats, "markdown", header=True)
    _test_markdown(markdown, header=True)

    # dtypes.Stats - No header
    markdown = format.stats_as(stats, "markdown", header=False)
    _test_markdown(markdown, header=False)

    stats = dtypes.FunctionStats(stats, lambda x: x)

    # dtypes.FunctionStats - With header
    csv = format.stats_as(stats, "csv", header=True)
    _test_csv(csv, header=True)

    # dtypes.FunctionStats - No  header
    csv = format.stats_as(stats, "csv", header=False)
    _test_csv(csv, header=False)

    # dtypes.FunctionStats - With header
    markdown = format.stats_as(stats, "markdown", header=True)
    _test_markdown(markdown, header=True)

    # dtypes.FunctionStats - No header
    markdown = format.stats_as(stats, "markdown", header=False)
    _test_markdown(markdown, header=False)

    with pytest.raises(ValueError):
        format.stats_as(stats, "hello")

    try:
        import matplotlib

        # TODO Test markdown

        plot = format.stats_as(stats, "plot")
        assert isinstance(plot, matplotlib.figure.Figure)
    except ImportError:
        pass
