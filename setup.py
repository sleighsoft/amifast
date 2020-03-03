VERSION = "0.1"


def main():
    from setuptools import setup, find_packages

    with open("README.md") as fp:
        long_description = fp.read().strip()

    setup(
        name="benchit",
        version=VERSION,
        description="A Python benchmarking package for simple benchmarks and performance regression testing.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/sleighsoft/benchit",
        author="Julian Niedermeier",
        author_email="jpniedermeier@gmail.com",
        extras_require={"test": ["pytest", "coverage"]},
        packages=find_packages(),
        zip_safe=True,
        install_requires=["py-cpuinfo"],
        # TODO https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
        # 'entry_points': {
        #     'console_scripts': ['benchit=benchit.__main__:main']
        # }
        # Optional dependencies
        # 'matplotlib'
        # TODO python_requires
        # TODO classifiers=[]
    )


if __name__ == "__main__":
    main()


# TODO Test and implement proper setup. Should also create a console ready application
# such as `bench <file>`
