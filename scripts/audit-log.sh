#!/usr/bin/env bash
# audit-log.sh — append an entry to the immutable agent audit log
# Usage: ./scripts/audit-log.sh <agent> <action> <target> [details]
# Actions: WRITE READ COMMIT SKIP IMPLEMENT FAIL
# Example: ./scripts/audit-log.sh dev-agent WRITE docs/agentic/backlog.md "moved H-03 to done"
set -euo pipefail

AGENT="${1:-unknown}"
ACTION="${2:-unknown}"
TARGET="${3:-unknown}"
DETAILS="${4:-}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/../docs/agent-audit.log"

# Bootstrap header if log doesn't exist
if [ ! -f "$LOG_FILE" ]; then
  {
    echo "# Agent Audit Log"
    echo "# Append-only — do not edit manually"
    echo "# Format: TIMESTAMP | AGENT | ACTION | TARGET | DETAILS"
    echo "# Created: ${TIMESTAMP}"
  } > "$LOG_FILE"
fi

printf '%s | %-20s | %-10s | %-40s | %s\n' \
  "$TIMESTAMP" "$AGENT" "$ACTION" "$TARGET" "$DETAILS" >> "$LOG_FILE"
