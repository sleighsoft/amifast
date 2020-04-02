# Building and Uploading a New Version

All commands are executed from the project root.

```bash
python setup.py clean --all
git tag <version_number>
python setup.py sdist bdist_wheel
twine upload dist/*
```
