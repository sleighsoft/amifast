import random

from benchit import format
from benchit import dtypes


def test_times_as():
    times = dtypes.Stats([random.random() for _ in range(20)])

    # TODO Test other dtypes

    csv = format.times_as(times, "csv")
    assert isinstance(csv, str)
    assert "| --- |" not in csv

    markdown = format.times_as(times, "markdown")
    assert isinstance(markdown, str)
    assert "| --- |" in markdown

    try:
        import matplotlib

        plot = format.times_as(times, "plot")
        assert isinstance(plot, matplotlib.figure.Figure)
    except ImportError:
        pass


def test_times_as_csv():
    times = dtypes.Stats([random.random() for _ in range(20)])

    # TODO Test other dtypes

    csv = format.times_as_csv(times)
    assert isinstance(csv, str)
    splits = csv.split("\n")
    assert "Time" in splits[0]
    assert len(splits) == 22

    csv = format.times_as_csv(times, header=False)
    assert isinstance(csv, str)
    splits = csv.split("\n")
    assert "Time" not in splits[0]
    assert len(splits) == 21


def test_times_as_markdown():
    times = dtypes.Stats([random.random() for _ in range(20)])

    # TODO Test other dtypes

    markdown = format.times_as_markdown(times)
    assert isinstance(markdown, str)
    splits = markdown.split("\n")
    assert "Time" in splits[0]
    assert "---" in splits[1]
    assert len(splits) == 23

    markdown = format.times_as_markdown(times, header=False)
    assert isinstance(markdown, str)
    splits = markdown.split("\n")
    assert "Time" not in splits[0]
    assert "---" not in splits[1]
    assert len(splits) == 21
