import system

from benchit import dtypes


def test_collect_system_statistics():
    statistics = system.collect_system_statistics()
    assert len(statistics) == 14
    assert isinstance(statistics, dtypes.SystemStatistics)
    # Hardware
    assert hasattr(statistics, "bits")
    assert hasattr(statistics, "machine_type")
    assert hasattr(statistics, "processor")
    assert hasattr(statistics, "processor_brand")
    assert hasattr(statistics, "processor_architecture")
    # OS
    assert hasattr(statistics, "platform_string")
    # Python
    assert hasattr(statistics, "python_implementation")
    assert hasattr(statistics, "python_version")
    assert hasattr(statistics, "python_compiler")
    assert hasattr(statistics, "python_build_no")
    assert hasattr(statistics, "python_build_date")
    assert hasattr(statistics, "python_branch")
    assert hasattr(statistics, "python_revision")
    # Packages
    assert hasattr(statistics, "python_installed_packages")
    assert isinstance(statistics.python_installed_packages, dict)
