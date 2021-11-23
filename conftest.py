import contextlib
import multiprocessing
import pathlib
import shutil
import tempfile
import os
import sys
import queue

import pytest
from playwright.sync_api import sync_playwright

TEMPLATE_DIR = "templates"


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        "--template-dir",
        action="store",
        default=TEMPLATE_DIR,
    )


@contextlib.contextmanager
def playwright_common(request, web_server_main):
    server_hostname, server_port, server_log = web_server_main

    p = sync_playwright().start()
    if request.param == "chrome":
        browser = p.chromium.launch()
    else:
        assert False

    page = browser.new_page()
    page.goto(f"http://{server_hostname}:{server_port}")

    page.evaluate(
        """
            (async () => {
                let pyodide = await loadPyodide({ indexURL : 'https://cdn.jsdelivr.net/pyodide/v0.18.1/full/', fullStdLib: false, jsglobals : self });
                self.pyodide = pyodide;
                globalThis.pyodide = pyodide;
                pyodide._module.inTestHoist = true; // improve some error messages for tests
                pyodide.globals.get;
                pyodide.pyodide_py.eval_code;
                pyodide.pyodide_py.eval_code_async;
                pyodide.pyodide_py.register_js_module;
                pyodide.pyodide_py.unregister_js_module;
                pyodide.pyodide_py.find_imports;
                pyodide.runPython("");
            })()
        """
    )

    try:
        yield page
    finally:
        browser.close()
        p.stop()


@pytest.fixture(params=["chrome"], scope="function")
def playwright_standalone(request, web_server_main):
    with playwright_common(request, web_server_main) as playwright:
        yield playwright


@pytest.fixture(scope="session")
def web_server_main(request):
    """Web server that serves files in the templates directory"""
    with spawn_web_server(request.config.option.template_dir) as output:
        yield output


@contextlib.contextmanager
def spawn_web_server(template_dir=None):

    if template_dir is None:
        template_dir = TEMPLATE_DIR

    tmp_dir = tempfile.mkdtemp()
    log_path = pathlib.Path(tmp_dir) / "http-server.log"
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_web_server, args=(q, log_path, template_dir))

    try:
        p.start()
        port = q.get()
        hostname = "127.0.0.1"

        print(
            f"Spawning webserver at http://{hostname}:{port} "
            f"(see logs in {log_path})"
        )
        yield hostname, port, log_path
    finally:
        q.put("TERMINATE")
        p.join()
        shutil.rmtree(tmp_dir)


def run_web_server(q, log_filepath, template_dir):
    """Start the HTTP web server
    Parameters
    ----------
    q : Queue
      communication queue
    log_path : pathlib.Path
      path to the file where to store the logs
    """
    import http.server
    import socketserver

    os.chdir(template_dir)

    log_fh = log_filepath.open("w", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format_, *args):
            print(
                "[%s] source: %s:%s - %s"
                % (self.log_date_time_string(), *self.client_address, format_ % args)
            )

        def end_headers(self):
            # Enable Cross-Origin Resource Sharing (CORS)
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

    with socketserver.TCPServer(("", 0), Handler) as httpd:
        host, port = httpd.server_address
        print(f"Starting webserver at http://{host}:{port}")
        httpd.server_name = "test-server"
        httpd.server_port = port
        q.put(port)

        def service_actions():
            try:
                if q.get(False) == "TERMINATE":
                    print("Stopping server...")
                    sys.exit(0)
            except queue.Empty:
                pass

        httpd.service_actions = service_actions
        httpd.serve_forever()


if (
    __name__ == "__main__"
    and multiprocessing.current_process().name == "MainProcess"
    and not hasattr(sys, "_pytest_session")
):
    with spawn_web_server():
        # run forever
        while True:
            time.sleep(1)
