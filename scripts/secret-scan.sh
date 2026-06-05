#!/usr/bin/env bash
# secret-scan.sh — scan a file for patterns resembling secrets
# Usage: ./scripts/secret-scan.sh <file>  |  cat file | ./scripts/secret-scan.sh -
# Exit 0 = clean. Exit 1 = secrets detected.
set -uo pipefail

FILE="${1:--}"
FOUND=0
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

declare -a PATTERNS=(
  "sk[-_][a-zA-Z0-9]{20,}"
  "AIza[0-9A-Za-z_-]{35}"
  "AKIA[0-9A-Z]{16}"
  "ghp_[a-zA-Z0-9]{36}"
  "xoxb-[0-9]+-[a-zA-Z0-9-]+"
  "-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"
  "password['\"]?\s*[:=]\s*['\"][^'\"]{8,}['\"]"
  "secret['\"]?\s*[:=]\s*['\"][^'\"]{8,}['\"]"
  "token['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_\-\.]{20,}['\"]"
)

for pattern in "${PATTERNS[@]}"; do
  if grep -qiE "$pattern" "$FILE" 2>/dev/null; then
    echo "[secret-scan] ${TIMESTAMP} DETECTED /${pattern}/ in ${FILE}" >&2
    FOUND=1
  fi
done

if [ "$FOUND" -eq 0 ]; then
  echo "[secret-scan] Clean: ${FILE}"
fi
exit "$FOUND"
