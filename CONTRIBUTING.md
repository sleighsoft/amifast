# Setup

1. Clone this repository `git clone git@github.com:sleighsoft/amifast.git`
2. Install dev environment using conda: `conda env create -f environment.yml`
3. Install pre-commit hooks: `pre-commit install`
4. Optional. Install the package for `examples/` to work: `pip install -e .`

```bash
git clone git@github.com:sleighsoft/amifast.git
conda env create -f environment.yml
pre-commit install
pip install -e .
```

# Running tests

Tests can be run with `pytest`.

```bash
pytest ./tests/
```

# Running coverage

Coverage can be determined using `coverage`.

```bash
coverage run -m pytest ./tests/
coverage html
```

Results will be written to `htmlcov/index.html`.


# Development using VSCode

The project root can be imported into VSCode without any addtional setup required.

Useful plugins for development are:
- Python (Microsoft)
- Visual Studio IntelliCode (Microsoft)
- autoDocstring (Nils Werner)
- Test Explorer UI (Holger Benl)
- Python Test Explorer for Visual Studio Code (Little Fox Team)
