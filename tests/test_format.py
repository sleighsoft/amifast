import json
import os
import random
import tempfile

import pytest

from amifast import dtypes
from amifast import format


def _test_csv(csv, append):
    assert isinstance(csv, format.CSV)
    resource = csv.resource(append)
    lines = resource.split(os.linesep)[:-1]

    expected_length = len(format._STATS_MAPPING) + len(format._METDATA_MAPPING)
    if append:
        assert len(lines) == 1
        row = lines[0]
        columns = row.split(",")
        assert all([(h not in columns) for h in format._METDATA_MAPPING])
        assert all([(h not in columns) for h in format._STATS_MAPPING])
        assert len(columns) == expected_length
    else:
        assert len(lines) == 2
        header, row = lines

        header_columns = header.split(",")
        assert all([(h in header_columns) for h in format._METDATA_MAPPING])
        assert all([(h in header_columns) for h in format._STATS_MAPPING])
        assert len(header_columns) == expected_length

        row_columns = row.split(",")
        assert len(row_columns) == expected_length


def test_stats_as_csv():
    stats = dtypes.Stats([random.random() for _ in range(20)], lambda x: x, 0)
    csv = format.stats_as_csv(stats)

    _test_csv(csv, append=False)
    _test_csv(csv, append=True)

    with pytest.raises(TypeError) as exc:
        format.stats_as_csv([1.0])
    assert "stats has to be of type dtypes.Stats" in str(exc.value)


def _test_markdown(markdown, append):
    assert isinstance(markdown, format.Markdown)
    resource = markdown.resource(append)
    lines = resource.split(os.linesep)[:-1]

    expected_length = len(format._STATS_MAPPING) + len(format._METDATA_MAPPING)
    if append:
        assert len(lines) == 1
        row = lines[0]
        columns = row.split("|")
        assert all([(h not in columns) for h in format._METDATA_MAPPING])
        assert all([(h not in columns) for h in format._STATS_MAPPING])
        assert len(columns[1:-1]) == expected_length
    else:
        assert len(lines) == 3
        header, header_separator, row = lines
        header_columns = [h.strip() for h in header.split("|")][1:-1]
        assert len(header_columns) == expected_length
        assert all([(h in header_columns) for h in format._METDATA_MAPPING])
        assert all([(h in header_columns) for h in format._STATS_MAPPING])

        header_separator_columns = [h.strip() for h in header_separator.split("|")][
            1:-1
        ]
        assert len(header_separator_columns) == expected_length

        row_columns = [h.strip() for h in row.split("|")][1:-1]
        assert len(row_columns) == expected_length


def test_stats_as_markdown():
    stats = dtypes.Stats([random.random() for _ in range(20)], lambda x: x, 0)
    markdown = format.stats_as_markdown(stats)

    _test_markdown(markdown, append=False)
    _test_markdown(markdown, append=True)

    with pytest.raises(TypeError) as exc:
        format.stats_as_markdown([1.0])
    assert "stats has to be of type dtypes.Stats" in str(exc.value)


def _test_json(json_obj, append):
    assert isinstance(json_obj, format.JSON)
    resource = json_obj.resource(append)

    assert isinstance(resource, dict)

    run = resource
    if not append:
        assert "runs" in resource
        assert len(resource["runs"]) == 1
        run = resource["runs"][0]

    assert "metadata" in run
    assert "data" in run

    metadata = run["metadata"]
    for k in format._METDATA_MAPPING.keys():
        assert k in metadata

    data = run["data"]
    for k in format._STATS_MAPPING.keys():
        assert k in data


def test_stats_as_json():
    stats = dtypes.Stats([random.random() for _ in range(20)], lambda x: x, 0)
    json = format.stats_as_json(stats)

    _test_json(json, append=False)
    _test_json(json, append=True)

    with pytest.raises(TypeError) as exc:
        format.stats_as_json([1.0])
    assert "stats has to be of type dtypes.Stats" in str(exc.value)


def test_stats_as():
    stats = dtypes.Stats([random.random() for _ in range(20)], lambda x: x, 0)

    # CSV
    csv1 = format.stats_as(stats, "csv")
    _test_csv(csv1, append=True)

    csv2 = format.stats_as(stats, format.Format.CSV)
    assert csv1.resource() == csv2.resource()

    # Markdown
    markdown1 = format.stats_as(stats, "markdown")
    _test_markdown(markdown1, append=True)

    markdown2 = format.stats_as(stats, format.Format.MARKDOWN)
    assert markdown1.resource() == markdown2.resource()

    # JSON
    json1 = format.stats_as(stats, "json")
    _test_json(json1, append=True)

    json2 = format.stats_as(stats, format.Format.JSON)
    assert json1.resource() == json2.resource()

    with pytest.raises(ValueError) as exc:
        format.stats_as(stats, "hello")
    assert "Unsupported format" in str(exc.value)

    # PLot
    try:
        import matplotlib

        # TODO Test plot

        plot = format.stats_as(stats, "plot")
        assert isinstance(plot, format.Plot)
    except ImportError:
        pass


def test_Markdown():
    with pytest.raises(TypeError):
        format.Markdown(0)

    # dtypes.Stats
    md = format.Markdown(dtypes.Stats([0.0, 1.0, 2.0, 3.0], lambda x: x, 0))
    _test_markdown(md, append=True)
    _test_markdown(md, append=False)

    with tempfile.TemporaryDirectory() as dir:
        # append but file does not exist yet
        md_file = os.path.join(dir, "md_file")
        md.save(md_file)
        assert os.path.exists(md_file)
        with open(md_file, "r", newline="") as read_f:
            read_md = read_f.read()
            assert read_md == md.resource()

        # append but file exists
        md.save(md_file, append=True)
        with open(md_file, "r", newline="") as read_f:
            read_md = read_f.read()
            rows = read_md.split(os.linesep)
            assert len(rows) == 5
            assert rows[2] == rows[3]

        # append == False and already exists
        with pytest.raises(FileExistsError) as exc:
            md.save(md_file, append=False)
        assert "already exists but 'append'" in str(exc)


def test_CSV():
    with pytest.raises(TypeError):
        format.CSV(0)

    # dtypes.Stats
    csv = format.CSV(dtypes.Stats([0.0, 1.0, 2.0, 3.0], lambda x: x, 0))
    _test_csv(csv, append=True)
    _test_csv(csv, append=False)

    with tempfile.TemporaryDirectory() as dir:
        # append but file does not exist yet
        csv_file = os.path.join(dir, "csv_file")
        csv.save(csv_file)
        assert os.path.exists(csv_file)
        with open(csv_file, "r", newline="") as read_f:
            read_csv = read_f.read()
            assert read_csv == csv.resource()

        # append but file exists
        csv.save(csv_file, append=True)
        with open(csv_file, "r", newline="") as read_f:
            read_csv = read_f.read()
            rows = read_csv.split(os.linesep)
            assert len(rows) == 4
            assert rows[1] == rows[2]

        # append == False and already exists
        with pytest.raises(FileExistsError) as exc:
            csv.save(csv_file, append=False)
        assert "already exists but 'append'" in str(exc)


def test_JSON():
    with pytest.raises(TypeError):
        format.JSON(0)

    # dtypes.Stats
    json_stat = format.JSON(dtypes.Stats([0.0, 1.0, 2.0, 3.0], lambda x: x, 0))
    _test_json(json_stat, append=True)
    _test_json(json_stat, append=False)

    with tempfile.TemporaryDirectory() as dir:
        # append but file does not exist yet
        json_file = os.path.join(dir, "json_file")
        json_stat.save(json_file)
        assert os.path.exists(json_file)
        with open(json_file, "r", newline="") as read_f:
            read_json = read_f.read()
            assert read_json == json.dumps(json_stat.resource(append=False))

        # append but file exists
        json_stat.save(json_file, append=True)
        with open(json_file, "r", newline="") as read_f:
            read_json = json.load(read_f)
            assert len(read_json["runs"]) == 2

        # append == False and already exists
        with pytest.raises(FileExistsError) as exc:
            json_stat.save(json_file, append=False)
        assert "already exists but 'append'" in str(exc)


def test_plot():
    # TODO
    assert False


def test_format_enum():
    # TODO
    assert False
