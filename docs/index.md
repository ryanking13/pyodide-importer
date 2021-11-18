# pyodide-importer documentation

## Overview

[![build](https://github.com/ryanking13/pyodide-importer/actions/workflows/test_core.yml/badge.svg)](https://github.com/ryanking13/pyodide-importer/actions/workflows/test_core.yml)

`pyodide-importer` is a plugin for the [Pyodide](https://pyodide.org) which adds
functionalities to import external Python packages through HTTP(s).


```{note}
`pyodide-impoter` is designed to be used inside Pyodide environment.
If you want to "import file thorugh HTTP" in native Python environment, try [httpimport](https://github.com/operatorequals/httpimport) instead.
```

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

## Index

```{eval-rst}
.. toctree::
   :maxdepth: 1

   api
   changelog
```