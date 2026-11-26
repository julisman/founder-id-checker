import http.client
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

from _load import ROOT

GUI = os.path.join(ROOT, "gui")


def _mod(name):
    sys.path.insert(0, GUI)
    try:
        spec = importlib.util.spec_from_file_location("checker_gui_" + name, os.path.join(GUI, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(GUI)


state = _mod("state")
serve = _mod("serve")
demo = _mod("demo")


class Demo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = tempfile.mkdtemp()
        assert demo.main([cls.project]) == 0
        cls.d = os.path.join(cls.project, "checker")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.project)

    def test_state_matches_the_health_tool(self):
        st = state.build(self.project)
        self.assertEqual(st["business"], "Bakso Mas Yono")
        self.assertEqual(st["verdict"], "Waspada")
        self.assertEqual(st["errors"], [])
        self.assertEqual(round(st["health"]["recent"]["kept"]), 4616067)
        self.assertEqual(len(st["health"]["months"]), 6)
        self.assertEqual(st["customers"]["rating_avg"], 4.18)
        self.assertEqual([m["vote"] for m in st["board"]], ["FIX", "FIX", "GROW", "FIX"])
        done = {s["step"]: s["done"] for s in st["steps"]}
        self.assertTrue(done["intake"] and done["customers"] and done["compliance"] and done["report"])
        self.assertFalse(done["channels"] or done["competitors"])
        json.dumps(st)  # plain JSON, nothing the page cannot read

    def test_project_or_checker_folder(self):
        self.assertEqual(state.checker_dir(self.project), self.d)
        self.assertEqual(state.checker_dir(self.d), self.d)

    def test_documents_only_from_the_list(self):
        self.assertIn("Bakso Mas Yono", state.read_doc(self.d, "report.md"))
        self.assertIn("Vote: FIX", state.read_doc(self.d, "board/money.md"))
        for bad in ("../../etc/passwd", "/etc/passwd", "actuals.json", "board/../business.md", "customers/reviews.csv", ""):
            self.assertIsNone(state.read_doc(self.d, bad), bad)

    def test_version_changes_when_a_file_changes(self):
        v = state.version(self.d)
        with open(os.path.join(self.d, "channels.md"), "w", encoding="utf-8") as fh:
            fh.write("# Channels\n")
        try:
            self.assertNotEqual(state.version(self.d), v)
        finally:
            os.remove(os.path.join(self.d, "channels.md"))

    def test_export_is_self_contained(self):
        page = serve.export_html(self.project)
        self.assertIn('<script id="state" type="application/json">', page)
        self.assertNotIn('src="app.js"', page)
        self.assertNotIn('href="style.css"', page)
        self.assertNotIn('content="SELF"', page)
        self.assertNotRegex(page, r'<(script|link)[^>]+(src|href)="https?://')  # nothing loaded from the internet
        data = re.search(r'<script id="state" type="application/json">(.*?)</script>', page, re.S).group(1)
        st = json.loads(data)
        self.assertTrue(st["exported"])
        self.assertIn("report.md", st["docs_text"])
        self.assertEqual(st["verdict"], "Waspada")

    def test_export_cannot_be_broken_by_a_document(self):
        path = os.path.join(self.d, "summary.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# Summary\n\n</script><script>alert(1)</script>\n")
        try:
            page = serve.export_html(self.project)
            self.assertNotIn("</script><script>alert(1)", page)
        finally:
            os.remove(path)


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = tempfile.mkdtemp()
        demo.main([cls.project])
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(cls.project))
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        shutil.rmtree(cls.project)

    def get(self, path, host=None, method="GET"):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.request(method, path, headers={"Host": host or "127.0.0.1:%d" % self.port})
        r = c.getresponse()
        body = r.read().decode("utf-8")
        c.close()
        return r, body

    def test_page_and_assets(self):
        r, body = self.get("/")
        self.assertEqual(r.status, 200)
        self.assertIn("<main id=\"app\"", body)
        self.assertNotIn('content="SELF"', body)
        self.assertIn("default-src 'self'", r.getheader("Content-Security-Policy"))
        self.assertEqual(r.getheader("X-Content-Type-Options"), "nosniff")
        for p in ("/app.js", "/style.css"):
            self.assertEqual(self.get(p)[0].status, 200, p)

    def test_api(self):
        r, body = self.get("/api/state")
        self.assertEqual(json.loads(body)["verdict"], "Waspada")
        r, body = self.get("/api/version")
        self.assertEqual(len(json.loads(body)["version"]), 16)
        r, body = self.get("/api/doc?name=report.md")
        self.assertIn("Business check-up", json.loads(body)["text"])

    def test_no_files_outside_the_list(self):
        for p in ("/api/doc?name=../../etc/passwd", "/api/doc?name=actuals.json", "/../serve.py", "/state.py", "/gui/serve.py"):
            self.assertEqual(self.get(p)[0].status, 404, p)

    def test_read_only_and_local_host_only(self):
        self.assertEqual(self.get("/api/state", method="POST")[0].status, 405)
        self.assertEqual(self.get("/api/state", host="evil.example:%d" % self.port)[0].status, 403)


class Languages(unittest.TestCase):
    def dictionaries(self):
        with open(os.path.join(GUI, "static", "app.js"), encoding="utf-8") as fh:
            js = fh.read()
        en = js[js.index("    en: {"):js.index("    id: {")]
        idn = js[js.index("    id: {"):js.index("  var lang =")]
        # a key starts a line or follows ", ", and its value is a string or a list
        keys = lambda block: set(re.findall(r'(?:^\s+|, )"?([a-zA-Z][\w-]*)"?: ["\[]', block, re.M))
        return keys(en), keys(idn), js

    def test_english_and_indonesian_have_the_same_words(self):
        en, idn, _ = self.dictionaries()
        self.assertGreater(len(en), 150)
        self.assertEqual(sorted(en - idn), [], "missing in Indonesian")
        self.assertEqual(sorted(idn - en), [], "missing in English")

    def test_every_key_the_page_uses_exists(self):
        en, _, js = self.dictionaries()
        used = set(k for k in re.findall(r'\bt\("([\w-]+)"', js) if not k.endswith("_"))  # "c_" + id is checked below
        with open(os.path.join(GUI, "static", "index.html"), encoding="utf-8") as fh:
            used |= set(re.findall(r'data-i18n="([\w-]+)"', fh.read()))
        self.assertEqual(sorted(used - en), [])
        # the keys built from data: every check id, status, step, verdict, lens and vote has its word
        for prefix, names in (("c_", ["margin", "breakeven", "trend", "direct_cost", "labour", "owner", "owner_pay", "debt", "cash",
                                      "platforms", "customers", "compliance"]),
                              ("status_", ["ok", "warn", "bad"]), ("s_", ["ok", "missing", "expired", "unknown"]),
                              ("v_", ["Sehat", "Waspada", "Kritis", "Incomplete"]), ("vote_", ["GROW", "FIX", "PIVOT", "CLOSE"]),
                              ("lens_", state.BOARD_LENSES), ("step_", [s for s, _, _ in state.STEPS]), ("theme_", ["auto", "light", "dark"])):
            for n in names:
                self.assertIn(prefix + n, en)

    def test_every_check_and_fix_speaks_indonesian(self):
        project = tempfile.mkdtemp()
        try:
            demo.main([project])
            h = state.build(project)["health"]
            for item in h["checks"] + h["fixes"]:
                self.assertTrue(item.get("text_id"), item["id"])
                self.assertNotEqual(item["text_id"], item["text"], item["id"])
            margin = next(c for c in h["checks"] if c["id"] == "margin")
            self.assertIn("23,6%", margin["text_id"])  # Indonesian decimal comma
            self.assertIn("23.6%", margin["text"])
        finally:
            shutil.rmtree(project)


class Static(unittest.TestCase):
    def test_page_script_never_writes_html_from_data(self):
        with open(os.path.join(GUI, "static", "app.js"), encoding="utf-8") as fh:
            js = fh.read()
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("outerHTML", js)
        self.assertNotIn("insertAdjacentHTML", js)
        self.assertNotIn("eval(", js)
        self.assertNotIn('setAttribute("style"', js)  # blocked by the page's policy; styles go through the DOM
        self.assertNotIn("</script", js)  # the export inlines this file inside a script tag

    def test_no_outside_resources(self):
        for name in ("index.html", "style.css", "app.js"):
            with open(os.path.join(GUI, "static", name), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotRegex(text, r"(src|href)=\"https?://", name)
            self.assertNotIn("@import", text, name)
            self.assertNotIn("fonts.googleapis", text, name)


if __name__ == "__main__":
    unittest.main()
