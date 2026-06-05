#!/usr/bin/env python3
"""
build-dashboard.py — regenerate the agent monitoring dashboard.

Reads the project's activity files (heartbeats, run log, audit log, backlog,
scheduled tasks, agent outputs, failure logs) and writes a fresh data block
into docs/agentic/dashboard/index.html. The dashboard HTML is self-contained — the
data is baked in between sentinel comments, so it opens in any browser offline.

Run from the repo root. The dashboard-refresh agent runs it on a schedule.

Stdlib only. Usage: python3 scripts/build-dashboard.py
Exit: 0 = dashboard rebuilt, 1 = dashboard HTML shell missing.
"""
import os
import re
import json
import glob
import time
from datetime import datetime, timezone

DASHBOARD = "docs/agentic/dashboard/index.html"
NOW = time.time()

# scheduled-task id -> the agent skill that runs it
TASK_AGENT = {
    "security-scan": "security-agent", "daily-health-check": "daily-health-check",
    "weekly-review": "weekly-review", "sprint-planning": "sprint-planning",
    "content-calendar": "marketing-agent", "friday-finance": "finance-agent",
    "nightly-monitor": "nightly-monitor", "weekend-ops": "weekend-ops",
    "marketing-daily": "marketing-agent", "dev-execution": "dev-agent",
    "qa-validation": "qa-agent", "analytics-daily": "analytics-agent",
    "support-digest": "support-agent", "seo-weekly": "seo-agent",
    "improvement-loop": "improvement-agent", "code-review-loop": "code-review-agent",
    "performance-benchmark": "performance-agent", "architecture-review": "architecture-agent",
    "tech-debt-audit": "tech-debt-agent", "dependency-security-scan": "dependency-security-agent",
    "compliance-audit": "compliance-agent", "access-control-review": "access-review-agent",
    "dashboard-refresh": "dashboard-refresh",
}

OUTPUT_GLOBS = [
    ("docs/audits/security-report-*.md", "Security audit"),
    ("docs/audits/secret-scan-*.md", "Secret scan"),
    ("docs/audits/dep-security-*.md", "Dependency audit"),
    ("docs/audits/access-review-*.md", "Access review"),
    ("docs/code-reviews/*.md", "Code review"),
    ("docs/agentic/weekly-reviews/review-*.md", "Weekly review"),
    ("docs/agentic/weekly-reviews/retro-*.md", "Retrospective"),
    ("docs/agentic/daily-briefs/*.md", "Daily brief"),
    ("docs/performance/*.md", "Performance"),
    ("docs/architecture/*.md", "Architecture"),
    ("docs/tech-debt/*.md", "Tech debt"),
    ("docs/legal/*.md", "Compliance / legal"),
    ("docs/agentic/sprint-plans/*.md", "Sprint plan"),
    ("docs/agentic/specs/*.md", "Spec"),
    ("docs/agentic/gtm/*.md", "GTM"),
    ("docs/agentic/design/*.md", "Design handoff"),
    ("docs/agentic/discovery/*.md", "Discovery"),
]

SEV = {"C": "critical", "H": "high", "M": "medium", "L": "low", "GRC": "grc"}

# output category -> the agent that produced it (for the review action)
CATEGORY_AGENT = {
    "Security audit": "security-agent", "Secret scan": "security-agent",
    "Dependency audit": "dependency-security-agent", "Access review": "access-review-agent",
    "Code review": "code-review-agent", "Weekly review": "weekly-review",
    "Retrospective": "weekend-ops", "Daily brief": "nightly-monitor",
    "Performance": "performance-agent", "Architecture": "architecture-agent",
    "Tech debt": "tech-debt-agent", "Compliance / legal": "compliance-agent",
    "Sprint plan": "sprint-planning", "Spec": "pm-agent", "GTM": "gtm-agent",
    "Design handoff": "design-agent", "Discovery": "discovery-agent",
}


def iso_to_unix(s):
    try:
        dt = datetime.strptime(s.strip(), "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return None


def cadence_from_cron(cron):
    """Return (label, expected-window-minutes) from a 5-field cron string."""
    parts = cron.split()
    if len(parts) != 5:
        return ("on-demand", 0)
    _minute, hour, dom, _mon, dow = parts
    if hour == "*":
        return ("hourly", 70)
    if hour.startswith("*/"):
        try:
            n = int(hour[2:])
        except ValueError:
            n = 3
        return ("every %dh" % n, n * 60 + 30)
    if dow != "*":
        if "-" in dow:
            return ("weekdays", 4500)
        if "," in dow:
            return ("twice weekly", 6000)
        if dom != "*":
            return ("monthly", 44640)
        return ("weekly", 11520)
    return ("daily", 1620)


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except Exception:
        return ""


def project_name():
    m = re.search(r"PROJECT_NAME:\s*(.+)", read("project-config.md"))
    return m.group(1).strip() if m else "Awade"


def parse_tasks():
    text = read("docs/agentic/SCHEDULED-TASKS.md")
    tasks = []
    for section in text.split("\n## "):
        m = re.match(r"Task (\d+): (.+)", section)
        if not m:
            continue
        idm = re.search(r"\*\*ID\*\*: `([^`]+)`", section)
        if not idm:
            continue
        schm = re.search(r"\*\*Schedule\*\*: ([^\n]+)", section)
        rtm = re.search(r"\*\*Runtime\*\*: ([^\n]+)", section)
        sched = schm.group(1).strip() if schm else ""
        cron = ""
        for cm in re.finditer(r"`([-0-9*/, ]+)`", sched):
            if len(cm.group(1).split()) == 5:
                cron = cm.group(1).strip()
                break
        cadence, _window = cadence_from_cron(cron)
        tasks.append({
            "num": int(m.group(1)),
            "id": idm.group(1),
            "name": m.group(2).strip(),
            "schedule": re.sub(r"\s*\(`[^`]+`\)", "", sched).strip(),
            "cron": cron,
            "runtime": rtm.group(1).strip() if rtm else "—",
            "cadence": cadence,
        })
    tasks.sort(key=lambda t: t["num"])
    return tasks


def parse_heartbeats():
    hb = {}
    for path in glob.glob(".agent-health/*.last-run"):
        name = os.path.basename(path)[:-len(".last-run")]
        try:
            hb[name] = int(read(path).strip())
        except Exception:
            pass
    return hb


def build_agents(tasks, heartbeats):
    # window + cadence per scheduled agent, from its task's cron
    agent_meta = {}
    for t in tasks:
        agent = TASK_AGENT.get(t["id"])
        if not agent:
            continue
        _label, window = cadence_from_cron(t["cron"])
        agent_meta[agent] = {
            "runtime": t["runtime"], "schedule": t["schedule"],
            "cadence": t["cadence"], "window": window,
        }
    skills = sorted(os.path.basename(p.rstrip("/"))
                    for p in glob.glob(".claude/skills/*/") if os.path.isdir(p))
    agents = []
    for name in skills:
        meta = agent_meta.get(name)
        hb = heartbeats.get(name)
        age_min = int((NOW - hb) / 60) if hb else None
        if meta:
            window = meta["window"]
            if hb is None:
                status = "idle"
            elif age_min < window:
                status = "healthy"
            elif age_min < window * 2:
                status = "warning"
            else:
                status = "critical"
        else:
            status = "on-demand"
            window = 0
        agents.append({
            "name": name,
            "scheduled": meta is not None,
            "runtime": meta["runtime"] if meta else "—",
            "schedule": meta["schedule"] if meta else "on-demand",
            "cadence": meta["cadence"] if meta else "on-demand",
            "windowMin": window,
            "lastRunUnix": hb,
            "lastRunIso": (datetime.fromtimestamp(hb, timezone.utc)
                           .strftime("%Y-%m-%dT%H:%M:%SZ") if hb else None),
            "ageMin": age_min,
            "status": status,
        })
    return agents


def parse_runlog():
    rows = []
    for line in read("docs/agentic/agent-run-log.jsonl").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        ts = parts[0]
        unix = iso_to_unix(ts)
        if unix is None:
            continue
        agent = re.sub(r"^agt-", "", parts[1])
        agent = TASK_AGENT.get(agent, agent)
        rows.append({
            "ts": ts, "unix": unix, "agent": agent, "kind": "run",
            "status": parts[2], "summary": parts[3] if len(parts) > 3 else "",
        })
    return rows


def parse_auditlog():
    rows = []
    for line in read("docs/agent-audit.log").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        unix = iso_to_unix(parts[0])
        if unix is None:
            continue
        rows.append({
            "ts": parts[0], "unix": unix, "agent": parts[1], "kind": "action",
            "status": parts[2], "target": parts[3],
            "summary": parts[4] if len(parts) > 4 else "",
        })
    return rows


def parse_backlog():
    text = read("docs/agentic/backlog.md")
    severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "grc": 0}
    stage = {"discover": 0, "define": 0, "gtm": 0, "design": 0,
             "ready": 0, "in-progress": 0}
    items = []
    done = 0
    # split on the heading (newline-anchored) — the string also appears in a header note
    active, _, donepart = text.partition("\n## ✅ Done")
    row_re = re.compile(r"^\|\s*\*?\*?(C|H|M|L|GRC)-(\d+)\*?\*?\s*\|")
    for line in active.splitlines():
        m = row_re.match(line.strip())
        if not m:
            continue
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        st = cells[1]
        if st == "done":
            done += 1  # a done row inside an active section — count it as done, not open
            continue
        sev = SEV[m.group(1)]
        severity[sev] += 1
        if st in stage:
            stage[st] += 1
        items.append({
            "id": cells[0], "severity": sev, "stage": st, "area": cells[2],
            "issue": cells[3], "files": cells[4], "effort": cells[5],
        })
    for line in donepart.splitlines():
        if re.match(r"^\|\s*\*?\*?(C|H|M|L|GRC)-\d+", line.strip()):
            done += 1
    return {"severity": severity, "stage": stage, "items": items, "done": done}


def scan_outputs():
    """Recent agent output documents, each with its full text baked in for inline review."""
    seen = set()
    outs = []
    for pattern, label in OUTPUT_GLOBS:
        for path in glob.glob(pattern):
            if path in seen or not os.path.isfile(path):
                continue
            seen.add(path)
            dm = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
            outs.append({
                "title": os.path.basename(path),
                "path": "../" + path[len("docs/"):],
                "category": label,
                "agent": CATEGORY_AGENT.get(label, ""),
                "date": dm.group(1) if dm else "",
                "_mtime": os.path.getmtime(path),
                "_fpath": path,
            })
    outs.sort(key=lambda o: (o["date"], o["_mtime"]), reverse=True)
    outs = outs[:40]
    for o in outs:
        txt = read(o.pop("_fpath"))
        o.pop("_mtime", None)
        lines = txt.splitlines()
        if len(lines) > 700:
            txt = "\n".join(lines[:700]) + (
                "\n\n*… %d more lines — open the source file for the full document.*"
                % (len(lines) - 700))
        if len(txt) > 60000:
            txt = txt[:60000] + "\n\n*… truncated — open the source file for the full document.*"
        o["content"] = txt
    return outs


def parse_alerts():
    def rows(path, marker):
        out = []
        for line in read(path).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and marker in line:
                out.append({"ts": parts[0],
                            "detail": " | ".join(parts[1:])})
        return out
    return {
        "mcp": rows(".agent-health/mcp-failures.log", "UNAVAILABLE"),
        "sync": rows(".agent-health/sync-failures.log", "DEFERRED")
              + rows(".agent-health/sync-failures.log", "FAILED"),
    }


def main():
    if not os.path.exists(DASHBOARD):
        print("build-dashboard: %s not found — cannot inject data" % DASHBOARD)
        return 1

    tasks = parse_tasks()
    heartbeats = parse_heartbeats()
    agents = build_agents(tasks, heartbeats)
    runlog = parse_runlog()
    timeline = runlog + parse_auditlog()
    timeline.sort(key=lambda r: r["unix"], reverse=True)
    timeline = timeline[:300]

    run_counts = {}
    for row in runlog:
        if NOW - row["unix"] < 86400:
            run_counts[row["agent"]] = run_counts.get(row["agent"], 0) + 1
    for a in agents:
        a["runs24h"] = run_counts.get(a["name"], 0)
    backlog = parse_backlog()
    outputs = scan_outputs()
    alerts = parse_alerts()
    brief = read("docs/agentic/daily-briefs/morning-brief.md") or None

    counts = {"healthy": 0, "warning": 0, "critical": 0, "idle": 0, "on-demand": 0}
    for a in agents:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    runs24h = sum(1 for r in timeline if r["kind"] == "run" and NOW - r["unix"] < 86400)
    alert_n = len(alerts["mcp"]) + len(alerts["sync"])
    sev = backlog["severity"]
    open_n = sum(sev.values())
    if counts["critical"] or sev["critical"] or alerts["sync"]:
        status = "red"
    elif counts["warning"] or counts["idle"] or sev["high"] or alerts["mcp"]:
        status = "yellow"
    else:
        status = "green"

    data = {
        "project": project_name(),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "status": status,
            "agents": {**counts, "total": len(agents)},
            "backlog": {**sev, "open": open_n, "done": backlog["done"]},
            "runs24h": runs24h,
            "alerts": alert_n,
        },
        "agents": agents,
        "tasks": tasks,
        "timeline": timeline,
        "backlog": backlog,
        "outputs": outputs,
        "alerts": alerts,
        "brief": brief,
    }

    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = read(DASHBOARD)
    pattern = re.compile(
        r"/\* DASHBOARD_DATA_START \*/.*?/\* DASHBOARD_DATA_END \*/", re.DOTALL)
    replacement = ("/* DASHBOARD_DATA_START */\n"
                   "window.DASHBOARD_DATA = " + blob + ";\n"
                   "/* DASHBOARD_DATA_END */")
    if not pattern.search(html):
        print("build-dashboard: data sentinels not found in %s" % DASHBOARD)
        return 1
    # lambda replacement → used literally; avoids re.sub interpreting \n, \1, etc. in the JSON
    open(DASHBOARD, "w", encoding="utf-8").write(
        pattern.sub(lambda _m: replacement, html, count=1))

    print("build-dashboard: rebuilt %s" % DASHBOARD)
    print("  agents: %d (%d healthy, %d warning, %d critical, %d idle, %d on-demand)"
          % (len(agents), counts["healthy"], counts["warning"], counts["critical"],
             counts["idle"], counts["on-demand"]))
    print("  tasks: %d | timeline: %d | open issues: %d | outputs: %d | alerts: %d"
          % (len(tasks), len(timeline), open_n, len(outputs), alert_n))
    print("  overall status: %s" % status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
