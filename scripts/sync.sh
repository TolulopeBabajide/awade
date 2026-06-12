#!/usr/bin/env bash
# sync.sh — keep the project in sync with GitHub.
#
# The agentic team runs across two runtimes (Claude Code and Cowork) and may span several
# machines and people. GitHub is the shared source of truth, reached through a single git
# gateway: the dev-agent. It is the only agent that runs git. Every other agent reads the
# working tree (kept current by the dev-agent) and writes output — it never runs git, because
# a pull would fail while other agents' output sits uncommitted in the tree.
# See CLAUDE.md §Sync Protocol.
#
# Usage (dev-agent only):
#   ./scripts/sync.sh push "<commit message>" <path> [<path> ...]
#       Stage the named paths, commit, pull --rebase, and push to the integration branch.
#       If there is nothing to commit it still pulls --rebase, so the tree always ends
#       current. Retries the push once if it is rejected. On push failure the commit is kept
#       locally and a PUSH_DEFERRED line is written to .agent-health/sync-failures.log.
#
#   ./scripts/sync.sh pull
#       Check out the integration branch and pull --rebase. Provided for manual/on-demand use;
#       in normal operation the dev-agent syncs via `push`.
#
# The integration branch is read from project-config.md (INTEGRATION_BRANCH:); if that is
# not found it falls back to the current branch.
#
# Exit codes: 0 = ok, 1 = usage/precondition error, 2 = push deferred (commit kept locally).
set -u

log_fail() {
  mkdir -p .agent-health
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $1" >> .agent-health/sync-failures.log
}

integration_branch() {
  local b
  b=$(grep -oE 'INTEGRATION_BRANCH:[[:space:]]*[^[:space:]]+' project-config.md 2>/dev/null \
        | awk '{print $2}' | head -1)
  if [ -n "${b:-}" ]; then
    echo "$b"
  else
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main"
  fi
}

cmd=${1:-}
BR=$(integration_branch)

case "$cmd" in
  pull)
    git checkout "$BR" 2>/dev/null || { echo "sync: cannot check out $BR"; exit 1; }
    if git pull --rebase 2>/dev/null; then
      echo "sync: pulled $BR — tree is current"
    else
      log_fail "PULL_FAILED | $BR"
      echo "sync: pull failed — continuing on local $BR (logged to sync-failures.log)"
    fi
    ;;

  push)
    msg=${2:-}
    if [ -z "$msg" ]; then
      echo "sync: push needs a commit message"; exit 1
    fi
    shift 2
    if [ "$#" -eq 0 ]; then
      echo "sync: push needs at least one path (stage specific paths — never git add -A)"; exit 1
    fi
    for _p in "$@"; do
      if git check-ignore -q -- "$_p" 2>/dev/null; then
        echo "sync: skipping gitignored path: $_p"
      else
        git add -- "$_p" || { echo "sync: git add failed for $_p"; exit 1; }
      fi
    done

    if git diff --cached --quiet; then
      # Nothing to commit — still sync down so the tree starts current.
      if git pull --rebase 2>/dev/null; then
        echo "sync: nothing to commit — pulled $BR"
      else
        log_fail "PULL_FAILED | $BR"
        echo "sync: nothing to commit — pull failed (logged to sync-failures.log)"
      fi
      exit 0
    fi

    git commit -m "$msg" || { echo "sync: commit failed"; exit 1; }
    git pull --rebase 2>/dev/null || log_fail "PULL_REBASE_FAILED | $BR"
    if git push origin "$BR" 2>/dev/null; then
      echo "sync: committed and pushed $BR"
    else
      git pull --rebase 2>/dev/null || true
      if git push origin "$BR" 2>/dev/null; then
        echo "sync: committed and pushed $BR (after retry)"
      else
        log_fail "PUSH_DEFERRED | $BR | $msg"
        echo "sync: push failed — commit kept locally, logged to .agent-health/sync-failures.log"
        exit 2
      fi
    fi
    ;;

  *)
    echo "usage: sync.sh push \"<message>\" <path> [<path> ...]   (dev-agent — commit + sync)"
    echo "       sync.sh pull                                     (manual pull)"
    exit 1
    ;;
esac
