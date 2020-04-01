import os
import platform
import time
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Union

import cpuinfo
import pkg_resources


class SystemStatistics(NamedTuple):
    """Container class for various system statistics: Hardware, OS, Python,
    Installed Packages.

    Included statistics are:

    - Hardware
        - cpu_count: int
        - bits: str
        - machine_type: str
        - processor: str
        - processor_brand: str
        - processor_architecture: str
    - OS
        - platform_string: str
        - c_timer: str
        - c_timer_resolution: float
    - Python
        - python_implementation: str
        - python_version: str
        - python_compiler: str
        - python_build_no: str
        - python_build_date: str
        - python_branch: str
        - python_revision: str
    - Packages
        - python_installed_packages: Dict[name, version]

    """

    # Hardware
    cpu_count: int
    bits: str
    machine_type: str
    processor: str
    processor_brand: str
    processor_architecture: str
    # OS
    platform_string: str
    c_timer: str
    c_timer_resolution: float
    # Python
    python_implementation: str
    python_version: str
    python_compiler: str
    python_build_no: str
    python_build_date: str
    python_branch: str
    python_revision: str
    # Packages
    python_installed_packages: Dict[str, str]


def collect_system_statistics() -> SystemStatistics:
    """Collects general system statistics about Hardware, OS, Python, and
    installed packages.

    Note: Some entries might be empty if the information is not available.

    Returns:
        SystemStatistics: A SystemStatistics object.
    """
    operating_system = platform.uname().system
    if operating_system == "Linux":
        return Linux.statistics()
    elif operating_system == "Windows":
        return Windows.statistics()
    elif operating_system == "MacOs":
        return MacOS.statistics()
    else:
        return System.statistics()


class System(object):
    """Operating system independent system statistics."""

    @staticmethod
    def hardware_cpu_count() -> Optional[int]:
        if hasattr(os, "cpu_count"):
            # Python 3.4+
            cpu_count = os.cpu_count()
        else:
            cpu_count = None
            try:
                import multiprocessing
            except ImportError:
                pass
            else:
                try:
                    cpu_count = multiprocessing.cpu_count()
                except NotImplementedError:
                    pass

        if cpu_count is not None and cpu_count < 1:
            return None

        return cpu_count

    @staticmethod
    def hardware_bits() -> str:
        return platform.architecture()[0]

    @staticmethod
    def hardware_machine_type() -> str:
        return platform.machine()

    @staticmethod
    def hardware_processor() -> str:
        return platform.processor()

    @staticmethod
    def hardware_processor_brand() -> str:
        return cpuinfo.get_cpu_info()["brand"]

    @staticmethod
    def hardware_processor_architecture() -> str:
        return cpuinfo.get_cpu_info()["arch"]

    @staticmethod
    def os_platform() -> str:
        return platform.platform()

    @staticmethod
    def os_c_timer() -> str:
        return time.get_clock_info("perf_counter").implementation

    @staticmethod
    def os_c_timer_resolution() -> float:
        return time.get_clock_info("perf_counter").resolution

    @staticmethod
    def python_build_no() -> str:
        return platform.python_build()[0]

    @staticmethod
    def python_build_date() -> str:
        return platform.python_build()[1]

    @staticmethod
    def python_implementation() -> str:
        return platform.python_implementation()

    @staticmethod
    def python_version() -> str:
        return platform.python_version()

    @staticmethod
    def python_compiler() -> str:
        return platform.python_compiler()

    @staticmethod
    def python_branch() -> str:
        return platform.python_branch()

    @staticmethod
    def python_revision() -> str:
        return platform.python_revision()

    @staticmethod
    def python_installed_packages() -> Dict[str, str]:
        return {d.project_name: d.version for d in pkg_resources.working_set}

    @classmethod
    def statistics(cls) -> SystemStatistics:
        """Collects system statistics about Hardware, OS, Python, and
        installed packages.

        Note: Some entries might be empty if the information is not available.

        Returns:
            SystemStatistics: A SystemStatistics object.
        """
        return SystemStatistics(
            cpu_count=cls.hardware_cpu_count(),
            bits=cls.hardware_bits(),
            machine_type=cls.hardware_machine_type(),
            processor=cls.hardware_processor(),
            processor_brand=cls.hardware_processor_brand(),
            processor_architecture=cls.hardware_processor_architecture(),
            platform_string=cls.os_platform(),
            c_timer=cls.os_c_timer(),
            c_timer_resolution=cls.os_c_timer_resolution(),
            python_implementation=cls.python_implementation(),
            python_version=cls.python_version(),
            python_compiler=cls.python_compiler(),
            python_build_no=cls.python_build_no(),
            python_build_date=cls.python_build_date(),
            python_branch=cls.python_branch(),
            python_revision=cls.python_revision(),
            python_installed_packages=cls.python_installed_packages(),
        )


class Windows(System):
    """Windows system statistics."""


class Linux(System):
    """Linux system statistics."""


class MacOS(System):
    """MacOS system statistics."""


if __name__ == "__main__":
    statistics = collect_system_statistics()
    from pprint import pprint

    pprint(statistics._asdict())


# TODO add used/available memory
