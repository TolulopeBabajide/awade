#!/usr/bin/env bash
# idempotency-check.sh — prevent an agent running twice within its window
# Usage: ./scripts/idempotency-check.sh <agent-name> <window-minutes>
# Exit 0 = safe to run (stamps the lock). Exit 1 = already ran, skip.
set -euo pipefail

AGENT="${1:?Usage: idempotency-check.sh <agent-name> <window-minutes>}"
WINDOW_MIN="${2:-50}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HEALTH_DIR="${SCRIPT_DIR}/../.agent-health"
STAMP="${HEALTH_DIR}/${AGENT}.last-run"

mkdir -p "$HEALTH_DIR"

if [ -f "$STAMP" ]; then
  LAST=$(cat "$STAMP")
  NOW=$(date +%s)
  ELAPSED=$(( (NOW - LAST) / 60 ))
  if [ "$ELAPSED" -lt "$WINDOW_MIN" ]; then
    echo "[idempotency] ${AGENT} ran ${ELAPSED}m ago (window=${WINDOW_MIN}m). Skipping."
    exit 1
  fi
fi

# Stamp and allow
date +%s > "$STAMP"
echo "[idempotency] ${AGENT} cleared. Running."
exit 0
