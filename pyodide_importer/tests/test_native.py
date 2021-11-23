import tempfile
import sys

import pytest

import pyodide_importer
from . import TEST_MODULE_URL


@pytest.fixture(scope="function")
def hook():
    tempdir = tempfile.TemporaryDirectory()
    pyfinder = pyodide_importer.register_hook(
        base_url=TEST_MODULE_URL,
        download_path=tempdir.name,
        update_syspath=True,
    )

    yield pyfinder

    pyodide_importer.unregister_hook()
    tempdir.cleanup()


@pytest.fixture(autouse=True)
def cleanup_imports():
    yield

    # Cleanup imported modules
    cleanup_targets = []
    for module in sys.modules:
        if module.startswith(("file_module", "regular_module")):
            cleanup_targets.append(module)

    for module in cleanup_targets:
        sys.modules.pop(module)


def test_file_module(hook):
    expected_response = "hello from file_module"

    import file_module

    assert file_module.hello() == expected_response


def test_regular_module_init(hook):
    expected_response = "hello from regular_module"

    import regular_module

    assert regular_module.hello() == expected_response


def test_regular_module_submodule(hook):
    expected_response = "hello from regular_module.submodule"

    import regular_module.submodule

    assert regular_module.submodule.hello() == expected_response


def test_regular_module_submodule2(hook):
    expected_response = "hello from regular_module.submodule2"

    import regular_module

    assert regular_module.submodule2_hello() == expected_response


def test_module_whitelist(hook):
    pyodide_importer.add_module("file_module")

    import file_module

    with pytest.raises(ModuleNotFoundError):
        import regular_module


def test_nohook():
    with pytest.raises(ModuleNotFoundError):
        import file_module


def test_unregister_hook(hook):
    pyodide_importer.unregister_hook()
    with pytest.raises(ModuleNotFoundError):
        import file_module


def test_available_modules(hook):
    hook.add_module(["module1", "module2"])

    modules = hook.available_modules()
    assert "module1" in modules
    assert "notamodule" not in modules


def test_contextmanager(hook):
    with hook:
        import file_module

    with pytest.raises(ModuleNotFoundError):
        import regular_module
