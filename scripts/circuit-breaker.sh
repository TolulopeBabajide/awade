#!/usr/bin/env bash
# circuit-breaker.sh — run a command; on failure log and exit 2 (graceful degradation)
# Usage: ./scripts/circuit-breaker.sh <tool-name> <command...>
# Exit 0 = success. Exit 2 = tool unavailable, caller should degrade gracefully.
set -uo pipefail

TOOL="${1:?Usage: circuit-breaker.sh <tool-name> <command...>}"
shift

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HEALTH_DIR="${SCRIPT_DIR}/../.agent-health"
FAIL_LOG="${HEALTH_DIR}/mcp-failures.log"
mkdir -p "$HEALTH_DIR"

"$@"
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "${TIMESTAMP} | UNAVAILABLE | ${TOOL} | exit=${STATUS}" >> "$FAIL_LOG"
  echo "[circuit-breaker] ${TOOL} unavailable (exit ${STATUS}). Degrading gracefully."
  exit 2
fi
exit 0
