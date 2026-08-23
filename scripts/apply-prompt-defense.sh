#!/usr/bin/env bash
# apply-prompt-defense.sh — inline the canonical Prompt Defense Baseline into
# every agent's SKILL.md, idempotently.
#
# Source of truth: .claude/rules/prompt-defense-baseline.md (block between the
#   <!-- ECC-PROMPT-DEFENSE:BEGIN --> / :END --> markers).
# Target:          .claude/skills/<agent>/SKILL.md (block inserted right after
#   the YAML frontmatter).
#
# Usage:
#   ./scripts/apply-prompt-defense.sh            # --check (default): report only, no writes
#   ./scripts/apply-prompt-defense.sh --check
#   ./scripts/apply-prompt-defense.sh --apply    # insert/update the block in every SKILL.md
#
# Exit codes:
#   --check:  0 = every skill already carries the current block
#             1 = one or more skills are missing or have a stale block
#   --apply:  0 = success (all skills now carry the current block)
#             1 = error (canonical block not found, etc.)
#
# Idempotent: running --apply repeatedly is a no-op once skills are current.
# Editing SKILL.md via this script is the sanctioned method (the Cowork file
# tools cannot write under .claude/; see .claude/rules/workflow.md).
set -euo pipefail

MODE="${1:---check}"
case "$MODE" in
  --check|--apply) ;;
  *) echo "Usage: $0 [--check|--apply]" >&2; exit 1 ;;
esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CANON="$ROOT/.claude/rules/prompt-defense-baseline.md"
SKILLS_DIR="$ROOT/.claude/skills"

python3 - "$MODE" "$CANON" "$SKILLS_DIR" <<'PY'
import sys, os, re, glob

mode, canon_path, skills_dir = sys.argv[1], sys.argv[2], sys.argv[3]
BEGIN = "<!-- ECC-PROMPT-DEFENSE:BEGIN -->"
END   = "<!-- ECC-PROMPT-DEFENSE:END -->"

# --- read canonical block (markers included) ---
try:
    canon = open(canon_path, encoding="utf-8").read()
except FileNotFoundError:
    print(f"✗ canonical file not found: {canon_path}", file=sys.stderr); sys.exit(1)
if BEGIN not in canon or END not in canon:
    print("✗ canonical file is missing the BEGIN/END markers", file=sys.stderr); sys.exit(1)
block = canon[canon.index(BEGIN): canon.index(END) + len(END)].strip()

def frontmatter_end(text):
    """Return index just after the closing '---' of YAML frontmatter, or 0."""
    if not text.startswith("---"):
        return 0
    m = re.search(r"\n---[ \t]*\n", text)
    return m.end() if m else 0

skills = sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md")))
missing, stale, current, changed = [], [], [], []

for path in skills:
    name = os.path.basename(os.path.dirname(path))
    text = open(path, encoding="utf-8").read()
    has = BEGIN in text and END in text
    existing = ""
    if has:
        existing = text[text.index(BEGIN): text.index(END) + len(END)].strip()

    if has and existing == block:
        current.append(name); continue
    (stale if has else missing).append(name)

    if mode == "--apply":
        if has:
            new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                         lambda _: block, text, count=1, flags=re.S)
        else:
            i = frontmatter_end(text)
            new = text[:i] + ("\n" if i else "") + block + "\n\n" + text[i:]
        open(path, "w", encoding="utf-8").write(new)
        changed.append(name)

total = len(skills)
if mode == "--check":
    print(f"Prompt Defense Baseline — check across {total} skill(s)")
    print(f"  current: {len(current)}   missing: {len(missing)}   stale: {len(stale)}")
    if missing: print("  MISSING : " + ", ".join(missing))
    if stale:   print("  STALE   : " + ", ".join(stale))
    if missing or stale:
        print("\nRun: ./scripts/apply-prompt-defense.sh --apply")
        sys.exit(1)
    print("✓ every skill carries the current Prompt Defense Baseline")
    sys.exit(0)
else:
    print(f"Prompt Defense Baseline — applied across {total} skill(s)")
    print(f"  updated: {len(changed)}   already-current: {len(current)}")
    if changed: print("  changed: " + ", ".join(changed))
    sys.exit(0)
PY
