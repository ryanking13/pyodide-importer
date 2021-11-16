# pyodide-importer

[Pyodide](https://pyodide.org) + external file import support

## Installation

Inside Pyodide:

```py
import micropip
await micropip.install("pyodide-importer")
```

## Basic Usage

```py
from pyodide_importer import register_hook
register_hook("<Base URL where python scripts are in>")
import external_module
```

__Example__

```py
import micropip
await micropip.install("pyodide-importer")
from pyodide_importer import register_hook
register_hook("https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/")

# https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/file_module.py
import file_module
file_module.hello()

# https://raw.githubusercontent.com/ryanking13/pyodide-importer/main/test_modules/regular_module/__init__.py
import regular_module
regular_module.hello()
```

## Advanced Usage

__Whitelisting modules to import__

Whitelisting modules will prevent from generating redundant HTTP requests when looking for not existing modules.

```py
register_hook(
    "<Base URL where python scripts are in>",
    modules=["module1", "module2"]
)
```

__Changing path where modules will be downloaded__

`download_path` option changes the path where modules will be downloaded inside the virtual file system,
default is set to the current working directory.

```py
register_hook(
    "<Base URL where python scripts are in>",
    download_path="/path/to/be/downloaded",
)
```