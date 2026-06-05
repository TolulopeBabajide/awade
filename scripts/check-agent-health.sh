#!/usr/bin/env bash
# check-agent-health.sh — read .last-run heartbeat files and produce an Agent Health report
# Usage: ./scripts/check-agent-health.sh
# Output: prints a markdown "## Agent Health" section to stdout
# Exit 0 = all agents OK or WARNING only. Exit 1 = at least one CRITICAL agent.
#
# Expected windows:
#   Hourly agents  (dev-agent, qa-agent, code-review-agent):     70 min
#   Daily agents   (security-agent, analytics-agent,
#                   support-agent, growth-agent, marketing-agent,
#                   finance-agent, nightly-monitor,
#                   content-agent, improvement-agent):           1500 min (25 hr)
#   Weekly agents  (weekly-review, sprint-planning):            11520 min (8 days)
#
# Portability: bash 3.2+ (macOS and Linux). No associative arrays.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HEALTH_DIR="${SCRIPT_DIR}/../.agent-health"
NOW=$(date +%s)
HAS_CRITICAL=0

# get_window <agent-name> — echo the expected window in minutes
get_window() {
  case "$1" in
    dev-agent)         echo 70 ;;
    qa-agent)          echo 70 ;;
    code-review-agent) echo 70 ;;
    security-agent)    echo 1500 ;;
    analytics-agent)   echo 1500 ;;
    support-agent)     echo 1500 ;;
    growth-agent)      echo 1500 ;;
    marketing-agent)   echo 1500 ;;
    finance-agent)     echo 1500 ;;
    nightly-monitor)   echo 1500 ;;
    content-agent)     echo 1500 ;;
    improvement-agent) echo 1500 ;;
    daily-health-check)        echo 1500 ;;
    dashboard-refresh)         echo 1500 ;;
    security-scan)             echo 1500 ;;
    dependency-security-agent) echo 1500 ;;
    weekly-review)     echo 11520 ;;
    sprint-planning)   echo 11520 ;;
    weekend-ops)       echo 11520 ;;
    performance-agent) echo 11520 ;;
    tech-debt-agent)   echo 11520 ;;
    compliance-agent)  echo 11520 ;;
    access-review-agent) echo 11520 ;;
    architecture-agent)  echo 23040 ;;
    *)                 echo 1500 ;;  # unknown agent: default to daily
  esac
}

# epoch_to_iso <epoch> — portable epoch → ISO-8601 UTC string
epoch_to_iso() {
  local ts="$1"
  # macOS: date -r <epoch>; Linux: date -d @<epoch>
  if date -u -r "$ts" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null; then
    return
  fi
  date -u -d "@${ts}" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "unknown"
}

# Ordered agent list (bash 3.2 compatible — no associative arrays)
AGENTS="dev-agent qa-agent code-review-agent security-agent analytics-agent
        support-agent growth-agent marketing-agent finance-agent nightly-monitor
        content-agent improvement-agent dependency-security-agent
        daily-health-check dashboard-refresh weekend-ops
        performance-agent tech-debt-agent compliance-agent access-review-agent
        architecture-agent weekly-review sprint-planning"

echo "## Agent Health"
echo ""
echo "| Agent | Last Run | Status |"
echo "|-------|----------|--------|"

for agent in $AGENTS; do
  STAMP="${HEALTH_DIR}/${agent}.last-run"
  WINDOW=$(get_window "$agent")

  if [ ! -f "$STAMP" ]; then
    echo "| ${agent} | never | ⚠️ WARNING — no heartbeat file found |"
    continue
  fi

  LAST=$(cat "$STAMP" 2>/dev/null || echo "0")

  # Guard against non-numeric or empty content
  case "$LAST" in
    ''|*[!0-9]*)
      echo "| ${agent} | invalid timestamp | ⚠️ WARNING — corrupt heartbeat file |"
      continue
      ;;
  esac

  ELAPSED_MIN=$(( (NOW - LAST) / 60 ))
  THRESHOLD_WARN=$(( WINDOW + WINDOW / 5 ))  # window + 20%
  THRESHOLD_CRIT=$(( WINDOW * 2 ))           # 2× window

  LAST_TS=$(epoch_to_iso "$LAST")

  if [ "$ELAPSED_MIN" -le "$THRESHOLD_WARN" ]; then
    echo "| ${agent} | ${LAST_TS} (${ELAPSED_MIN}m ago) | OK |"
  elif [ "$ELAPSED_MIN" -le "$THRESHOLD_CRIT" ]; then
    echo "| ${agent} | ${LAST_TS} (${ELAPSED_MIN}m ago) | WARNING — missed expected window (${WINDOW}m) |"
  else
    echo "| ${agent} | ${LAST_TS} (${ELAPSED_MIN}m ago) | CRITICAL — ${ELAPSED_MIN}m elapsed, 2x window exceeded |"
    HAS_CRITICAL=1
  fi
done

echo ""
if [ "$HAS_CRITICAL" -eq 1 ]; then
  echo "> CRITICAL: One or more agents have exceeded 2x their expected run window."
  echo "> Check .agent-health/ heartbeat files and restart the affected scheduled tasks."
else
  echo "> All scheduled agents are within expected run windows."
fi

exit "$HAS_CRITICAL"
