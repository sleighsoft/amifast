import platform
import pkg_resources
from cpuinfo import get_cpu_info

from dtypes import SystemStatistics

def collect_system_statistics():
    bits, _ = platform.architecture()
    machine_type = platform.machine()
    platform_string = platform.platform()
    processor = platform.processor()
    python_impl = platform.python_implementation()
    python_version = platform.python_version()
    python_packages = {d.project_name: d.version for d in pkg_resources.working_set}

    cpu_info = get_cpu_info()
    processor_brand = cpu_info["brand"]
    processor_architecture = cpu_info["arch"]

    statistics = SystemStatistics(
        bits=bits,
        machine_type=machine_type,
        platform_string=platform_string,
        processor=processor,
        processor_brand=processor_brand,
        processor_architecture=processor_architecture,
        python_impl=python_impl,
        python_version=python_version,
        python_packages=python_packages,
    )
    return statistics
