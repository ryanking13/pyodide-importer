from contextlib import contextmanager
import pathlib
import sys
from typing import Union, List
from .import_hook import PyFinder, PyHTTPFinder

# Singleton instance of PyFinder
pyfinder: PyFinder = None


def _update_syspath(path: str):
    """
    Append `path` to sys.path so that files in path can be imported
    """
    path = pathlib.Path(path).resolve().as_posix()
    if path not in sys.path:
        sys.path.append(path)


def register_hook(
    base_url: str,
    download_path: str = "",
    modules: List[str] = None,
    update_syspath: bool = True,
):
    """
    Register PyFinder import hook to sys.meta_path
    """
    global pyfinder
    if pyfinder is not None and pyfinder._registered():
        raise RuntimeError(
            "import hook is already registered, if you want to register a new hook, unregister the existing hook with unregister_hook() first"
        )

    pyfinder = PyHTTPFinder(base_url, download_path, modules)
    pyfinder.register()
    if update_syspath:
        _update_syspath(download_path)

    return pyfinder


def unregister_hook():
    """
    Unregister PyFinder import hook from sys.meta_path
    """
    global pyfinder

    if pyfinder is not None:
        pyfinder.unregister()
        pyfinder = None


def add_module(module: Union[str, List[str]]):
    """
    Add new module(s) to the whitelist which PyFinder import hook can import
    """
    global pyfinder

    if pyfinder is None or (not pyfinder._registered()):
        raise RuntimeError("import hook is not registered")

    pyfinder.add_module(module)


def available_modules():
    """
    Get the list of whitelisted modules which PyFinder import hook can import
    """
    global pyfinder
    if pyfinder is None or (not pyfinder._registered()):
        raise RuntimeError("import hook is not registered")

    return pyfinder.available_modules()
