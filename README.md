# pyodide-importer

[![build](https://github.com/ryanking13/pyodide-importer/actions/workflows/test_core.yml/badge.svg)](https://github.com/ryanking13/pyodide-importer/actions/workflows/test_core.yml)
[![Documentation Status](https://readthedocs.org/projects/pyodide-importer/badge/?version=latest)](https://pyodide-importer.readthedocs.io/en/latest/?badge=latest)

`pyodide-importer` is a plugin for the [Pyodide](https://pyodide.org) which adds
functionalities to import external Python packages through HTTP(s).

## Quickstart

Loading Python package through HTTP(s):

```python
>>> import micropip
>>> await micropip.install("pyodide-importer")

>>> from pyodide_importer import register_hook
>>> url = "https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/"
>>> register_hook(url)
>>> # now you can import python packages from `url`

>>> # https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/file_module.py
>>> import file_module
>>> file_module.hello()

>>> # https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/regular_module/__init__.py
>>> import regular_module
>>> regular_module.hello()
```