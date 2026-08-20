#!/usr/bin/env bash
# validate-output.sh — validate an agent output file before it is accepted
# Usage: ./scripts/validate-output.sh <agent-name> <output-file>
# Exit 0 = valid. Exit 1 = rejected (hard failure).
# On hard failure, automatically files a C-## Critical item in docs/agentic/backlog.md.
set -uo pipefail

AGENT="${1:?Usage: validate-output.sh <agent-name> <output-file>}"
FILE="${2:?Usage: validate-output.sh <agent-name> <output-file>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKLOG="${REPO_ROOT}/docs/agentic/backlog.md"
ISSUES=0

# ---------------------------------------------------------------------------
# file_critical_bug <reason>
# Appends a C-## row to docs/agentic/backlog.md critical table and logs to audit log.
# ---------------------------------------------------------------------------
file_critical_bug() {
  local reason="$1"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  if [ ! -f "$BACKLOG" ]; then
    echo "[validate] WARN: cannot file C-## — backlog not found: ${BACKLOG}" >&2
    return
  fi

  # Determine next C-## ID (find highest existing, increment by 1)
  local last_num
  last_num=$(grep -oE 'C-[0-9]+' "$BACKLOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
  local next_num="01"
  if [ -n "$last_num" ]; then
    next_num=$(printf "%02d" $(( 10#$last_num + 1 )))
  fi
  local issue_id="C-${next_num}"
  local short_file
  short_file=$(basename "$FILE")
  local issue_text="validate-output FAIL: ${AGENT} — ${reason} — ${short_file}"

  # Use Python3 to reliably insert the row into the Critical section of backlog.md
  python3 - "$BACKLOG" "$issue_id" "$issue_text" "$FILE" <<'PYEOF'
import sys, re, os

backlog_path, issue_id, issue_text, filepath = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

with open(backlog_path, 'r') as f:
    content = f.read()

new_row = f"| {issue_id} | ready | Infra | {issue_text} | `{filepath}` | S |"

# Replace the "no critical issues" placeholder if present
placeholder = '| — | — | — | No critical issues | — | — |'
if placeholder in content:
    content = content.replace(placeholder, new_row)
else:
    # Insert after the separator row in the Critical section header
    content = re.sub(
        r'(## 🔴 Critical\n\n\| # \| Stage \| Area \| Issue \| File\(s\) \| Effort \|\n\|[-| ]+\|\n)',
        lambda m: m.group(0) + new_row + '\n',
        content
    )

with open(backlog_path, 'w') as f:
    f.write(content)

print(f"[validate] FILED: {issue_id} in docs/agentic/backlog.md — {issue_text}")
PYEOF

  # Audit log entry for the filed critical bug
  if [ -x "${SCRIPT_DIR}/audit-log.sh" ]; then
    "${SCRIPT_DIR}/audit-log.sh" "validate-output" "WRITE" "$BACKLOG" \
      "filed ${issue_id}: ${reason} from ${AGENT}" 2>/dev/null || true
  fi
}

# ---------------------------------------------------------------------------
# 1. File must exist
# ---------------------------------------------------------------------------
if [ ! -f "$FILE" ]; then
  echo "[validate] FAIL: file not found: ${FILE}" >&2
  file_critical_bug "file not found"
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. File must not be empty
# ---------------------------------------------------------------------------
if [ ! -s "$FILE" ]; then
  echo "[validate] FAIL: ${AGENT} produced empty output: ${FILE}" >&2
  file_critical_bug "empty output file"
  exit 1
fi

# ---------------------------------------------------------------------------
# 3. Minimum length (chars)
# ---------------------------------------------------------------------------
THRESHOLDS_FILE="${SCRIPT_DIR}/output-thresholds.json"
MIN_CHARS=200  # default
if [ -f "$THRESHOLDS_FILE" ] && command -v python3 &>/dev/null; then
  AGENT_MIN=$(python3 -c "
import json, sys
t = json.load(open('$THRESHOLDS_FILE'))
print(t.get('$AGENT', t.get('default', 200)))
" 2>/dev/null || echo 200)
  MIN_CHARS="$AGENT_MIN"
fi
CHAR_COUNT=$(wc -c < "$FILE" | tr -d ' ')
if [ "$CHAR_COUNT" -lt "$MIN_CHARS" ]; then
  echo "[validate] WARN: ${AGENT} output short (${CHAR_COUNT}/${MIN_CHARS} chars): ${FILE}" >&2
  ISSUES=$((ISSUES + 1))
fi

# ---------------------------------------------------------------------------
# 4. Must have a markdown heading
# ---------------------------------------------------------------------------
if ! grep -q "^#" "$FILE"; then
  echo "[validate] WARN: ${AGENT} output missing markdown heading: ${FILE}" >&2
  ISSUES=$((ISSUES + 1))
fi

# ---------------------------------------------------------------------------
# 5. Secret scan — hard failure if a secret pattern is detected
# ---------------------------------------------------------------------------
if [ -x "${SCRIPT_DIR}/secret-scan.sh" ]; then
  if ! "${SCRIPT_DIR}/secret-scan.sh" "$FILE" 2>/dev/null; then
    echo "[validate] FAIL: secret detected in ${AGENT} output — rejecting: ${FILE}" >&2
    file_critical_bug "secret pattern detected — output rejected"
    exit 1
  fi
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 6. Rebuild TF-IDF index (non-blocking — failures are logged, not fatal)
# ---------------------------------------------------------------------------
INDEX_SCRIPT="${SCRIPT_DIR}/build-index.py"
if command -v python3 &>/dev/null && [ -f "$INDEX_SCRIPT" ]; then
  python3 "$INDEX_SCRIPT" 2>/dev/null &
fi

if [ "$ISSUES" -gt 0 ]; then
  echo "[validate] WARN: ${AGENT} output has ${ISSUES} warning(s): ${FILE}"
else
  echo "[validate] OK: ${AGENT} → ${FILE} (${CHAR_COUNT} chars)"
fi
exit 0
