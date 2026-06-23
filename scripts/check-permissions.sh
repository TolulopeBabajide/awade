#!/usr/bin/env bash
# check-permissions.sh — Verify an agent is permitted to write to a target path.
#
# Usage:
#   ./scripts/check-permissions.sh <agent-name> <target-file-or-dir> [manifest-path]
#
# Exit codes:
#   0 — write is permitted (target path matches an entry in the agent's write list)
#   1 — write is DENIED  (target path is not in the agent's write list)
#   2 — manifest not found or agent not listed in manifest
#
# Example:
#   ./scripts/check-permissions.sh "dev-agent" "docs/agentic/sprints/dev-log.md"
#   ./scripts/check-permissions.sh "marketing-agent" "docs/agentic/specs/foo-spec.md"  # exits 1
#   ./scripts/check-permissions.sh "dev-agent" "docs/agentic/backlog.md" /tmp/custom-manifest.json
#
# The manifest defaults to: agent-permissions.json (repo root)

set -euo pipefail

AGENT="${1:-}"
TARGET="${2:-}"
MANIFEST="${3:-$(dirname "$0")/../agent-permissions.json}"

if [[ -z "$AGENT" || -z "$TARGET" ]]; then
  echo "Usage: $0 <agent-name> <target-file-or-dir>" >&2
  exit 2
fi

if [[ ! -f "$MANIFEST" ]]; then
  echo "[check-permissions] ERROR: manifest not found at $MANIFEST" >&2
  exit 2
fi

# Use python3 to parse JSON and do prefix matching
python3 - "$AGENT" "$TARGET" "$MANIFEST" << 'PYEOF'
import sys, json, os

agent  = sys.argv[1]
# Canonicalize target: strip leading slash then normalize to resolve .. components
target = os.path.normpath(sys.argv[2].lstrip("/"))
manifest_path = sys.argv[3]

with open(manifest_path) as f:
    try:
        manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[check-permissions] ERROR: invalid JSON in manifest {manifest_path}: {e}", file=sys.stderr)
        sys.exit(2)

agents = manifest.get("agents", manifest)
if agent not in agents:
    print(f"[check-permissions] DENY: agent '{agent}' not found in manifest", file=sys.stderr)
    sys.exit(2)

write_list = agents[agent].get("writes", agents[agent].get("write", []))

# Allowed if target equals a permitted path exactly, or is inside a permitted directory.
# Glob suffixes (/** or /*) are stripped to their directory prefix before comparison so
# that "docs/tech-debt/**" matches "docs/tech-debt/report.md" without a startswith that
# could match sibling prefixes (e.g. docs/agentic/specs-evil vs docs/agentic/specs).
# Final-component globs (e.g. *.py, sprint-*.md, *.last-run) are also stripped so that
# "alembic/versions/*.py" matches "alembic/versions/0001_foo.py".
for allowed in write_list:
    # Strip trailing glob components before normalization
    if allowed.endswith("/**") or allowed.endswith("/*"):
        allowed = allowed.rsplit("/", 1)[0]
    elif "*" in allowed.rsplit("/", 1)[-1]:
        # e.g. alembic/versions/*.py  → alembic/versions
        #      sprint-plans/sprint-*.md → sprint-plans
        #      .agent-health/*.last-run → .agent-health
        allowed = allowed.rsplit("/", 1)[0]
    # NOTE: mid-path wildcards (e.g. docs/*/report.md) are NOT supported.
    # rsplit("/", 1)[-1] returns the final component ("report.md"), which contains
    # no "*", so neither branch above fires and the literal path reaches normpath —
    # where it will never match a real target.  No current manifest entry uses this
    # pattern; if one is ever added, extend this logic to detect and strip mid-path
    # wildcard components before reaching normpath.
    allowed = os.path.normpath(allowed.rstrip("/"))
    if target == allowed or target.startswith(allowed + "/"):
        print(f"[check-permissions] ALLOW: '{target}' permitted for {agent}")
        sys.exit(0)

print(f"[check-permissions] DENY: '{target}' not in write list for {agent}", file=sys.stderr)
sys.exit(1)
PYEOF
