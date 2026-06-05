#!/usr/bin/env bash
# check-permissions.sh — Verify an agent is permitted to write to a target path.
#
# Usage:
#   ./scripts/check-permissions.sh <agent-name> <target-file-or-dir>
#
# Exit codes:
#   0 — write is permitted (target path matches an entry in the agent's write list)
#   1 — write is DENIED  (target path is not in the agent's write list)
#   2 — manifest not found or agent not listed in manifest
#
# Example:
#   ./scripts/check-permissions.sh "dev-agent" "docs/agentic/sprints/dev-log.md"
#   ./scripts/check-permissions.sh "marketing-agent" "docs/agentic/specs/foo-spec.md"  # exits 1
#
# The manifest lives at: agent-permissions.json (repo root)

set -euo pipefail

AGENT="${1:-}"
TARGET="${2:-}"
MANIFEST="$(dirname "$0")/../agent-permissions.json"

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
    manifest = json.load(f)

if agent not in manifest:
    print(f"[check-permissions] DENY: agent '{agent}' not found in manifest", file=sys.stderr)
    sys.exit(2)

write_list = manifest[agent].get("write", [])

# Allowed if target equals a permitted path exactly, or is inside a permitted directory.
# The unbounded startswith(allowed) check is intentionally absent — it would allow
# prefix-sibling paths (e.g. docs/agentic/specs-evil matching docs/agentic/specs).
for allowed in write_list:
    allowed = os.path.normpath(allowed.rstrip("/"))
    if target == allowed or target.startswith(allowed + "/"):
        print(f"[check-permissions] ALLOW: '{target}' permitted for {agent}")
        sys.exit(0)

print(f"[check-permissions] DENY: '{target}' not in write list for {agent}", file=sys.stderr)
sys.exit(1)
PYEOF
