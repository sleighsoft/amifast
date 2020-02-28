import system
import dtypes


def test_collect_system_statistics():
    statistics = system.collect_system_statistics()
    assert len(statistics) == 9
    assert isinstance(statistics, dtypes.SystemStatistics)
    assert hasattr(statistics, "bits")
    assert hasattr(statistics, "machine_type")
    assert hasattr(statistics, "platform_string")
    assert hasattr(statistics, "processor")
    assert hasattr(statistics, "processor_brand")
    assert hasattr(statistics, "processor_architecture")
    assert hasattr(statistics, "python_impl")
    assert hasattr(statistics, "python_version")
    assert hasattr(statistics, "python_packages")
    assert isinstance(statistics.python_packages, dict)
