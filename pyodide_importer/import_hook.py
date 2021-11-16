from importlib.abc import MetaPathFinder
from _frozen_importlib_external import PathFinder
import sys
import pathlib
import warnings
from typing import List, Any, Union, Iterable

PYODIDE = True

try:
    from js import XMLHttpRequest
except:
    warnings.warn("Pyodide not found, running in native mode")
    import requests

    PYODIDE = False


class PyFinder(MetaPathFinder):
    """Meta path finder for Pyodide which supports importing external Python files"""

    def __init__(
        self,
        import_path: Union[str, List[str]] = "",
        download_path: str = "",
        modules: Iterable[str] = None,
    ):
        self.import_path = self._prepare_import_path(import_path)
        self.download_path = self._to_abspath(download_path)
        self.modules = set(modules) if modules is not None else None

    def register(self):
        if not self._registered():
            sys.meta_path.append(self)

    def unregister(self):
        if self._registered():
            sys.meta_path.remove(self)

    def _registered(self):
        return self in sys.meta_path

    def __enter__(self):
        self.register()

    def __exit__(self, type, value, traceback):
        self.unregister()

    def _prepare_import_path(self, paths: Union[str, List[str]]):
        if isinstance(paths, str):
            return [paths.rstrip("/") + "/"]
        elif isinstance(paths, list):
            return [path.rstrip("/") + "/" for path in paths]

    def _to_abspath(self, path: str):
        return pathlib.Path(path).resolve()

    def add_module(self, module: Union[str, List[str]]):
        if self.modules is None:
            self.modules = set()

        if isinstance(module, str):
            self.modules.add(module)
        else:
            self.modules.update(module)

    def available_modules(self):
        return self.modules

    @staticmethod
    def invalidate_caches():
        """Call the invalidate_caches() method on all path entry finders
        stored in sys.path_importer_caches (where implemented)."""
        for name, finder in list(sys.path_importer_cache.items()):
            if finder is None:
                del sys.path_importer_cache[name]
            elif hasattr(finder, "invalidate_caches"):
                finder.invalidate_caches()

    def find_spec(self, fullname: str, path: List[str], target: Any = None):
        # Should find python packages according to PEP-420.
        raise NotImplementedError


class PyHTTPFinder(PyFinder):
    """Meta path finder for importing python files through HTTP(s)"""

    def __init__(
        self,
        import_path: Union[str, List[str]] = "",
        download_path: str = "",
        modules: Iterable[str] = None,
    ):
        super().__init__(import_path, download_path, modules)

    def _get(self, url: str):
        if PYODIDE:
            req = XMLHttpRequest.new()
            req.open("GET", url, False)
            req.send(None)
            return (req.status, req.responseText)
        else:
            # This enables testing this module outside of Pyodide
            resp = requests.get(url)
            return (resp.status_code, resp.text)

    def find_spec(self, fullname: str, path: List[str], target: Any = None):
        # Search order:
        # 1. <directory>/foo/__init__.py
        # 2. <directory>/foo.py
        # (-) Not supported: binary formats (pyc, pyd, so)
        # (-) Not supported: Namespace packages without __init__.py

        # module1.module2 ==> module1/module2
        modules = fullname.split(".")
        if self.modules is not None and modules[0] not in self.modules:
            return None

        fullname_aspath = fullname.replace(".", "/")

        import_subpaths = [
            f"{fullname_aspath}/__init__.py",  # Regular package
            f"{fullname_aspath}.py",  # Module package
        ]

        for base_path in self.import_path:
            for import_subpath in import_subpaths:
                status_code, content = self._get(f"{base_path}{import_subpath}")
                if status_code != 200:
                    continue

                package_path = self.download_path / import_subpath
                package_path.parent.mkdir(parents=True, exist_ok=True)
                with package_path.open("w") as f:
                    f.write(content)

                # We need to invalidate caches since PathFinder have already failed once and it is cached.
                self.invalidate_caches()
                return PathFinder.find_spec(fullname, path, target)

        return None
