#!/usr/bin/env python3
"""The founder-id-checker dashboard: a live, read-only web page of a project's checker/ folder.

Standard library only. Listens on 127.0.0.1 only, never writes the skills' files,
never touches the network, never starts a Claude session. The page refreshes by
itself while the skills write to checker/.

    python3 gui/serve.py --dir path/to/project                  # serve on http://127.0.0.1:8765
    python3 gui/serve.py --dir path/to/project --port 9000 --open
    python3 gui/serve.py --dir path/to/project --export check-up.html   # one offline HTML file to send
    python3 gui/serve.py --dir path/to/project --stop           # stop the server started for this project
"""

import argparse
import json
import os
import signal
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import state as S  # noqa: E402

STATIC = os.path.join(HERE, "static")
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}
HEADERS = {"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
           "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;"
                                      " connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"}


CSP_PLACEHOLDER = '<meta http-equiv="Content-Security-Policy" content="SELF">'


def _asset(name):
    with open(os.path.join(STATIC, name), encoding="utf-8") as fh:
        return fh.read()


def page_for_server():
    """The page as the server sends it: the policy travels in the response header instead."""
    return _asset("index.html").replace(CSP_PLACEHOLDER + "\n", "").replace(CSP_PLACEHOLDER, "")


def make_handler(project):
    class Handler(BaseHTTPRequestHandler):
        server_version = "checker-gui"

        def log_message(self, fmt, *args):  # quiet: the terminal belongs to the owner
            pass

        def _send(self, code, body, ctype):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            for k, v in HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

        def do_GET(self):
            host = (self.headers.get("Host") or "").split(":")[0]
            if host not in ("127.0.0.1", "localhost"):  # no DNS rebinding: only our own address
                return self._send(403, "forbidden", "text/plain; charset=utf-8")
            url = urlparse(self.path)
            if url.path in ASSETS:
                name, ctype = ASSETS[url.path]
                return self._send(200, page_for_server() if name == "index.html" else _asset(name), ctype)
            if url.path == "/api/version":
                return self._json({"version": S.version(S.checker_dir(project))})
            if url.path == "/api/state":
                return self._json(S.build(project))
            if url.path == "/api/doc":
                name = (parse_qs(url.query).get("name") or [""])[0]
                text = S.read_doc(S.checker_dir(project), name)
                if text is None:
                    return self._json({"error": "no such document"}, 404)
                return self._json({"name": name, "text": text})
            return self._send(404, "not found", "text/plain; charset=utf-8")

        def do_POST(self):
            self._send(405, "read-only", "text/plain; charset=utf-8")

        do_PUT = do_DELETE = do_PATCH = do_POST

    return Handler


def export_html(project):
    """One self-contained HTML file: the page, its styles, its script and a frozen copy of the data."""
    st = S.build(project)
    st["docs_text"] = S.all_docs(S.checker_dir(project))
    st["exported"] = True
    data = json.dumps(st, ensure_ascii=False).replace("<", "\\u003c")  # cannot close the script tag
    page = _asset("index.html")
    page = page.replace('<link rel="stylesheet" href="style.css">', "<style>\n%s\n</style>" % _asset("style.css"))
    page = page.replace('<script src="app.js"></script>',
                        '<script id="state" type="application/json">%s</script>\n<script>\n%s\n</script>' % (data, _asset("app.js")))
    page = page.replace(CSP_PLACEHOLDER,
                        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\';'
                        ' script-src \'unsafe-inline\'; img-src data:;">')
    return page


def pid_file(project):
    return os.path.join(S.checker_dir(project), ".gui", "server.json")


def stop(project):
    p = pid_file(project)
    try:
        with open(p, encoding="utf-8") as fh:
            info = json.load(fh)
    except (FileNotFoundError, ValueError):
        print("No dashboard is running for %s." % project)
        return 0
    try:
        os.kill(int(info["pid"]), signal.SIGTERM)
        print("Stopped the dashboard on http://127.0.0.1:%s" % info.get("port"))
    except (ProcessLookupError, PermissionError, KeyError, ValueError):
        print("The dashboard was not running any more.")
    try:
        os.remove(p)
    except OSError:
        pass
    return 0


def _on_term(*_):
    raise KeyboardInterrupt


def serve(project, port, open_browser=False):
    httpd = None
    for p in range(port, port + 20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), make_handler(project))
            break
        except OSError:
            continue
    if httpd is None:
        print("error: no free port from %d to %d" % (port, port + 19), file=sys.stderr)
        return 2
    real = httpd.server_address[1]
    url = "http://127.0.0.1:%d" % real
    d = S.checker_dir(project)
    if os.path.isdir(d):
        os.makedirs(os.path.dirname(pid_file(project)), exist_ok=True)
        with open(pid_file(project), "w", encoding="utf-8") as fh:
            json.dump({"pid": os.getpid(), "port": real, "url": url}, fh)
    print("Dashboard for %s on %s (read-only; Ctrl+C or --stop to end it)" % (d, url), flush=True)
    if open_browser:
        webbrowser.open(url)
    signal.signal(signal.SIGTERM, _on_term)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        try:
            with open(pid_file(project), encoding="utf-8") as fh:
                if json.load(fh).get("pid") == os.getpid():
                    os.remove(pid_file(project))
        except (OSError, ValueError):
            pass
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=".", help="the project folder (the one that holds checker/), or checker/ itself")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open the page in the browser")
    ap.add_argument("--export", metavar="FILE", help="write one offline HTML file and exit")
    ap.add_argument("--stop", action="store_true", help="stop the dashboard started for this project")
    a = ap.parse_args(argv)
    if a.stop:
        return stop(a.dir)
    if a.export:
        with open(a.export, "w", encoding="utf-8") as fh:
            fh.write(export_html(a.dir))
        print("Wrote %s (open it in any browser; it needs no server and no internet)" % a.export)
        return 0
    return serve(a.dir, a.port, a.open)


if __name__ == "__main__":
    sys.exit(main())
