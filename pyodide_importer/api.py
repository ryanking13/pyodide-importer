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
    base_url: Union[str, List[str]],
    download_path: str = "",
    modules: List[str] = None,
    update_syspath: bool = True,
):
    """
    Register import hook to sys.meta_path.

    Args:
        base_url (str or List[str]): URL(s) where the directory containing Python packages is served through HTTP/S
        download_path (str): the path in virtual file system where Python packages will be downloaded, default is current working directory
        modules (List[str]): a list, with the names of the root modules/packages that can be imported from the given URL
        update_syspath (bool): whether to add ``download_path`` to `sys.path`

    **Notes on** ``module`` **parameter**:
    If this parameter is not specified, import statement will try to search a module everytime
    when the module is not found in local filesystem. This means every FAILED import statement will result in multiple 404 HTTP errors.
    So when you have fixed modules, using modules parameter to whitelist downloadable modules in recommended.
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
    Unregister import hook from sys.meta_path.

    After calling this method, new external modules cannot be downloaded and imported,
    while previously imported modules can be keep available.
    """
    global pyfinder

    if pyfinder is not None:
        pyfinder.unregister()
        pyfinder = None


def add_module(module: Union[str, List[str]]):
    """
    Add new module(s) that can be imported from URL.

    Args:
        module (str or List[str]): modules/packages that can be imported from the URL
    """
    global pyfinder

    if pyfinder is None or (not pyfinder._registered()):
        raise RuntimeError("import hook is not registered")

    pyfinder.add_module(module)


def available_modules():
    """
    Get the list of modules that can be imported from the URL.
    """
    global pyfinder
    if pyfinder is None or (not pyfinder._registered()):
        raise RuntimeError("import hook is not registered")

    return pyfinder.available_modules()
