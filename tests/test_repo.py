import json
import os
import re
import unittest

from _load import ROOT, SKILLS_DIR

SKILLS = ["checker-intake", "checker-health", "checker-channels", "checker-customers", "checker-competitors",
          "checker-compliance", "checker-board", "checker-report", "checker-simulate"]
REFERENCE = ["tax.md", "permits.md", "payroll.md", "payments-channels.md", "calendar.md", "sources.md"]
EM = chr(0x2014)  # built in code so this file does not trip its own check


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


def text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".py", ".json", ".csv", ".txt", ".js", ".css", ".html")) or f in ("LICENSE", ".gitignore"):
                yield os.path.join(base, f)


class Repo(unittest.TestCase):
    def test_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 300, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)

    def test_paths_and_skills_named_exist(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
            for tool in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w.\-/]+\.(?:py|md|json|csv))", text):
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(SKILLS_DIR, s, tool))), "%s: %s" % (s, tool))
            for other in re.findall(r"`/(checker-[\w-]+)", text):
                self.assertIn(other, SKILLS, "%s mentions /%s, which does not exist" % (s, other))
            self.assertNotIn("founder/", text, "%s points at founder-id's folder" % s)

    def test_reference_files(self):
        _, text = frontmatter(os.path.join(SKILLS_DIR, "checker-compliance", "SKILL.md"))
        for f in REFERENCE:
            self.assertTrue(os.path.isfile(os.path.join(SKILLS_DIR, "checker-compliance", "reference", f)), f)
            self.assertIn("reference/%s" % f, text)

    def test_stands_alone(self):
        """A separate product: nothing reads founder-id's skills or folders."""
        for path in text_files():
            if os.path.basename(path) == "test_repo.py":
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotRegex(text, r"/founder-(?!id-checker)[a-z]", os.path.relpath(path, ROOT))
            self.assertNotIn("founder/", text, os.path.relpath(path, ROOT))

    def test_commands(self):
        for name in ("checker-gui", "checker-gui-stop"):
            fm, text = frontmatter(os.path.join(ROOT, "commands", name + ".md"))
            self.assertRegex(fm, r"description: ", name)
            self.assertIn("${CLAUDE_PLUGIN_ROOT}/gui/serve.py", text, name)

    def test_manifests(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "founder-id-checker")
        self.assertEqual(plugin["license"], "MIT")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["plugins"][0]["name"], "founder-id-checker")
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_readme_lists_every_skill(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# founder-id-checker"))
        self.assertIn("/plugin install founder-id-checker@founder-id-checker", readme)
        self.assertIn("## Fine print", readme)
        for s in SKILLS:
            self.assertIn("/%s`" % s, readme)

    def test_examples_have_no_dollars_and_parse(self):
        with open(os.path.join(SKILLS_DIR, "checker-health", "example.json"), encoding="utf-8") as fh:
            raw = fh.read()
        json.loads(raw)
        self.assertNotIn("$", raw)

    def test_no_em_dashes(self):
        for path in text_files():
            with open(path, encoding="utf-8") as fh:
                self.assertNotIn(EM, fh.read(), os.path.relpath(path, ROOT))


if __name__ == "__main__":
    unittest.main()
