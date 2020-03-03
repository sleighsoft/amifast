import platform
import pkg_resources
from cpuinfo import get_cpu_info

from benchit import dtypes


def collect_system_statistics() -> dtypes.SystemStatistics:
    # TODO Add documentation
    # Hardware
    bits, _ = platform.architecture()
    machine_type = platform.machine()
    processor = platform.processor()
    cpu_info = get_cpu_info()
    processor_brand = cpu_info["brand"]
    processor_architecture = cpu_info["arch"]
    # OS
    platform_string = platform.platform()
    # Python
    python_build_no, python_build_date = platform.python_build()
    python_implementation = platform.python_implementation()
    python_version = platform.python_version()
    python_compiler = platform.python_compiler()
    python_branch = platform.python_branch()
    python_revision = platform.python_revision()
    # Packages
    python_installed_packages = {
        d.project_name: d.version for d in pkg_resources.working_set
    }

    statistics = dtypes.SystemStatistics(
        bits=bits,
        machine_type=machine_type,
        processor=processor,
        processor_brand=processor_brand,
        processor_architecture=processor_architecture,
        platform_string=platform_string,
        python_implementation=python_implementation,
        python_version=python_version,
        python_compiler=python_compiler,
        python_build_no=python_build_no,
        python_build_date=python_build_date,
        python_branch=python_branch,
        python_revision=python_revision,
        python_installed_packages=python_installed_packages,
    )
    return statistics
