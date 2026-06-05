#!/usr/bin/env python3
"""
check-backlog-format.py — validate docs/agentic/backlog.md against docs/agentic/BACKLOG-FORMAT.md.

Awade row format (6 columns, Stage last):
  | # | Area | Issue | File(s) | Effort | Stage |

For each ACTIVE issue row — a table row whose first cell is a valid issue ID — it checks:
  - exactly 6 columns
  - ID prefix is one of C / H / M / L / GRC
  - Stage is a canonical lifecycle value
  - Effort is one of XS / S / M / L
  - Issue cell is non-empty (not blank, not "TBD")
  - no duplicate issue IDs

Rows whose ID is struck through (~~H-12~~) are resolved-in-place legacy rows:
only the duplicate-ID check applies. Completed issues belong in
docs/agentic/completed_backlog.md (different format — not validated here).

Usage:  python3 scripts/check-backlog-format.py [path-to-backlog.md]
Exit:   0 = valid, 1 = problems found or file missing.
"""
import re
import sys

VALID_STAGES = {"discover", "define", "gtm", "design", "ready", "in-progress", "done"}
VALID_EFFORT = {"XS", "S", "M", "L"}
ID_RE = re.compile(r"^(?:AWD-)?(C|H|M|L|GRC)-\d+$")
STRUCK_RE = re.compile(r"^~~(?:AWD-)?(C|H|M|L|GRC)-\d+~~$")
_PIPE = "\x00"  # placeholder for escaped pipes while splitting


def split_row(line):
    """Split a markdown table row into trimmed cells, honouring escaped \\| pipes."""
    body = line.strip().strip("|").replace(r"\|", _PIPE)
    return [c.replace(_PIPE, r"\|").strip() for c in body.split("|")]


def main(path="docs/agentic/backlog.md"):
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except FileNotFoundError:
        print(f"✗ {path} not found")
        return 1

    errors = []
    seen = {}

    for n, line in enumerate(lines, 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = split_row(s)
        if not cells:
            continue
        first = cells[0]

        struck = bool(STRUCK_RE.match(first))
        if not struck and not ID_RE.match(first):
            continue  # header, separator, legend, or placeholder row

        issue_id = first.strip("~")
        if issue_id in seen:
            errors.append(f"line {n}: duplicate ID {issue_id} (first seen line {seen[issue_id]})")
        else:
            seen[issue_id] = n

        if struck:
            continue  # legacy resolved-in-place row — dup check only

        if len(cells) != 6:
            errors.append(f"line {n}: {issue_id} has {len(cells)} columns, expected 6 (| # | Area | Issue | File(s) | Effort | Stage |)")
            continue

        _, area, issue, files, effort, stage = cells
        if not issue or issue.upper() == "TBD":
            errors.append(f"line {n}: {issue_id} Issue cell is empty or TBD")
        if stage not in VALID_STAGES:
            errors.append(f"line {n}: {issue_id} invalid stage '{stage}' (valid: {', '.join(sorted(VALID_STAGES))})")
        if effort not in VALID_EFFORT:
            errors.append(f"line {n}: {issue_id} invalid effort '{effort}' (valid: XS S M L)")

    if errors:
        print(f"✗ {path}: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✓ {path}: {len(seen)} issue rows OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
