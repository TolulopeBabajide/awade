# Backlog Format

> How issues are stored, formatted, and maintained in `docs/backlog.md`.
> This is the single source of truth for the format every agent follows when filing or editing an issue.
> Quick reference for filing agents: `.claude/rules/backlog-filing.md`.

---

## File model — single file

All issues live in **one file**: `docs/backlog.md`.

- **Active issues** sit under their severity section — `## 🔴 Critical`, `## 🟠 High`, `## 🟡 Medium`, `## 🟢 Low / Polish`.
- **Completed issues** move to the `## ✅ Done` section in the same file, with `stage=done`.

There is no separate `completed_backlog.md`. The dev log (`docs/sprints/dev-log.md`) is a one-line-per-merge work log — not a backlog file.

---

## Row format — 6 columns, one line per issue

```markdown
| # | Stage | Area | Issue | File(s) | Effort |
|---|-------|------|-------|---------|--------|
| H-04 | ready | Auth | Add password-reset flow with token expiry | `src/pages/Login.tsx` | M |
```

| Column | Rule |
|--------|------|
| **#** | Issue ID — see prefixes below. Never reuse an ID, even one whose issue was closed or abandoned. |
| **Stage** | Exactly one of: `discover`, `define`, `gtm`, `design`, `ready`, `in-progress`, `done`. No other values. |
| **Area** | Short domain label — `Auth`, `Security`, `UX`, `SEO`, `Tooling`, etc. |
| **Issue** | One-line description of what is wrong or needed. Keep it to a single line — detail belongs in a linked spec, not the table. Escape any literal `|` inside backticks as `\|`. |
| **File(s)** | Backtick-wrapped, comma-separated paths. Use `—` when no file applies. |
| **Effort** | `XS` (<2 hr) · `S` (2–4 hr) · `M` (4–8 hr) · `L` (>8 hr). No other values. |

One issue is exactly one row — never split an issue across multiple rows.

---

## ID prefixes and severity

| Prefix | Severity | Meaning |
|--------|----------|---------|
| `C-##` | 🔴 Critical | Broken behaviour, data loss, security risk |
| `H-##` | 🟠 High | Significant functional gap or user-facing failure |
| `M-##` | 🟡 Medium | Degraded experience or subtle correctness issue |
| `L-##` | 🟢 Low | Minor, cosmetic, or edge-case |
| `GRC-##` | 🔵 Compliance | Legal / regulatory finding (filed by the compliance-agent) — note the underlying severity in the Issue cell |

IDs are permanent references in commits, specs, and docs. Never renumber and never reuse.

---

## Lifecycle stages

```
discover → define → gtm → design → ready → in-progress → done
```

The dev agent only picks up items at **`stage=ready`**. Everything earlier is pre-build work. See `CLAUDE.md §Lifecycle Stages` for who advances each stage.

---

## Maintenance rules

**Filing a new issue**

1. Assign the next unused number for the severity prefix. Check the active sections **and** `## ✅ Done` — never reuse a historical ID.
2. Write a one-line Issue description. Default `Stage` to `discover`; an agent may file at `ready` when the fix is already clear and actionable.
3. Estimate Effort and list the affected File(s).
4. Add the row under the matching severity section.

**Editing an issue** — change Stage, Effort, Issue text, or File(s). Never change the ID. If scope grows fundamentally, split it into a new issue rather than rewriting the row.

**Completing an issue** — move the row to `## ✅ Done`, set `stage=done`, and append a line to `docs/sprints/dev-log.md`:

```
date | issue-id | title | commit-hash | CI status
```

---

## Validation

`scripts/check-backlog-format.py` validates the active severity sections of `docs/backlog.md` — column count, valid Stage and Effort values, valid ID prefixes, non-empty Issue cells, and duplicate-ID detection. The `## ✅ Done` section is an append-only archive and is not strictly validated. Run the check before committing any backlog change:

```bash
python3 scripts/check-backlog-format.py
```

Exit 0 = valid · exit 1 = problems found (printed with line numbers).
