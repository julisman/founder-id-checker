"""What the dashboard shows, read from a project's checker/ folder. Standard library only.

Read-only: nothing here writes inside checker/ except the server's own pid file
(checker/.gui/), and nothing touches the network. The verdict and the numbers
come from the health tool, so the page can never disagree with the report.
"""

import hashlib
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HEALTH_PY = os.path.join(HERE, "..", "skills", "checker-health", "health.py")

# The pipeline, in order: (step, the skill, the files that show it ran: any one is enough)
STEPS = [
    ("intake", "checker-intake", ("actuals.json",)),
    ("health", "checker-health", ("health.md", "health.json")),
    ("channels", "checker-channels", ("channels.md",)),
    ("customers", "checker-customers", ("customers.md", "customers.json")),
    ("competitors", "checker-competitors", ("competitors.md", "competitors.csv")),
    ("compliance", "checker-compliance", ("compliance.md", "compliance.json")),
    ("board", "checker-board", ("board.md",)),
    ("report", "checker-report", ("report.md",)),
]
# The only documents the page may read: a fixed list, never a path from the browser.
DOCS = [
    ("report.md", "Report"), ("summary.md", "Summary"), ("plan-90.md", "90-day plan"), ("one-pager.md", "One-pager"),
    ("business.md", "The business"), ("health.md", "Health check"), ("channels.md", "Channels"),
    ("customers.md", "Customers"), ("customers-data.md", "Customer data"), ("competitors.md", "Competitors"),
    ("compliance.md", "Compliance"), ("board.md", "Board"),
]
BOARD_LENSES = ["money", "customer", "position", "local-market"]
VOTE_RE = re.compile(r"Score:\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?\s*\|\s*Vote:\s*(GROW|FIX|PIVOT|CLOSE)", re.I)


def _health():
    spec = importlib.util.spec_from_file_location("checker_health_gui", HEALTH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def checker_dir(path):
    """Accept the project folder or the checker/ folder itself."""
    path = os.path.abspath(path)
    if os.path.basename(path.rstrip(os.sep)) == "checker":
        return path
    return os.path.join(path, "checker")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
        return None


def _json(path):
    raw = _read(path)
    if raw is None:
        return None, None
    try:
        return json.loads(raw), None
    except ValueError as e:
        return None, "%s is not valid JSON: %s" % (os.path.basename(path), e)


def watched_files(d):
    files = [name for name, _ in DOCS] + ["actuals.json", "customers.json", "compliance.json"]
    files += ["board/%s.md" % lens for lens in BOARD_LENSES]
    return files


def version(d):
    """Changes whenever any file the page shows changes."""
    h = hashlib.sha1()
    for name in watched_files(d):
        try:
            st = os.stat(os.path.join(d, name))
            h.update(("%s:%d:%d;" % (name, st.st_mtime_ns, st.st_size)).encode())
        except OSError:
            h.update(("%s:-;" % name).encode())
    return h.hexdigest()[:16]


def read_doc(d, name):
    """A document by its name from the fixed list, or None. Never a free path."""
    allowed = dict(DOCS)
    allowed.update({"board/%s.md" % l: "Board: %s lens" % l for l in BOARD_LENSES})
    if name not in allowed:
        return None
    return _read(os.path.join(d, name))


def board(d):
    members = []
    for lens in BOARD_LENSES:
        text = _read(os.path.join(d, "board", "%s.md" % lens))
        if text is None:
            continue
        m = VOTE_RE.search(text)
        members.append({"lens": lens, "doc": "board/%s.md" % lens,
                        "score": float(m.group(1)) if m else None, "vote": m.group(2).upper() if m else None})
    return members


def _plain(h):
    """The parts of the health result the page draws, as plain JSON."""
    keep = ("business", "type", "verdict", "checks", "fixes", "estimates", "targets", "recent", "recent_months",
            "breakeven_month", "breakeven_day", "contribution_ratio", "net_margin", "trend", "cash", "channels",
            "missing_months", "profit_after_owner_pay")
    out = {k: h.get(k) for k in keep if k in h}
    out["months"] = [{k: v for k, v in m.items()} for m in h.get("months", [])]
    return out


def build(path):
    d = checker_dir(path)
    errors = []
    state = {"dir": d, "exists": os.path.isdir(d), "version": version(d), "errors": errors}
    customers, err = _json(os.path.join(d, "customers.json"))
    if err:
        errors.append(err)
    compliance, err = _json(os.path.join(d, "compliance.json"))
    if err:
        errors.append(err)
    actuals, err = _json(os.path.join(d, "actuals.json"))
    if err:
        errors.append(err)
    health = None
    if actuals is not None:
        H = _health()
        try:
            health = _plain(H.analyse(actuals, customers, compliance))
        except ValueError as e:
            errors.append("checker/actuals.json: %s" % e)
    state["health"] = health
    state["verdict"] = health["verdict"] if health else "Incomplete"
    state["customers"] = customers
    state["compliance"] = compliance
    state["board"] = board(d)
    state["steps"] = [{"step": s, "skill": k, "done": any(os.path.exists(os.path.join(d, f)) for f in fs)} for s, k, fs in STEPS]
    state["docs"] = [{"name": n, "title": t} for n, t in DOCS if os.path.exists(os.path.join(d, n))]
    title = None
    biz = _read(os.path.join(d, "business.md"))
    if biz and biz.startswith("# "):
        title = biz.splitlines()[0][2:].strip()
    state["business"] = title or (health and health.get("business")) or "Your business"
    return state


def all_docs(d):
    out = {name: read_doc(d, name) for name, _ in DOCS}
    out.update({"board/%s.md" % l: read_doc(d, "board/%s.md" % l) for l in BOARD_LENSES})
    return {k: v for k, v in out.items() if v is not None}
