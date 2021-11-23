import tempfile
import sys

import pytest

import pyodide_importer
from . import TEST_MODULE_URL


def _async(code):
    return (
        """(async() => {
        %s
    })()"""
        % code
    )


def test_check_pyodide(playwright_standalone):

    playwright_standalone.evaluate(
        """
        pyodide.runPython(`
            print(1)
        `)
        """
    )


def test_file_module(playwright_standalone):
    expected_response = "hello from file_module"
    playwright_standalone.evaluate(
        _async(
            """
        await pyodide.loadPackage("micropip")
        pyodide.runPythonAsync(`
            import micropip
            await micropip.install("pyodide-importer")
            import pyodide_importer
            pyodide_importer.register_hook("%s")
            import file_module
            assert file_module.hello() == "%s"
        `)
        """
            % (TEST_MODULE_URL, expected_response)
        )
    )


def test_regular_module(playwright_standalone):
    expected_response = "hello from regular_module"
    playwright_standalone.evaluate(
        _async(
            """
        await pyodide.loadPackage("micropip")
        pyodide.runPythonAsync(`
            import micropip
            await micropip.install("pyodide-importer")
            import pyodide_importer
            pyodide_importer.register_hook("%s")
            import regular_module
            assert regular_module.hello() == "%s"
        `)
        """
            % (TEST_MODULE_URL, expected_response)
        )
    )
