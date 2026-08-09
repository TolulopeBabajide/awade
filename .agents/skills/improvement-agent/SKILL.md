---
name: improvement-agent
description: "Improvement Agent: Reads docs/agentic/improvement-backlog.md, implements the top ready item, self-tests, and marks it done. Scheduled every 3 hours. Also trigger on demand: 'run the improvement agent', 'implement next system improvement', 'implement IMP-##'."
---

# Improvement Agent

## Permission Check

Before writing to any file, verify the target path is in your allowed write list in `agent-permissions.json`.

```bash
./scripts/check-permissions.sh "improvement-agent" "<target-file>"
```

- **Exit 0** → write permitted. Proceed.
- **Exit 1** → write denied. Log and stop:

```bash
./scripts/audit-log.sh "improvement-agent" "PERMISSION_DENIED" "<target-file>" "write denied by permission manifest"
```

- **Exit 2** → manifest missing or agent not listed. Treat as denied — log and stop.

---
## Idempotency Check — Run This First

Before doing anything else, check whether this agent ran too recently:

```bash
./scripts/idempotency-check.sh "improvement-agent" 170
```

- **Exit 0** → safe to proceed. Continue to the next section.
- **Exit 1** → ran within the 170-minute window. Log the skip and stop:

```bash
./scripts/audit-log.sh "improvement-agent" "SKIP" "idempotency" "ran within 170-minute window — skipping"
```

Do not proceed with any further steps if the idempotency check returns 1.

---

## Purpose
The system builds itself. This agent reads `docs/agentic/improvement-backlog.md`, selects the
highest-priority ready item, implements it, self-tests, and marks it done — cycling every
3 hours. Over time the system becomes more robust, secure, and capable without manual intervention.

## When to run
- **Scheduled**: Every 3 hours (`0 */3 * * *`)
- **On demand**: "Run the improvement agent" or "Implement next system improvement" or "Implement IMP-##"

## Before starting
1. Read `project-config.md`
2. Read `docs/agentic/improvement-backlog.md` in full
3. Read `.Codex/rules/workflow.md`
4. Read `docs/agentic/backlog.md` — needed to sync cross-referenced issues and to file H-## blockers

## Process

### Step 1 — Select the item
Find the highest-priority item where:
- `Stage = ready`
- Phase gate is open (all Phase 1 items done before starting Phase 2; IMP-14 has ≥20 entries before Phase 3)

If no items are ready: write a brief status to `docs/agentic/daily-briefs/improvement-report.md` and stop.

### Step 2 — Read the spec completely
For the selected item, read its full specification from the backlog:
- Acceptance criteria (all checkboxes)
- Target files
- What to build
- Test instructions

Mark the item `stage=in-progress` in `docs/agentic/improvement-backlog.md`.

### Step 3 — Read all files you will touch
Before writing a single line, read every target file in full.
For SKILL.md files: understand the existing structure before modifying.
For new scripts: check if a stub already exists in `scripts/`.

### Step 4 — Implement
Write the implementation. Rules:
- Shell scripts: include a usage comment block at the top, handle errors with `set -e` or explicit checks, make executable (`chmod +x`)
- Python scripts: stdlib only unless the item spec says otherwise, include a docstring, handle missing files gracefully
- SKILL.md updates: make minimal targeted changes — add a new section or step, do not rewrite the whole skill
- New files: follow the existing naming conventions in the directory they land in
- Minimal scope: implement exactly what the spec says, nothing more

### Step 5 — Self-test
For every file you produced or modified:

**Shell scripts**:
```bash
bash -n scripts/<script>.sh          # syntax check
./scripts/<script>.sh --help 2>&1 || true  # smoke test
```

**Python scripts**:
```bash
python3 -m py_compile scripts/<script>.py  # syntax check
python3 scripts/<script>.py --help 2>&1 || true
```

**SKILL.md edits**:
- Verify markdown structure is intact (headings, code blocks balanced)
- Verify no existing sections were accidentally removed

**Run the item's test** if one is specified in the spec.

### Step 6 — Check Phase 1 gate (if completing Phase 1)
After marking any Phase 1 item done, count remaining Phase 1 items at `stage=ready` or `stage=in-progress`.
If count = 0: update all Phase 2 items from `blocked` to `ready` in `docs/agentic/improvement-backlog.md`.

### Step 7 — Update backlog
In `docs/agentic/improvement-backlog.md`:
- Change `Stage` from `in-progress` to `done` in the summary table
- Check all acceptance criteria checkboxes that were met
- Move item to `## Done` table with: date, what was implemented, any deviations from spec

#### Step 7b — Sync cross-references to `docs/agentic/backlog.md`
If the completed item has a **Routes** field (e.g. `Routes: H-04` or `Routes: M-04, L-02`):
1. Open `docs/agentic/backlog.md`
2. Find each originating issue by ID in the backlog table rows
3. Move each matching issue from its current section to `## ✅ Done`
4. Append ` — closed by [IMP-##] [YYYY-MM-DD]` to the issue title line so the link is traceable
5. Log the sync:
```bash
./scripts/audit-log.sh improvement-agent WRITE docs/agentic/backlog.md "synced [ISSUE-ID] to Done (completed via [IMP-##])"
```
Skip this sub-step entirely if the completed item has no Routes field.

### Step 8 — Write to audit log
```bash
./scripts/audit-log.sh improvement-agent IMPLEMENT <IMP-ID> "<one-line summary>"
```
If `scripts/audit-log.sh` doesn't exist yet (IMP-01 not done): append directly to `docs/agent-audit.log`.

### Step 9 — Write improvement report
Append to `docs/agentic/daily-briefs/improvement-report.md`:
```
## [DATE] — [IMP-##] [Item title]
**Implemented**: [what was built]
**Files changed**: [list]
**Self-test**: [passed / failed — details]
**Next item**: [IMP-## title] (stage=ready)
**Phase gate**: Phase [1|2|3] — [N] items remaining
```

### Step 10 — Write heartbeat
```bash
date +%s > .agent-health/improvement-agent.last-run
```

## Phase Gate Rules

| Phase | Unlocks when |
|-------|-------------|
| Phase 2 | All 8 Phase 1 items at stage=done |
| Phase 3 (IMP-14) | Phase 2 IMP-09 done (ready to log feedback) |
| Phase 3 (IMP-15+) | `docs/agentic/feedback-log.md` has ≥20 entries |
| Phase 3 (IMP-16+) | `docs/agentic/feedback-log.md` has ≥50 entries |

## Hard Rules
- Never skip an item's test step, even if the implementation looks obviously correct
- Never implement more than one item per run — one item, done fully, is better than two items done partially
- Never modify application source code — only `scripts/`, `.Codex/skills/`, `docs/`, config files at repo root
- If a spec is ambiguous, implement the most conservative interpretation and note the ambiguity in the improvement report
- If an implementation fails self-test: revert the changes, mark the item `stage=ready` again, document what failed in the report
- If implementing a SKILL.md update would break that agent's current workflow: file an `H-##` in `docs/agentic/backlog.md` before proceeding
- Call `./scripts/audit-log.sh` (or direct append) on every run — even failed runs

## Output Validation
After writing any file under `docs/`, immediately call:
```bash
./scripts/validate-output.sh "improvement-agent" "<output-file>"
```
- **Exit 0** → validation passed. Continue.
- **Exit non-0** → validation failed. Do NOT advance the backlog item. The script auto-files a `C-##` row in `docs/agentic/backlog.md`. Log the failure and stop.

## Audit Log
As your **final step on every run** — including runs that skip, fail, or partially complete —
call the audit logger so every action is traceable:

```bash
./scripts/audit-log.sh "improvement-agent" "IMPLEMENT" "docs/agentic/improvement-backlog.md" "implemented improvement item"
```

If `scripts/audit-log.sh` does not yet exist, append directly:
```bash
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | improvement-agent | IMPLEMENT | docs/agentic/improvement-backlog.md | implemented improvement item" >> docs/agent-audit.log
```

Write your heartbeat last:
```bash
date +%s > .agent-health/improvement-agent.last-run
```
