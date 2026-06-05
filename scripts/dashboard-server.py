#!/usr/bin/env python3
"""
dashboard-server.py — optional local companion service for one-click management.

Run it from the project root:

    python3 scripts/dashboard-server.py

then open http://localhost:8787/ — the dashboard's management actions now execute
directly (backlog stage changes, new issues, mark-done, review logging) instead of
only producing a command to copy. Stop it with Ctrl-C; the dashboard then falls back
to the command console.

The server binds to localhost only, serves files under docs/ read-only, and only
mutates docs/agentic/backlog.md, docs/agentic/feedback-log.md, and docs/agentic/agent-requests.md. After a
backlog change it rebuilds the dashboard so a reload shows the new state.

Agent and scheduled-task actions (run / pause / reschedule) cannot be executed by a
local process — they need an agent runtime — so the server records them as durable
requests in docs/agentic/agent-requests.md and the dashboard still offers the copy-command.

Stdlib only.  Port: $DASHBOARD_PORT (default 8787).
"""
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PORT = int(os.environ.get("DASHBOARD_PORT", "8787"))

DOCS = "docs"
DASHBOARD = os.path.join("docs", "dashboard", "index.html")
BACKLOG = os.path.join("docs", "backlog.md")
FEEDBACK = os.path.join("docs", "feedback-log.md")
REQUESTS = os.path.join("docs", "agent-requests.md")

SEV_PREFIX = {"Critical": "C", "High": "H", "Medium": "M", "Low": "L", "GRC": "GRC"}
SEV_SECTION = {"C": "## 🔴 Critical", "H": "## 🟠 High",
               "M": "## 🟡 Medium", "L": "## 🟢 Low / Polish", "GRC": "## 🟡 Medium"}
VALID_STAGES = {"discover", "define", "gtm", "design", "ready", "in-progress", "done"}
CTYPE = {".html": "text/html; charset=utf-8", ".json": "application/json",
         ".css": "text/css", ".js": "text/javascript"}


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return ""


def write(path, text):
    open(path, "w", encoding="utf-8").write(text)


def rebuild_dashboard():
    """Regenerate the dashboard data so a reload reflects the change."""
    try:
        subprocess.run([sys.executable, "scripts/build-dashboard.py"],
                       capture_output=True, timeout=30)
    except Exception:
        pass


def now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def find_issue_line(lines, issue_id):
    rx = re.compile(r"^\|\s*\*?\*?" + re.escape(issue_id) + r"\*?\*?\s*\|")
    for i, ln in enumerate(lines):
        if rx.match(ln.strip()):
            return i
    return -1


# ---- action handlers: each returns (ok: bool, message: str) ----

def act_backlog_stage(d):
    issue_id = (d.get("id") or "").strip()
    stage = (d.get("stage") or "").strip()
    if stage not in VALID_STAGES:
        return False, "invalid stage '%s'" % stage
    lines = read(BACKLOG).splitlines()
    i = find_issue_line(lines, issue_id)
    if i < 0:
        return False, "%s not found in docs/agentic/backlog.md" % issue_id
    cells = lines[i].split("|")
    if len(cells) < 4:
        return False, "%s row is malformed" % issue_id
    cells[2] = " %s " % stage
    lines[i] = "|".join(cells)
    write(BACKLOG, "\n".join(lines) + "\n")
    rebuild_dashboard()
    return True, "%s set to stage=%s" % (issue_id, stage)


def act_backlog_done(d):
    issue_id = (d.get("id") or "").strip()
    lines = read(BACKLOG).splitlines()
    i = find_issue_line(lines, issue_id)
    if i < 0:
        return False, "%s not found in docs/agentic/backlog.md" % issue_id
    cells = lines[i].split("|")
    if len(cells) < 4:
        return False, "%s row is malformed" % issue_id
    cells[2] = " done "
    row = "|".join(cells)
    del lines[i]
    for j, ln in enumerate(lines):
        if ln.strip() == "## ✅ Done":
            lines.insert(j + 1, row)
            write(BACKLOG, "\n".join(lines) + "\n")
            rebuild_dashboard()
            return True, "%s moved to ## ✅ Done" % issue_id
    lines.insert(i, row)
    write(BACKLOG, "\n".join(lines) + "\n")
    rebuild_dashboard()
    return True, "%s marked done (no ## ✅ Done section found)" % issue_id


def act_backlog_new(d):
    prefix = SEV_PREFIX.get(d.get("severity", "High"), "H")
    text = read(BACKLOG)
    nums = [int(n) for n in re.findall(r"\b" + prefix + r"-(\d+)\b", text)]
    new_id = "%s-%02d" % (prefix, (max(nums) + 1) if nums else 1)
    area = (d.get("area") or "").strip() or "—"
    stage = (d.get("stage") or "discover").strip()
    if stage not in VALID_STAGES:
        stage = "discover"
    effort = (d.get("effort") or "M").strip()
    files = (d.get("files") or "").strip()
    files = "`%s`" % files if files else "—"
    issue = (d.get("issue") or "").strip().replace("|", "\\|") or "—"
    row = "| %s | %s | %s | %s | %s | %s |" % (new_id, stage, area, issue, files, effort)
    lines = text.splitlines()
    section = SEV_SECTION[prefix]
    for j, ln in enumerate(lines):
        if ln.strip() == section:
            k = j + 1
            while k < len(lines) and not re.match(r"^\|[-\s|]+\|$", lines[k].strip()):
                k += 1
            insert_at = k + 1 if k < len(lines) else j + 1
            lines.insert(insert_at, row)
            write(BACKLOG, "\n".join(lines) + "\n")
            rebuild_dashboard()
            return True, "filed %s under %s" % (new_id, section.replace("## ", ""))
    return False, "section '%s' not found in docs/agentic/backlog.md" % section


def act_feedback(d):
    agent = (d.get("agent") or "agent").strip()
    verdict = (d.get("verdict") or "revised").strip()
    note = (d.get("note") or "").strip() or "reviewed via dashboard"
    if not os.path.exists(FEEDBACK):
        write(FEEDBACK, "# Feedback Log\n\n"
              "> Agent-output reviews. Appended by the dashboard companion service.\n")
    with open(FEEDBACK, "a", encoding="utf-8") as f:
        f.write("- %s — %s output was %s — %s\n" % (now(), agent, verdict, note))
    return True, "review logged for %s (%s)" % (agent, verdict)


def act_request(d):
    action = (d.get("action") or "run").strip()
    target = (d.get("target") or "").strip()
    extra = (d.get("detail") or "").strip()
    if not os.path.exists(REQUESTS):
        write(REQUESTS, "# Agent Requests\n\n"
              "> Management requests raised from the dashboard. Each line is a durable,\n"
              "> trackable request — an agent run, pause, or reschedule. Tick a box when done.\n")
    line = "- [ ] %s — %s: %s" % (now(), action, target or "—")
    if extra:
        line += " (%s)" % extra
    with open(REQUESTS, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return True, "request logged to docs/agentic/agent-requests.md"


HANDLERS = {
    "backlog-stage": act_backlog_stage,
    "backlog-done": act_backlog_done,
    "backlog-new": act_backlog_new,
    "feedback": act_feedback,
    "request": act_request,
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json")

    def do_OPTIONS(self):
        self._send(204, b"", "text/plain")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/ping":
            project = "Awade"
            m = re.search(r"PROJECT_NAME:\s*(.+)", read("project-config.md"))
            if m:
                project = m.group(1).strip()
            return self._json(200, {"ok": True, "service": "dashboard-server",
                                    "project": project})
        # static: serve the dashboard at / and files under docs/
        if path in ("/", "/index.html", "/dashboard/", "/dashboard/index.html"):
            target = DASHBOARD
        else:
            rel = path.lstrip("/")
            target = os.path.normpath(os.path.join(DOCS, rel))
            if not target.startswith(DOCS + os.sep):
                return self._json(403, {"ok": False, "error": "forbidden"})
        if not os.path.isfile(target):
            return self._json(404, {"ok": False, "error": "not found"})
        ext = os.path.splitext(target)[1]
        ctype = CTYPE.get(ext, "text/plain; charset=utf-8")
        try:
            with open(target, "rb") as f:
                self._send(200, f.read(), ctype)
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

    def do_POST(self):
        if self.path.split("?")[0] != "/api/action":
            return self._json(404, {"ok": False, "error": "unknown endpoint"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"ok": False, "error": "bad request body"})
        handler = HANDLERS.get(data.get("type"))
        if not handler:
            return self._json(400, {"ok": False,
                                    "error": "unknown action '%s'" % data.get("type")})
        try:
            ok, message = handler(data)
            self._json(200 if ok else 422, {"ok": ok,
                                            ("message" if ok else "error"): message})
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})


def main():
    if not os.path.isfile(DASHBOARD):
        print("dashboard-server: %s not found — run scripts/build-dashboard.py first." % DASHBOARD)
        return 1
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("dashboard-server: companion service running")
    print("  open  →  http://localhost:%d/" % PORT)
    print("  one-click backlog, review, and request actions are now live in the dashboard")
    print("  stop  →  Ctrl-C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\ndashboard-server: stopped")
    server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
