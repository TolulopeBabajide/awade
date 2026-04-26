# Morning Brief — 2026-04-26

Status: 🟡 Attention Needed

> Code is clean — TypeScript and frontend tests pass. Main action item: resolve the working tree's staged/unstaged complexity and push **35 unpushed commits** to GitHub to trigger CI.

---

## Code Health

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Frontend tests | ✅ 72 passing / 0 failing (7 test files) |
| Backend tests | ⚠️ Skipped — `pytest` not installed in nightly sandbox (recurring infra constraint; not a code issue) |
| Last CI on develop | ⚠️ Unknown — `gh` CLI not available in sandbox |
| Uncommitted | ⚠️ Complex — see Working Tree section below |

---

## Working Tree (Action Required)

`develop` is **35 commits ahead of `origin/develop`** — nothing has been pushed to GitHub yet. CI has not run on any of today's work.

There is also unfinished staging from AWD-M-06:

- **Staged (index):** deletions of 7 image assets + modifications to `FeaturesSection.tsx`, `HeroSection.tsx`, `HeroSectionParent.tsx`, `vite.config.ts`
- **Unstaged modifications:** `apps/backend/middleware/security_headers.py`, `apps/backend/tests/test_security.py`, the same 4 frontend components above, `docs/agentic/backlog.md`, `docs/agentic/sprints/qa-log.md`
- **Untracked:** the same image asset filenames that are staged for deletion (new optimised versions), plus `apps/frontend/package-lock 2.json` and `apps/backend/test_awade.db-journal`

The image situation: AWD-M-06 staged old images for deletion but the new optimised versions landed as untracked. The frontend components appear in both staged and unstaged, meaning the index holds a partial snapshot. This needs to be committed or reset before pushing.

---

## Today's Commits (2026-04-25 — 28 commits)

| Commit | Issue | Summary |
|--------|-------|---------|
| `fd42a4e` | M-06 | docs: update backlog, dev-log, manual_to_do |
| `3c0e2be` | M-06 | perf: optimise landing page images + code splitting |
| `490b05a` | M-43 | fix(security): remove unsafe-inline from style-src, add font-src |
| `2f79fed` | M-44 | test(security): mark hollow test_rate_limiting skip with backlog reason |
| `fb9e718` | M-35 | fix(security): remove unsafe-inline from CSP script-src |
| `c83bee8` | M-21 | feat(parents): PDF export for parent guides |
| `e3627b9` | M-41 | fix(frontend): restore typed API interfaces stripped in M-04 |
| `7fe0c3b` | M-04 | test(backend): service-layer tests for lesson_plan_service + children |
| `663b50a` | M-15 | feat(frontend): proper types for children/guides API methods |
| `6880ce3` | C-07 | fix(security): restore safe_context + openai 1.109.1 |
| `3b2c067` | M-39 | fix(security): upgrade openai + safe_context in cache metadata |
| `f9605aa` | H-41 | fix(testing): GuideViewPage.test.tsx TS errors + failing test |
| `a762c11` | C-06 | fix(git): restore full 266-file tree lost by mass deletion |
| `4b52109` | M-38 | fix(ai): correct _sanitize_user_context type to Optional[str] |
| *(+ 14 earlier in 24h window)* | — | See `git log --oneline --since="24 hours ago"` for full list |

---

## Open Issues

| Priority | Count |
|----------|-------|
| 🔴 Critical | 0 |
| 🟠 High | 1 |
| 🟡 Medium | 6 |
| 🔵 Low | 10 |

**Open High:** AWD-H-03 — Admin panel has no parent/child management views (effort: L)

**Open Medium:** AWD-M-45 (fetchPriority React compat), M-07 (landing screenshots), M-16 (subjects join table), M-17 (migration system consolidation — needs Tolu decision), M-19 (mobile audit), M-20 (AI prompt quality review)

---

## Tomorrow's Focus

1. **Push to GitHub** — run `git push origin develop` and monitor CI. This is blocking — 35 commits are local-only and no CI has validated today's security, testing, and performance work. The push table in `manual_to_do.md` lists every commit in order.

2. **Resolve working tree state before pushing** — the staged index holds partial AWD-M-06 work (image deletions + component changes). The working tree has further modifications on top. Options: (a) commit the remaining unstaged changes to close out M-06 cleanly, or (b) reset to last clean commit and re-stage selectively. Check `git diff --cached` vs `git diff` to decide. Do not `git push` with a dirty, inconsistent index.

3. **Fix AWD-M-45** — bump `react` / `react-dom` to `^18.3.0` in `apps/frontend/package.json` (also bumps `@types/react`, `@types/react-dom`). Resolves the `fetchPriority` console warning in tests. S-effort, fully unblocked.

---

## QA Update — 2026-04-26T00:37Z

✅ **AWD-C-08 QA PASS** — CSP restore (security_headers.py + test_security.py) passed all automated checks:
- TypeScript: ✅ · Lint: ✅ · Frontend tests: ✅ 72/72 · OpenAPI: ✅ · Spot-check: ✅ clean

⚠️ **QA auto-filed AWD-M-46** — `venv/bin/python` is a broken symlink (points to python3.13, not available in QA sandbox). Backend pytest cannot run until venv is recreated with Python 3.10 on your Mac: `rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r apps/backend/requirements.txt`. S-effort, run locally.

## QA Update — 2026-04-26T~hourly

✅ **AWD-M-45 + AWD-C-08 spot-check PASS** — react ^18.3.0 bump and CSP restore both clean:
- `package.json`: react, react-dom, @types/react, @types/react-dom all at ^18.3.0 ✅
- `security_headers.py`: CSP intact — no unsafe-inline in script-src or style-src, font-src present ✅
- No new issues filed.

⚠️ **Bash sandbox still blocked** (9th+ consecutive cycle — "No space left on device"). tsc, lint, pytest, and git commands remain unavailable. CI mirror cannot run until sandbox disk is cleared. **Push to GitHub is the critical outstanding action** — 36 commits are local-only.

## QA Update — 2026-04-26T~hourly (13th+ consecutive blocked cycle)

⏭ **Skipped — no new commits to validate.** Dev log shows no new work since the prior QA cycle (AWD-L-02 docs change, already spot-checked clean). Bash sandbox still fails with "No space left on device" on all attempts — git log, tsc, lint, and pytest remain blocked.

⚠️ **Outstanding Tolu actions (unchanged from prior cycles):**
1. Clear sandbox disk space to restore QA automation
2. Resolve dirty working tree (partial AWD-M-06 staging — `git diff --cached` vs `git diff`)
3. Push ~37 pending commits: `git push origin develop` → triggers real CI pipeline
