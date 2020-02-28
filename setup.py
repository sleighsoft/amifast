from setuptools import setup


INSTALL_REQUIRES = [
    "py-cpuinfo"
]


def main():
    setup(
        use_scm_version={"write_to": "src/_pytest/_version.py"},
        setup_requires=["setuptools-scm", "setuptools>=40.0"],
        package_dir={"": "benchit"},
        extras_require={
            "testing": [
                "pytest",
                "coverage",
            ],
        },
        install_requires=INSTALL_REQUIRES,
    )


if __name__ == "__main__":
    main()