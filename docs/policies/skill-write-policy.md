# Policy: Writing to .claude/skills/ (SKILL.md Files)

> **Status**: Active  
> **Decided**: 2026-04-27  
> **Decided by**: Founder (Tolu)  
> **Resolves**: H-06  

---

## Decision

Agents **may write to `.claude/skills/`** using **bash or Python** as the write mechanism.

The Cowork file tools (`Edit`/`Write`) cannot write to `.claude/skills/` due to a Cowork runtime restriction. This is a tooling constraint, not a security boundary. The restriction does not apply to shell commands executed via the workspace bash tool.

**Approved write method**: Use `python3` or `bash` to read and modify SKILL.md files directly, as documented in `.claude/rules/workflow.md §Editing SKILL.md Files`.

---

## Rationale

- The `.claude/skills/` directory contains agent skill definitions, not secrets or production code.
- Agents self-improving their own skill files is a core feature of the template — blocking it defeats the purpose of the improvement-agent.
- The bash write method was validated on 2026-04-26 as part of IMP-08: all 26 SKILL.md files were successfully updated via `python3` with `## Permission Check` sections. No unintended side effects observed.
- The `improvement-agent` already has `.claude/skills/` listed in its `write` paths in `agent-permissions.json` — the permission manifest was always correct.

---

## Who May Write to .claude/skills/

Only agents explicitly listed in `agent-permissions.json` with `.claude/skills/` in their `write` array. As of this policy:

| Agent | May write to .claude/skills/ | Purpose |
|-------|------------------------------|---------|
| `improvement-agent` | ✅ Yes | Self-improvement — adding infrastructure sections to SKILL.md files |

All other agents: **No**. If another agent needs to modify a skill file, it should file a backlog item for the improvement-agent to action.

---

## How to Write (Standard Method)

```python
# Read-modify-write pattern (safe for multi-line insertions)
python3 -c "
content = open('.claude/skills/<agent>/SKILL.md').read()
content = content.replace('OLD_SECTION', 'NEW_SECTION')
open('.claude/skills/<agent>/SKILL.md', 'w').write(content)
"
```

For appending a new section:
```bash
cat >> .claude/skills/<agent>/SKILL.md << 'SECTION'
## New Section
Content here.
SECTION
```

Always verify after writing:
```bash
# Check headings are intact
grep "^##" .claude/skills/<agent>/SKILL.md

# Check code fences are balanced (even count)
grep -c '```' .claude/skills/<agent>/SKILL.md
```

See `.claude/rules/workflow.md §Editing SKILL.md Files` for the full reference.

---

## What This Resolves

| Item | Resolution |
|------|-----------|
| H-06 (Backlog) | Closed — founder confirmed bash write method as official approach |
| IMP-04, IMP-05, IMP-06, IMP-07 (improvement-backlog) | SKILL.md integration deferred items are now unblocked; use bash method going forward |
| H-04 (sanitize-input.sh wiring) | Unblocked — improvement-agent can now directly update the four target skills |
| M-04 (validate-output.sh wiring) | Unblocked — same as H-04 |
| M-05 (circuit-breaker.sh wiring) | Unblocked — same as H-04 |

---

## Audit Trail

| Date | Agent | Action |
|------|-------|--------|
| 2026-04-26 | improvement-agent | First confirmed bash write to `.claude/skills/` — IMP-08, 26 SKILL.md files updated |
| 2026-04-27 | sprint-planning | Noted H-06 as founder decision pending in sprint-2026-04-27.md |
| 2026-04-27 | founder (Tolu) | Confirmed: bash write method is the official approach — H-06 closed |
