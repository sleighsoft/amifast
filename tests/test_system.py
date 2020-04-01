from benchit import system


def test_collect_system_statistics():
    statistics = system.collect_system_statistics()
    assert len(statistics) == 17
    assert isinstance(statistics, system.SystemStatistics)
    # Hardware
    assert hasattr(statistics, "cpu_count")
    assert isinstance(statistics.cpu_count, int)
    assert hasattr(statistics, "bits")
    assert hasattr(statistics, "machine_type")
    assert hasattr(statistics, "processor")
    assert hasattr(statistics, "processor_brand")
    assert hasattr(statistics, "processor_architecture")
    # OS
    assert hasattr(statistics, "platform_string")
    assert hasattr(statistics, "c_timer")
    assert hasattr(statistics, "c_timer_resolution")
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
