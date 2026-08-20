#!/usr/bin/env bash
# run-secret-scan-docs.sh — scan docs/, scripts/, and config files for secret patterns
# Usage: ./scripts/run-secret-scan-docs.sh
# Exit 0 = clean. Exit 1 = secrets detected.
# Writes a scan report to docs/audits/secret-scan-[DATE].md.
# On detection, prints file paths only — never the secret values.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKLOG="${REPO_ROOT}/docs/agentic/backlog.md"
SCAN_DATE=$(date -u +"%Y-%m-%d")
SCAN_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SCAN_OUT="${REPO_ROOT}/docs/audits/secret-scan-${SCAN_DATE}.md"
SECRET_SCAN="${SCRIPT_DIR}/secret-scan.sh"
AUDIT_LOG="${REPO_ROOT}/docs/agent-audit.log"

mkdir -p "${REPO_ROOT}/docs/audits"

SECRETS_FOUND=0
FILES_SCANNED=0
DETECTED_FILES=()

# ---------------------------------------------------------------------------
# Collect files to scan: docs/, scripts/, root config files
# ---------------------------------------------------------------------------
mapfile -t SCAN_TARGETS < <(
  find "${REPO_ROOT}/docs" -type f \( -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null
  find "${REPO_ROOT}/scripts" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.json" \) 2>/dev/null
  find "${REPO_ROOT}" -maxdepth 1 -type f \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" \) 2>/dev/null
)

# ---------------------------------------------------------------------------
# Write report header
# ---------------------------------------------------------------------------
cat > "$SCAN_OUT" <<HEADER
# Secret Scan Report — ${SCAN_DATE}

**Run at**: ${SCAN_TIME}
**Scanner**: scripts/secret-scan.sh
**Scope**: docs/, scripts/, root config files

HEADER

# ---------------------------------------------------------------------------
# Scan each file
# ---------------------------------------------------------------------------
for f in "${SCAN_TARGETS[@]}"; do
  [ -f "$f" ] || continue
  FILES_SCANNED=$((FILES_SCANNED + 1))
  RESULT=$(bash "$SECRET_SCAN" "$f" 2>&1)
  STATUS=$?
  if [ "$STATUS" -ne 0 ]; then
    RELATIVE="${f#${REPO_ROOT}/}"
    echo "🔴 DETECTED: ${RELATIVE}" >> "$SCAN_OUT"
    DETECTED_FILES+=("${RELATIVE}")
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
  fi
done

# ---------------------------------------------------------------------------
# Write summary
# ---------------------------------------------------------------------------
echo "" >> "$SCAN_OUT"
echo "---" >> "$SCAN_OUT"
echo "" >> "$SCAN_OUT"
echo "**Files scanned**: ${FILES_SCANNED}" >> "$SCAN_OUT"
echo "**Secrets detected**: ${SECRETS_FOUND}" >> "$SCAN_OUT"

if [ "$SECRETS_FOUND" -eq 0 ]; then
  echo "**Result**: ✅ Clean — no secret patterns found" >> "$SCAN_OUT"
  echo "[secret-scan-docs] Clean: ${FILES_SCANNED} files scanned, 0 secrets detected"
else
  echo "**Result**: 🔴 SECRETS DETECTED — rotate affected credentials immediately" >> "$SCAN_OUT"
  echo "" >> "$SCAN_OUT"
  echo "**Affected files (paths only — no values)**:" >> "$SCAN_OUT"
  for df in "${DETECTED_FILES[@]}"; do
    echo "- ${df}" >> "$SCAN_OUT"
  done

  # File a C-## Critical backlog item
  if [ -f "$BACKLOG" ]; then
    LAST_NUM=$(grep -oE 'C-[0-9]+' "$BACKLOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
    NEXT_NUM="01"
    if [ -n "$LAST_NUM" ]; then
      NEXT_NUM=$(printf "%02d" $(( 10#$LAST_NUM + 1 )))
    fi
    ISSUE_ID="C-${NEXT_NUM}"
    ISSUE_TEXT="Secret pattern detected by secret-scan-docs in ${SECRETS_FOUND} file(s) — rotate credentials immediately"

    python3 - "$BACKLOG" "$ISSUE_ID" "$ISSUE_TEXT" "$SCAN_OUT" <<'PYEOF'
import sys, re

backlog_path, issue_id, issue_text, filepath = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(backlog_path, 'r') as fh:
    content = fh.read()

new_row = f"| {issue_id} | ready | Security | {issue_text} | `{filepath}` | S |"
placeholder = '| — | — | — | No critical issues | — | — |'
if placeholder in content:
    content = content.replace(placeholder, new_row)
else:
    content = re.sub(
        r'(## 🔴 Critical\n\n\| # \| Stage \| Area \| Issue \| File\(s\) \| Effort \|\n\|[-| ]+\|\n)',
        lambda m: m.group(0) + new_row + '\n',
        content
    )
with open(backlog_path, 'w') as fh:
    fh.write(content)
print(f"[secret-scan-docs] FILED: {issue_id} — {issue_text}")
PYEOF
  fi

  echo "[secret-scan-docs] 🔴 SECRETS DETECTED in ${SECRETS_FOUND} file(s) — see ${SCAN_OUT}" >&2
fi

# ---------------------------------------------------------------------------
# Audit log entry
# ---------------------------------------------------------------------------
AUDIT_MSG="secret scan: ${FILES_SCANNED} files scanned, ${SECRETS_FOUND} secrets detected — ${SCAN_OUT}"
if [ -x "${SCRIPT_DIR}/audit-log.sh" ]; then
  "${SCRIPT_DIR}/audit-log.sh" "security-agent" "READ" "docs/audits/" "${AUDIT_MSG}" 2>/dev/null || true
else
  echo "${SCAN_TIME} | security-agent | READ | docs/audits/ | ${AUDIT_MSG}" >> "$AUDIT_LOG"
fi

exit "$SECRETS_FOUND"
