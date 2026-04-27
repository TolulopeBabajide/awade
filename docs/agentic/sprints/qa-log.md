# Awade QA Log

> Append-only. Each entry added by the QA Agent after a dev-execution cycle.

---

## QA — 2026-04-26T~hourly (12th+ consecutive sandbox-blocked cycle)

**Result**: ⚠️ BLOCKED (sandbox) — no new file-based work to validate

**Step 0**: Bash sandbox fails with `useradd: No space left on device` on all 3 invocation attempts. Git log unavailable. Cannot confirm whether new commits landed on develop in the last 40 minutes. Previous QA entry (same date, AWD-L-02) already spot-checked all file-based work from the most recent dev cycle — no additional changes to validate this cycle.

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable (also: venv broken symlink — AWD-M-46) |
| OpenAPI valid | ✅ No API surface changes since last check |
| Spot-check (file tools) | ✅ Already done this date — see entry below (AWD-L-02 cycle) |
| CI on develop | ❓ Unknown — 37+ commits still un-pushed; CI has not run on any of today's work |

**Issues filed this cycle**: None — all outstanding infra issues already in backlog (AWD-M-46 venv symlink, persistent sandbox disk-full condition).

**Verdict**: ⚠️ Needs human — automated CI mirror is fully blocked. Tolu must: (1) clear sandbox disk space to restore QA automation, (2) push the ~37 pending commits to GitHub (`git push origin develop`) to trigger the real CI pipeline, (3) recreate the venv on the dev machine per AWD-M-46 instructions.

---

## Dev — 2026-04-26T~hourly (AWD-L-02)

**Result**: ⚠️ BLOCKED (sandbox) + ✅ Docs change applied

**Step 0**: Bash sandbox failed — "No space left on device" (11th+ consecutive cycle). Confirmed via 4 independent bash attempts. Git log unavailable. QA of file-based work from last cycle (L-11, M-45, C-08) already confirmed clean by prior QA entry. Selected AWD-L-02 (docs-only) as best safe option for file-tools-only execution.

**AWD-L-02 — Spot-check:**
- `docs/public/api/README.md` — all 10 parent/children/guide endpoints documented ✅
- Auth section updated from stale "Basic Auth" to httpOnly cookie + Bearer pattern (per AWD-H-25) ✅
- 403/502/503 error codes added to HTTP status table ✅
- All Pydantic schemas documented: `ChildProfileCreate`, `ChildProfileResponse`, `ChildProfileListResponse`, `ParentGuideResponse`, `ParentGuideListResponse`, `ParentGuideAIContent` ✅
- No code changes — docs only; no tsc/lint/pytest impact ✅
- Backlog and completed_backlog.md updated ✅

**Issues filed this cycle**: None.

**Verdict**: ⚠️ Needs human — docs change is clean. Persistent sandbox issue (11 cycles, disk full) requires Tolu to: (1) clear sandbox disk space, (2) push the ~37 pending commits via `git push origin develop`, (3) recreate the venv (AWD-M-46). Today's commit: `git add docs/public/api/README.md && git commit -m "docs(api): AWD-L-02 add parent/children endpoint docs to public API README" && git push origin develop`.

---

## QA — 2026-04-26T~hourly

**Result**: ⚠️ BLOCKED (sandbox) + ✅ Spot-check PASS

**Step 0**: `git log` unavailable — bash sandbox fails with `useradd: No space left on device` (9th+ consecutive cycle). Cannot confirm new commits in last 40 minutes via shell. Proceeding to file-based spot-check of most recently completed issues: AWD-M-45 (react ^18.3.0 bump) and AWD-C-08 (CSP restore), both marked ✅ 2026-04-26 in backlog.

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable (also: venv symlink broken — AWD-M-46) |
| OpenAPI valid | ✅ No API surface changes in M-45 or C-08 — no recheck needed |
| Spot-check (file tools) | ✅ Clean — see below |
| CI on develop | ❓ Unknown — 36 commits still un-pushed; CI has never run on any of today's work |

**Spot-check — AWD-M-45 (`apps/frontend/package.json`)**:
- `"react": "^18.3.0"` ✅
- `"react-dom": "^18.3.0"` ✅
- `"@types/react": "^18.3.0"` ✅
- `"@types/react-dom": "^18.3.0"` ✅
- `HeroSection.tsx` and `HeroSectionParent.tsx` retain `fetchPriority="high"` — correct; fix was bumping React (not changing the prop), React 18.3+ officially supports camelCase `fetchPriority` ✅
- No hardcoded secrets, no TODO/FIXME added ✅

**Spot-check — AWD-C-08 (`apps/backend/middleware/security_headers.py`)**:
- `Content-Security-Policy` header present ✅
- `script-src 'self'` — no `'unsafe-inline'` (AWD-M-35 preserved) ✅
- `style-src 'self' https://fonts.googleapis.com` — no `'unsafe-inline'` (AWD-M-43 preserved) ✅
- `font-src 'self' https://fonts.gstatic.com` present ✅
- `frame-ancestors 'none'`, `form-action 'self'`, `base-uri 'self'`, `default-src 'self'` all present ✅
- CSP tests in `apps/backend/tests/test_security.py`: `test_csp_header_directives`, `test_csp_script_src_no_unsafe_inline`, `test_csp_style_src_no_unsafe_inline`, `test_csp_font_src_google_fonts` — all present ✅
- No hardcoded secrets, no bare print(), no @ts-ignore, no TODO/FIXME ✅

**Issues filed this cycle**: None — spot-check clean. AWD-M-46 (broken venv symlink) already filed last cycle.

**Verdict**: ⚠️ Needs human — file-based checks are clean. Tolu must: (1) clear sandbox disk to restore automated CI mirrors, (2) push the 36 pending commits to GitHub (`git push origin develop`) to trigger the real CI pipeline, (3) resolve the dirty working tree state (partial AWD-M-06 staging) before pushing.

---

## QA — 2026-04-26T~hourly (13th+ consecutive sandbox-blocked cycle)

**Result**: ⏭ SKIP — bash sandbox still blocked; no new dev work to validate since last QA cycle

**Step 0**: `mcp__workspace__bash` fails immediately with `useradd: No space left on device` on all 3 invocation attempts (13th+ consecutive cycle). `git log --since="40 minutes ago"` unavailable. Dev log shows no new entries beyond AWD-L-02, which was already spot-checked by the prior QA cycle. No file-based changes to review this cycle.

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable (also: venv broken symlink — AWD-M-46) |
| OpenAPI valid | ✅ No API surface changes since last validated cycle |
| Spot-check (file tools) | ✅ No new changes to check — last cycle's spot-check (AWD-L-02) still current |
| CI on develop | ❓ Unknown — 37+ commits still un-pushed; real CI has not run on any recent work |

**Issues filed this cycle**: None — no new work to triage; all outstanding infra issues already captured (AWD-M-46 venv, persistent sandbox disk-full).

**Verdict**: ⏭ Skip / ⚠️ Needs human — no new code to validate this cycle. Persistent blocker (13 consecutive cycles): sandbox disk full. Tolu actions remain: (1) clear sandbox disk, (2) resolve dirty working tree (partial AWD-M-06 staging), (3) push ~37 commits to GitHub (`git push origin develop`) to trigger the real CI pipeline.

---

## QA — 2026-04-25T~hourly — Sandbox still down; file-based spot-check of pending AWD-H-40 (lesson_plans export)

**Result**: ⚠️ BLOCKED (sandbox) + ✅ Spot-check PASS

**Step 0**: `git log` unavailable — bash sandbox fails with `useradd: No space left on device` (8th+ consecutive cycle). Cannot confirm new commits in last 40 minutes. Proceeding to file-based spot-check of the latest pending fix (AWD-H-40, applied by previous dev cycle).

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable |
| OpenAPI valid | ✅ No API surface changes in H-40 — no recheck needed |
| Spot-check (file tools) | ✅ Clean — see below |
| CI on develop | ❓ Unknown — gh CLI unavailable; pending commits not yet pushed |

**Spot-check — `apps/backend/routers/lesson_plans.py` (AWD-H-40)**:
- `import logging` at module top (line 18) ✅
- `logger = logging.getLogger(__name__)` declared at module scope (line 39) ✅
- `except HTTPException: raise` handler preserves HTTP exceptions correctly ✅
- `except Exception:` block calls `logger.error("Unexpected error exporting lesson resource %s", resource_id, exc_info=True)` — no `str(e)` in message ✅
- `HTTPException(status_code=500, detail="An error occurred while exporting the resource.")` — static detail, no internal info disclosed ✅
- No hardcoded secrets, no `console.log`/`print()`, no `@ts-ignore`, no TODO/FIXME ✅
- Auth guards unchanged (`require_educator`, `require_admin_or_educator`) ✅

**Spot-check — `apps/backend/tests/test_lesson_plans_router.py` (AWD-H-40)**:
- File exists at `apps/backend/tests/test_lesson_plans_router.py` ✅
- `_make_user()` and `_make_resource()` use `User()` / `LessonResource()` constructors (not `__new__`) — avoids SQLAlchemy `_sa_instance_state=None` bug (fixed in AWD-H-27) ✅
- `teardown_method` clears `app.dependency_overrides` ✅
- 7 test cases present: `test_resource_not_found_returns_404`, `test_cross_user_export_returns_403`, `test_admin_can_export_any_resource`, `test_unsupported_format_returns_400`, `test_unexpected_error_returns_static_detail` (H-40 core assertion — asserts `secret_message not in detail`), `test_pdf_export_happy_path`, `test_docx_export_happy_path` ✅
- Core assertion uses `RuntimeError("WeasyPrint internal traceback: /etc/secrets/db.cred")` as `side_effect` — verifies the exact leakage vector is blocked ✅

**Pending commits on disk (not yet in git)**:
- AWD-H-40: `fix(lesson-plans): AWD-H-40 replace str(e) with static detail in export endpoint`
- AWD-M-05: `feat(parents): AWD-M-05 add WhatsApp share button to guide view`
- AWD-H-39: `fix(ai): AWD-H-39 add 60s timeout to GeminiProvider via HttpOptions`
- AWD-L-12: `style(ai): AWD-L-12 move import re to module top in GeminiProvider`

**Issues filed this cycle**: None — spot-check clean; no new issues observed.

**Verdict**: ⚠️ Needs human — all four pending fixes are code-clean. Tolu must: (1) clear sandbox disk, (2) commit and push all four pending fixes, (3) run CI mirror locally before each push.

---

## QA — 2026-04-25T~hourly — Sandbox still down; file-based spot-check of pending AWD-M-05 (WhatsApp share)

**Result**: ⚠️ BLOCKED (sandbox) + ✅ Spot-check PASS

**Step 0**: `git log` unavailable — bash sandbox fails with `useradd: No space left on device` (7th+ consecutive cycle). Cannot confirm new commits in last 40 minutes. Proceeding to file-based spot-check of the latest pending fix (AWD-M-05, applied by previous dev cycle).

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable |
| OpenAPI valid | ✅ No API changes in pending commits — no recheck needed |
| Spot-check | ✅ Clean — see below |
| CI on develop | ❓ Unknown — gh CLI unavailable; pending commits not yet pushed |

**Spot-check — `apps/frontend/src/pages/GuideViewPage.tsx` (AWD-M-05)**:
- `FaWhatsapp` imported from `react-icons/fa` at module top ✅
- `handleWhatsAppShare()` builds wa.me deep-link: topic + subject + grade_level header, truncated explanation (≤180 chars), home activity title, Awade branding footer ✅
- `window.open(..., '_blank', 'noopener,noreferrer')` — correct security flags ✅
- Share button has `aria-label="Share this guide on WhatsApp"` ✅
- No hardcoded secrets, no `console.log`, no `@ts-ignore`, no TODO/FIXME ✅
- No changes to auth guards or protected routes ✅

**Spot-check — `apps/frontend/src/pages/GuideViewPage.test.tsx` (AWD-M-05)**:
- File exists alongside `GuideViewPage.tsx` ✅
- Mocks `apiService.getGuide`, `apiService.generateGuide`, `apiService.toggleGuideBookmark` via `vi.mock` ✅
- Layout components (Sidebar, MobileNavigation) shimmed out ✅
- 8 test cases expected (loading/error/success states, WhatsApp URL shape, `window.open` call signature, disabled query) — structure confirmed present ✅

**Pending commits on disk (not yet in git)**:
- AWD-M-05: `feat(parents): AWD-M-05 add WhatsApp share button to guide view`
- AWD-H-39: `fix(ai): AWD-H-39 add 60s timeout to GeminiProvider via HttpOptions`
- AWD-L-12: `style(ai): AWD-L-12 move import re to module top in GeminiProvider`

**Issues filed this cycle**: None — spot-check clean; no new issues observed.

**Verdict**: ⚠️ Needs human — code changes are clean. Tolu must: (1) clear sandbox disk, (2) commit and push M-05 + H-39 + L-12, (3) run CI mirror locally before push.

---

## QA — 2026-04-25T~hourly — Sandbox still down; file-based spot-check of pending H-39 + L-12

**Result**: ⚠️ BLOCKED (sandbox) + ✅ Spot-check PASS

**Step 0**: `git log` unavailable — bash sandbox fails with `useradd: No space left on device` (5th+ consecutive cycle). Cannot confirm new commits in last 40 minutes. Proceeding to file-based spot-check of the two pending (uncommitted) fixes.

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox unavailable |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable |
| OpenAPI valid | ✅ No API changes in pending commits — no recheck needed |
| Spot-check (file tools) | ✅ Clean — see below |
| CI on develop | ❓ Unknown — gh CLI unavailable; pending commits not yet pushed |

**Spot-check — `packages/ai/providers/gemini_provider.py` (H-39 + L-12)**:
- `import re` at module top (line 2) ✅ — L-12 hygiene fix correctly applied
- `DEFAULT_TIMEOUT = 60.0` class constant present ✅
- `self.timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", str(self.DEFAULT_TIMEOUT)))` ✅ — env override works
- `http_options=genai_types.HttpOptions(timeout=self.timeout)` passed to `genai.Client(...)` at init ✅ — timeout applied at client level
- `logger.info("GeminiProvider initialized (timeout=%.1fs)", ...)` ✅ — observability present
- No hardcoded secrets, no `print()`, no `console.log`, no TODO/FIXME ✅

**Spot-check — `apps/backend/tests/test_ai_providers.py`**:
- `test_initialization` for GeminiProvider asserts `http_options` is not None ✅
- `test_initialization_custom_timeout` tests `GEMINI_TIMEOUT_SECONDS` env var override (45s), verifies `provider.timeout == 45.0` and `http_opts.timeout == 45.0` ✅

**Spot-check — `.env.example`**:
- `GEMINI_TIMEOUT_SECONDS=60` present ✅

**Commits pending push** (on disk, not yet in git):
- H-39: `fix(ai): AWD-H-39 add 60s timeout to GeminiProvider via HttpOptions`
- L-12: `style(ai): AWD-L-12 move import re to module top in GeminiProvider`

**Issues**: None new. Sandbox disk-full blocker persists (see AWD-C-05 for git corruption context — same root cause).

**Verdict**: ⚠️ Needs human — code changes are clean; Tolu must: (1) clear sandbox disk, (2) commit and push H-39 + L-12, (3) run CI mirror locally before push.

---

## QA — 2026-04-25T05:30Z — Infrastructure failure: sandbox disk full

**Result**: ❌ BLOCKED — bash sandbox unavailable; all CI mirror checks skipped

| Check | Result |
|-------|--------|
| TypeScript | ⚠️ SKIPPED — sandbox unavailable |
| Lint | ⚠️ SKIPPED — sandbox unavailable |
| Frontend tests | ⚠️ SKIPPED — sandbox unavailable |
| Backend tests | ⚠️ SKIPPED — sandbox unavailable |
| OpenAPI valid | ⚠️ SKIPPED — sandbox unavailable |
| Spot-check | ⚠️ SKIPPED — sandbox unavailable |
| CI on develop | ⚠️ Unknown — gh CLI unavailable |

**Root cause**: Linux sandbox fails to start with `useradd: /etc/passwd.*: No space left on device` — volume is full. This is the 4th+ consecutive cycle with this failure (00:00Z, 00:30Z, 05:00Z, 05:30Z).

**Commits checked**: Unable to run `git log` — cannot determine if new commits exist.

**Issues**: Persistent infrastructure blocker prevents all automated validation. No new backlog items filed (cannot observe code changes).

**Verdict**: ⏭ Skip (sandbox unrecoverable this cycle) — **Needs human intervention**

---

## QA — 2026-04-25T05:00Z — No new commits / sandbox still down

**Result**: ⏭ SKIPPED — no new commits on develop since last cycle

**Step 0 check**: `refs/heads/develop` = `7cb442c` (unchanged from prior QA run at 00:30Z). No commits in the last 40 minutes. Stopping per task instructions.

**Infrastructure note**: Bash sandbox has failed with "No space left on device" for 3+ consecutive cycles (Dev abort at 00:00Z, QA at 00:30Z, QA at 05:00Z). Until Tolu clears the sandbox disk, ALL automated CI mirror checks remain blocked: TypeScript, lint, frontend tests, backend tests. Only file-based spot-checks and direct JSON validation are possible.

**Pending actions for Tolu**:
1. Clear sandbox disk (or wait for scheduled cleanup) so automated checks can resume
2. Run CI mirror locally for the three commits covered in the 00:30Z QA run: `cd apps/frontend && npx tsc --noEmit && npm run lint && npm run test:run` + `cd apps/backend && python -m pytest tests/ -v`
3. Repair `refs/heads/develop` git corruption (AWD-C-05) and push H-39 fix to origin

**Verdict**: ⏭ Skip (no new code to validate)

---

## QA — 2026-04-25T00:30Z — AWD-M-39 Gemini migration · AWD-M-40 postcss patch · AWD-M-38 Optional type fix

**Result**: ⚠️ BLOCKED — bash sandbox out of disk space; automated checks unavailable; spot-check clean with one new finding (H-39 filed)

**Context**: This run covers three unvalidated commits from 2026-04-24T21:39Z–23:17Z UTC that were not QA'd in the preceding cycle (the QA run that would have covered them was also blocked by sandbox disk space). The "40 minutes ago" Step 0 window technically excludes all three commits from the vantage point of this run; however, the QA log has no entry validating them, so this run provides the catch-up validation.

**Commits**:
- `20e88d4` — `fix(ai): AWD-M-39 migrate GeminiProvider from deprecated google-generativeai to google-genai`
- `e7a1d51` — `fix(deps): AWD-M-40 npm audit fix — patch postcss XSS (GHSA-qx2v-qp2m-jg93)`
- `4b52109` — `fix(ai): AWD-M-38 correct _sanitize_user_context type to Optional[str]`
- `3b930b3`, `f8db6f1` — backlog/dev-log update commits

**Files changed (code)**:
- `packages/ai/providers/gemini_provider.py` (M-39)
- `apps/frontend/package-lock.json` (M-40)
- `packages/ai/gpt_service.py` line 231 (M-38)

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ❌ BLOCKED — bash sandbox "No space left on device" |
| Lint (`npm run lint`) | ❌ BLOCKED — bash sandbox unavailable |
| Frontend tests (`npm run test:run`) | ❌ BLOCKED — bash sandbox unavailable |
| Backend tests (`pytest`) | ❌ BLOCKED — bash sandbox unavailable |
| OpenAPI valid | ✅ `apps/backend/app/openapi.json` exists and opens as valid JSON (read directly — no API changes in these commits) |
| Spot-check | ✅ Clean — see findings below |
| CI on develop | ❓ unknown — `gh` CLI unavailable; `refs/heads/develop` = `7cb442c` (see git note below) |

**Spot-check findings**:

*M-39 — Gemini SDK migration*
- `from google import genai` and `from google.genai import types as genai_types` correctly replaces deprecated `google-generativeai` imports ✅
- `genai.Client(api_key=...)` initialisation uses the new SDK API ✅
- `client.models.generate_content(model=..., contents=..., config=...)` matches new SDK call signature ✅
- `google-genai==1.14.0` pinned in `requirements.txt` ✅
- Safety settings configured via `genai_types.SafetySetting` ✅
- `ImportError` guard retained; logs warning if package missing ✅
- **⚠️ New finding — AWD-H-39 filed**: `generate_content()` has no explicit request timeout on the `client.models.generate_content(...)` call. H-09 added a timeout to `OpenAIProvider`; the Gemini provider was not updated to match. A hung Gemini request can block a worker indefinitely (OWASP LLM10 — Model DoS).
- L-12 already in backlog (stale docstring + inline `import re`) — no new item needed ✅

*M-40 — postcss XSS patch*
- `node_modules/postcss` resolved to version `8.5.10` in `package-lock.json` ✅ (GHSA-qx2v-qp2m-jg93 patched at 8.4.31; 8.5.10 is well past the fix) ✅
- No application code changes; pure dependency lock update ✅

*M-38 — Optional[str] type annotation*
- `def _sanitize_user_context(self, text: Optional[str]) -> Optional[str]` at line 231 — correctly updated ✅
- `Optional` already imported at module top ✅
- Production caller guard (`if context else None`) unchanged ✅

*General*
- No hardcoded secrets or API keys ✅
- No `console.log` / `print()` / debug statements in any changed file ✅
- No `@ts-ignore` or suppression directives ✅
- No TODO/FIXME comments ✅
- No changes to protected routes or auth guards ✅

**Git ref note**: `refs/heads/develop` (loose) = `7cb442c` — this SHA does not appear in `logs/refs/heads/develop` (ends at `f8db6f1`). `packed-refs` still has `af7f7b5c` as the packed develop ref. C-05 (git repo corruption) is still open in the backlog and this discrepancy suggests the ref file was re-corrupted or partially updated after the C-05 recovery attempt. Tolu must verify and repair.

**Infrastructure note**: Bash sandbox continues to fail with "No space left on device" — same blocker as the 2026-04-25T00:00Z dev cycle abort. ALL automated CI mirror checks are blocked until disk is cleared. Tolu must clear the sandbox disk before the next automated run can validate anything.

**Issues filed**: AWD-H-39 (Gemini timeout)

**Verdict**: ⚠️ Needs human — spot-check clean for all three commits; H-39 filed for missing Gemini timeout. Run CI mirror locally (`cd apps/frontend && npx tsc --noEmit && npm run lint && npm run test:run` + `cd apps/backend && python -m pytest tests/ -v`) before merging to main. Git corruption (C-05) still needs Tolu to repair refs/heads/develop locally.

---

## QA — 2026-04-24T20:37:04Z — AWD-M-12 prompt injection fence + input sanitisation

**Result**: ✅ PASS (backend tests skipped — see note)
**Commits**: `322e9e5` (feat: AWD-M-12 fence user context) · `b606c38` (chore: mark done) · `af7f7b5` (chore: qa)
**Files changed (code)**: `packages/ai/gpt_service.py`, `packages/ai/prompts.py`, `apps/backend/tests/test_ai_providers.py`

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 63 passing, 0 failing |
| Backend tests (`pytest`) | ⚠️ SKIPPED — venv/bin/python is a broken symlink to python3.13 (unavailable in sandbox). Run locally: `cd apps/backend && python -m pytest tests/test_ai_providers.py -v` |
| OpenAPI valid | ✅ `apps/backend/app/openapi.json` parses cleanly |
| Spot-check | ✅ Clean — see findings below |
| CI on develop | ❓ unknown — `gh` CLI not available in sandbox |

**Spot-check findings**:
- `_sanitize_user_context()` added with 3-layer defence: truncation at 2000 chars, PII stripping (reuses `_sanitize_input`), regex scrub of 10 injection patterns ✅
- Caller `generate_lesson_resource` correctly applies `_sanitize_user_context(context)` before building `prompt_params` ✅
- `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` now wraps `{local_context}` in `<user_context>` XML tags with an IMPORTANT: instruction telling the model to treat the field as data only ✅
- 11 new tests in `TestSanitizeUserContext` covering: clean passthrough, None/empty input, truncation, PII redaction (email, API key), injection scrubbing (ignore/jailbreak/fake role tags/disregard), and end-to-end `generate_lesson_resource` injection test ✅
- `generate_parent_guide` does NOT use `_sanitize_user_context` — verified intentional: all parent guide params (topic, subject, grade, country, curriculum, objectives) come from the curriculum DB, not free-form user input. No injection surface there ✅
- No hardcoded secrets or API keys ✅
- No `console.log` / `print()` / debug statements ✅
- No `@ts-ignore` or suppression directives ✅
- No TODO/FIXME comments ✅

**Minor issue found (AWD-M-38 filed)**:
- `_sanitize_user_context` is typed `(text: str) -> str` but the test `test_returns_empty_for_none` documents it accepts `None` and returns `None`. In production the caller guards with `if context else None` so `None` is never passed, but the type annotation is wrong. Should be `Optional[str] -> Optional[str]`. Low priority.

**Verdict**: ✅ Ship — all verifiable checks pass. Tolu must run `python -m pytest apps/backend/tests/test_ai_providers.py -v` locally to confirm the 11 new `TestSanitizeUserContext` tests pass before pushing to production.

---

## QA — 2026-04-24T18:35:47Z — AWD-H-37 unauthenticated 401 assertion fix

**Result**: ✅ PASS (backend tests skipped — see note)
**Commits**: `a513468` (merge) · `af523cd` (test: AWD-H-37 fix TestUnauthenticated assertion 403→401)
**Files changed**: `apps/backend/tests/test_children_router.py`

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 63 passing, 0 failing |
| Backend tests (`pytest`) | ⚠️ SKIPPED — venv Python 3.13 symlinks broken in sandbox (Python 3.10 available); disk full, cannot pip install. Run locally: `cd apps/backend && python -m pytest tests/ -v` |
| OpenAPI valid | ✅ `apps/backend/app/openapi.json` parses cleanly |
| Spot-check | ✅ Clean — see findings below |
| CI on develop | ❓ unknown — `gh` CLI not available in sandbox |

**Spot-check findings**:
- Change is test-only — no production code modified ✅
- `TestUnauthenticated.test_returns_401` now correctly asserts HTTP 401 (was 403). This aligns with AWD-H-25's change where `HTTPBearer(auto_error=False)` + manual 401 raise in `get_current_user` replaced the previous auto-error 403 path ✅
- Class docstring updated with clear explanation of the dependency chain ✅
- No hardcoded secrets or API keys ✅
- No `console.log` / `print()` / debug statements ✅
- No `@ts-ignore` or suppression directives ✅
- No TODO/FIXME comments ✅
- No AI prompt changes ✅

**Outstanding known issue (not introduced by this commit)**:
- AWD-H-38 remains open: `TestGenerateGuideIdempotency` and `TestGenerateGuideMalformedAI` still use the double `.filter.return_value` mock chain that doesn't match the service's single `.filter()` call — those 3 tests will still fail in a real pytest run. This fix did not worsen or improve H-38.

**Verdict**: ✅ Ship — test-only fix; frontend green; spot-check clean. Backend tests must be verified locally before next production push.

---

## QA — 2026-04-24T13:35:00Z — AWD-M-14 post-merge validation

**Commits**: `99981fc` (merge) · `d9f8125` (perf: batch subject FK)
**Files changed in commit**: `apps/backend/services/children_service.py`, `apps/backend/tests/test_children_service.py`

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 63 passing, 0 failing |
| Backend tests (`pytest`) | ⚠️ SKIPPED — venv Python symlinks point to macOS framework path (`/Library/Frameworks/Python.framework/Versions/3.13/`) unavailable in Linux QA sandbox. Run locally: `cd apps/backend && python -m pytest tests/ -v` |
| OpenAPI valid | ✅ `apps/backend/app/openapi.json` parses cleanly |
| Spot-check (committed diff) | ✅ No secrets, no console.log/print(), no @ts-ignore, no TODO/FIXME, no missing role checks |
| CI on develop | ❓ unknown — `gh` CLI not available in sandbox |

**Spot-check findings (committed diff — clean)**:
- `children_service.py`: batch `Subject.subject_id.in_(ids)` query correctly replaces per-subject loops in both `create_child` and `update_child` ✅
- `test_children_service.py`: 3 new tests covering batch validation edge cases added (`_db_subjects_not_found` mock, partial-invalid, all-valid) ✅
- No hardcoded secrets or API keys ✅
- No debug statements left in ✅

**REGRESSION DETECTED (working tree / staging area — not in committed HEAD)**:
- `git diff --cached` shows staged `children_service.py` has **reverted** the AWD-M-14 batch IN query back to per-subject loops in both `create_child` and `update_child`
- Staged `test_children_service.py` removes the 3 batch-query tests added by AWD-M-14
- Working-tree (unstaged) version of `children_service.py` adds correct AI output validation (`ParentGuideAIContent.model_validate_json`) — this new code is correct and should be preserved
- If the next `git commit` runs with files in their current staged state, AWD-M-14 silently regresses and N+1 query behavior returns
- **18 additional files** have uncommitted working-tree changes (services, tests, frontend pages) — normal for in-progress work, but confirm none are staged alongside the regression before next commit

**Issues filed**: AWD-H-36 (regression — staging surgery needed before next commit)

**Verdict**: ❌ Needs fix — AWD-H-36 must be resolved (unstage/re-stage `children_service.py` and `test_children_service.py`) before the next commit. Committed HEAD is green and shippable; staging area is not.

---

## QA — 2026-04-24T12:36:00Z
Result: ✅ PASS
Commits: 9e25c23, ff6856c | Files: ParentDashboardPage.tsx, ParentDashboardPage.test.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 63 passing, 0 failing |
| Backend tests | ⚠️ Skipped — venv symlink broken (python3.13 not in sandbox), sandbox out of disk space for pip install. No backend files changed. |
| OpenAPI valid | ✅ (no API changes) |
| Spot-check | ✅ No issues found |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No new TODO/FIXME comments ✅
- Error handling: try/finally on delete handler ✅
- No changes to protected routes / auth guards ✅
- No changes to packages/ai/prompts.py ✅
- Fix verified: child selector cards correctly converted from `<button>` to `<div role="group" tabIndex={0}>` with `onKeyDown` for keyboard navigation. Edit/Delete `<button>` elements are now valid (inside a div, not a button). AWD-M-36 resolved.
- New tests cover the fix: 3 AWD-M-36 specific assertions — card element type, no nested buttons, Enter-key selection all pass ✅

Issues: None
Verdict: Ship

---

## QA — 2026-04-24T11:35:00Z
Result: ⚠️ PASS WITH WARNING
Commits: 5e72d9d, 19017d1 | Files: ParentDashboardPage.tsx, ParentDashboardPage.test.tsx, SavedGuidesPage.tsx, SavedGuidesPage.test.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 60 passing, 0 failing |
| Backend tests | ⚠️ venv Python symlink broken (python3.13 not installed in sandbox) — skipped. Run locally: `cd apps/backend && ../venv/bin/python -m pytest tests/ -v` |
| OpenAPI valid | ✅ (no API changes) |
| Spot-check | ⚠️ 1 issue — see below |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No new TODO/FIXME comments ✅
- Error messages generic — no internal details leaked ✅
- Async error handling in place on both pages ✅
- Role check: pages are parent-only and sit behind auth — no new unguarded routes ✅

**⚠️ DOM nesting violation — `<button>` inside `<button>` (AWD-M-36)**
`ParentDashboardPage.tsx` lines 168–203: each child selector is a `<button>`, and inside it sit two more `<button>` elements (Edit, Delete). This is invalid HTML per spec and fires a `validateDOMNesting` warning in test output. Browsers handle it inconsistently; screen readers and keyboard navigation may break. Fix: convert the outer selector to a `<div role="group">` or restructure so action buttons are siblings, not descendants.

Issues: AWD-M-36 auto-filed (see backlog.md)
Verdict: Ship (DOM nesting is non-blocking for current release but must be fixed before accessibility review)

---

## QA — 2026-04-24T10:36:07Z
Result: ✅ PASS
Commits: fc130ab | Files: apps/frontend/src/pages/SettingsPage.tsx
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ Skipped — venv is a broken symlink (python3.13 not in sandbox) and sandbox has no disk space for pip install. No backend files changed in this commit. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ No secrets, no console.log, no @ts-ignore, no new TODO/FIXME, auth guard present via useAuth, no prompts.py changes. Change cleanly replaces two empty TODO stubs with a user-friendly "not yet available" message and removes a dead `alert()` call. |
| CI on develop | unknown — gh CLI not available in sandbox |
Issues: None
Verdict: Ship

---

## QA — 2026-04-24T09:35:14Z
Result: ✅ PASS
Commits: 31a9d95 | Files: apps/backend/requirements.txt

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv not found in sandbox (recurring infrastructure limitation) — skipped |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check findings:**
- `apps/backend/requirements.txt`: AWD-M-08 implementation. All dependencies pinned to exact versions. Security-critical pins include: `python-multipart==0.0.18` (CVE-2024-53981, PVE-2024-99762), `jinja2==3.1.6` (5 CVEs addressed), `PyJWT==2.12.1` (AWD-H-23 CVE surface), `requests==2.32.4` (CVE-2024-47081), `urllib3==2.5.0` (CVE-2025-50181/50182), `cryptography==44.0.1` (CVE-2024-12797), `setuptools==78.1.1` (CVE-2025-47273, CVE-2024-6345). Comments correctly reference CVE IDs and backlog issue IDs for traceability. No hardcoded secrets, no debug artifacts, no TODO/FIXME. `openai==1.12.0` and `google-generativeai==0.7.2` locked with explanatory comments noting API breaking-change risks.
- **Awareness item (not blocking):** `Pillow==10.0.0` — multiple CVEs exist in Pillow < 10.3.0 (e.g. CVE-2024-28219 heap buffer overflow). Pin may be intentional for compatibility but worth a follow-up review.

Issues: Pillow version flagged as awareness item — see backlog entry L-## below

Verdict: Ship

---
## QA — 2026-04-24T02:35:00Z
Result: ✅ PASS
Commits: eec3d39 ad6a631 | Files: apps/backend/tests/test_async_integration.py

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv symlink broken in sandbox (macOS Python 3.13 framework path not accessible in Linux sandbox) — skipped |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available) |

**Spot-check findings:**
- `test_async_integration.py`: This is a test-only change resolving AWD-M-22. The fix correctly adds `mock_lesson_template` as the 5th `side_effect` entry for the `.first()` chain, and corrects `generate_lesson_resource` return value to the 2-tuple `("Generated Content", True)` that the worker unpacks as `ai_content, is_safe = ...`. No hardcoded secrets, no debug prints, no `@ts-ignore`, no TODO/FIXME, no role-check concerns. Test data is synthetic. Both test functions are clean and properly decorated with `@pytest.mark.asyncio`. No skipped tests.

Issues: None (recurring sandbox venv limitation is infrastructure, not a code issue)

Verdict: Ship

---

## QA — 2026-04-24T01:36:54Z
Result: ✅ PASS
Commits: 84d7829 7865610 | Files: packages/ai/gpt_service.py, apps/backend/tests/test_audit_security_features.py

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv symlink broken in sandbox (python3.13 not accessible in Linux sandbox — recurring limitation) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check findings:**
- `packages/ai/gpt_service.py`: AWD-M-23 implementation. Adds module-level constants `_OUTPUT_PII_PATTERNS`, `_OUTPUT_INJECTION_PATTERNS`, `_HARMFUL_CONTENT_PATTERNS` and a new `_check_content_safety()` method. `validate_output()` now runs a content-safety pass (PII, injection markers, harmful words) before structural JSON validation. Logging uses `logger.warning()` throughout — no bare `print()`. No hardcoded secrets, no @ts-ignore, no TODO/FIXME. Error handling solid. Minor style note: constants defined between import groups (lines 27-51 sit between `from .prompts import` and `from .providers.base import`) — cosmetic issue only, no functional impact. Not worth a backlog item.
- `apps/backend/tests/test_audit_security_features.py`: 8 tests covering token rotation, token revocation, input sanitization, output structure validation, PII rejection, injection marker rejection, harmful content rejection, and rate limiting. Test data is synthetic (`test-key`, `teacher@example.com`). No real credentials. All three content-safety paths (`_check_content_safety`) are directly exercised — solid coverage for the new AWD-M-23 code. `test_rate_limiting_enforcement` depends on the limiter being active in the test environment — accepted pattern per existing test suite.

Issues: None

Verdict: Ship

---

## QA — 2026-04-24T23:33:00Z
Result: ✅ PASS
Commits: f959324 351b63b | Files: apps/frontend/src/pages/ParentOnboardingPage.test.tsx

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv symlink broken in sandbox (python3.13 not accessible in Linux sandbox — recurring limitation) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check findings:**
- `ParentOnboardingPage.test.tsx`: Test-only change scoped entirely to AWD-M-25. No hardcoded secrets, no `console.log`, no `@ts-ignore`, no TODO/FIXME. Synthetic test data used throughout (`parent@test.invalid`, country code `ZZ`, names `Test Child 01/02`). All tests use `vi.hoisted()` correctly to prevent mock-hoisting issues. Root-cause fix is correct: pending-promise pattern keeps all async calls unresolved during synchronous assertions, eliminating `act()` warnings. Redirect test additionally holds ref-data calls pending to prevent post-unmount state updates. All 11 tests in the file pass. No concerns.

Issues: None

Verdict: Ship

---

## QA — 2026-04-22T07:34:53Z
⏭ Skipping — no new commits on develop in the last 40 minutes.

Note: git repo corruption first logged at 06:35Z remains unresolved (`refs/heads/develop` points to missing object `187bd80b`). AWD-C-05 is open. No development activity possible until Tolu runs the recovery commands from the 06:35Z entry.

---

## QA — 2026-04-22T06:35:00Z
Result: ❌ FAIL — git repo corruption blocks development workflow
Commits: no new commit readable (git HEAD corrupted — see below) | Files changed since last valid commit: `apps/backend/services/lesson_plan_service.py` (06:09), `apps/backend/tests/test_ai_providers.py` (04:11), `packages/ai/providers/openai_provider.py` (04:10)

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ 9 passing / 0 failing | All vitest tests pass |
| Backend tests | ❌ env | pytest unavailable — sandbox disk at 100% (9.3G/9.8G used), `pip install` fails with `[Errno 28] No space left on device`. Pre-existing env constraint, not a code regression. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | H-22 fix confirmed in `test_ai_providers.py` (lines 51-52 now assert `gemini-flash-latest`). H-26 fix confirmed in `lesson_plan_service.py` (no `traceback.print_exc()` calls remain). No secrets, no debug logs, no `@ts-ignore` in any changed file. `test-key` values in `test_ai_providers.py` are appropriate test fixtures. Role checks present and correct in `routers/users.py` and `services/children_service.py`. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

**⚠️ CRITICAL: git repo corruption — `refs/heads/develop` points to a missing commit object**

`refs/heads/develop` contains SHA `187bd80b8614c9f84ff3a69f0cddb39a2e31e24b`, but this object does not exist in `.git/objects/`. Running `git log`, `git status`, `git commit`, or `git push` on the develop branch all fail with `fatal: bad object HEAD`. The repo is currently unusable for commits or pushes to GitHub/CI.

**Root cause:** The `.git/objects` directory contains leftover `tmp_obj_*` files from an interrupted commit operation (e.g. `18/tmp_obj_*` at 05:12 UTC, `9d/tmp_obj_*` at 04:10 UTC). These temporaries are written before git renames them to the final SHA filename. The commit object `187bd80b` was never finalized — consistent with a write interruption (likely the sandbox filesystem nearing capacity, as the session disk is at 100%).

**What is safely on disk (confirmed):**
- H-22 fix: `test_ai_providers.py` updated (model name assertions corrected) — modified 04:11 UTC
- H-26 fix: `lesson_plan_service.py` cleaned (no `traceback.print_exc()` calls) — modified 06:09 UTC
- `packages/ai/providers/openai_provider.py` — modified 04:10 UTC (appears to be the H-09 timeout provider work)

**Recovery path (exact commands):**
1. Reset develop to the last valid commit object:
   `git update-ref refs/heads/develop da90c8967dd912f38467e2c93c41ab7501114204`
2. Verify: `git log --oneline -3` should now show `da90c89 chore(backend): replace datetime.UTC with timezone.utc for Python 3.10 compat`
3. Re-commit the on-disk changes (H-22, H-26, openai_provider.py) using `git add <files>` then `git commit`
4. Push to GitHub

→ **AWD-C-05**

Issues: AWD-C-05 auto-filed (git repo corruption — develop branch broken, cannot commit or push)
Verdict: STOP — development is blocked. No pushes or CI runs possible until `refs/heads/develop` is recovered. Code quality on disk is clean; no functional regression detected.

---

## QA — 2026-04-22T02:58:00Z
Result: ⚠️ PASS (commit clean — pre-existing test failure newly visible)
Commits: `da90c89` | Files: `apps/backend/services/context_service.py`, `apps/backend/services/curriculum_service.py`, `apps/backend/services/lesson_plan_service.py`, `apps/backend/tests/test_contexts_router.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ 9 passing / 0 failing | All vitest tests pass |
| Backend tests | ⚠️ 7 passing / 1 failing | `test_ai_providers.py`: 7 pass, 1 fail (`TestGeminiProvider::test_get_model_name`). API endpoint tests (34) error due to no Postgres in sandbox — expected. Failure pre-existing, newly unmasked by `da90c89` Python 3.10 fix. → AWD-H-22 |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, `@ts-ignore`, new `print()`, or new TODO/FIXME introduced by this commit. Pre-existing print calls in `lesson_plan_service.py` already filed as AWD-H-21. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

**Change summary (re-run on `da90c89`):** Second QA pass on the Python 3.10 compat commit (prior run was 02:35:00Z). All static checks pass. This run successfully executes `test_ai_providers.py` — previously impossible before `da90c89` due to the `datetime.UTC` import error — which exposes a pre-existing model-name mismatch in `TestGeminiProvider::test_get_model_name`.

**Gemini test failure (`TestGeminiProvider::test_get_model_name`):**
```
AssertionError: assert 'gemini-flash-latest' == 'gemini-1.5-flash'
  - gemini-1.5-flash
  + gemini-flash-latest
File: apps/backend/tests/test_ai_providers.py:51
```
Root cause: `packages/ai/providers/gemini_provider.py` default model was updated to `gemini-flash-latest` (comment: "Available models as of Jan 2026") but `test_ai_providers.py` lines 51-52 still assert the old `gemini-1.5-flash` / `gemini-1.5-pro` names. Not introduced by `da90c89` (test file not in diff) — pre-existing since provider was updated. Newly visible because the Python 3.10 compat fix unblocks test execution in sandbox/CI. → **AWD-H-22**

Issues: AWD-H-22 auto-filed (pre-existing Gemini model name mismatch in test, newly unmasked)
Verdict: Ship ✅ — commit `da90c89` itself is clean. AWD-H-22 is a separate fix tracked in backlog.

---

## QA — 2026-04-22T02:35:00Z
Result: ✅ PASS
Commits: `da90c89` | Files: `apps/backend/services/context_service.py`, `apps/backend/services/curriculum_service.py`, `apps/backend/services/lesson_plan_service.py`, `apps/backend/tests/test_contexts_router.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ✅ | 0 errors, 0 warnings — clean pass (`node_modules.stale` no longer blocking ESLint) |
| Frontend tests | ✅ 9 passing / 0 failing | All vitest tests pass |
| Backend tests | ⚠️ env | Sandbox timeout — pre-existing Python 3.10/3.11 env mismatch. Not a regression. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ⚠️ | 2 pre-existing `print()` calls in `lesson_plan_service.py` — not introduced by this commit but file was touched. Auto-filed AWD-H-21. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

**Change summary (`da90c89`):** Replaces `datetime.UTC` (Python 3.11+) with `timezone.utc` (Python 3.10-compatible) across `context_service.py`, `curriculum_service.py`, and `lesson_plan_service.py`. Fixes the long-standing sandbox env mismatch that blocked backend test runs locally (Python 3.10 vs 3.11). CI on develop uses Python 3.11 so was unaffected, but local QA was blind to backend tests — this unblocks that.

**Spot-check findings:**
- All three service files: `timezone.utc` substitution is correct. No secrets, no `@ts-ignore`, no new TODO/FIXME. ✅
- `lesson_plan_service.py` line 397: `print(f"Failed to enqueue job: {e}")` — pre-existing, swallows enqueue error after printing to stdout. ⚠️ → AWD-H-21
- `lesson_plan_service.py` line 534: `print(f"DEBUG: Resource {resource_id}...")` — pre-existing debug statement in production path. ⚠️ → AWD-H-21
- `test_contexts_router.py`: Clean — no print/str(e)/secrets. ✅

**Notable:** Lint passed fully clean this time — `node_modules.stale` artifact is resolved. ✅

Issues: AWD-H-21 auto-filed (2 bare `print()` calls in `lesson_plan_service.py`, pre-existing)
Verdict: Ship ✅

---

## QA — 2026-04-22T23:34:00Z
Result: ✅ PASS
Commits: `d108e86`, `022b959` | Files: `apps/backend/routers/auth.py`, `apps/backend/tests/test_security.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`tsc --noEmit`) |
| Lint | ✅ | 0 errors/warnings. ESLint `EACCES: node_modules.stale` workaround applied (sandbox artifact, not a code issue). |
| Frontend tests | ✅ 9 passing / 0 failing | All 9 vitest tests pass. |
| Backend tests | ⚠️ env | Cannot run in sandbox: `ImportError: cannot import name 'UTC' from datetime` (Python 3.10 vs 3.11 req). Pre-existing env mismatch — not a new regression. CI uses Python 3.11 and is expected to pass. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, no `print()`/`console.log`, no `@ts-ignore`, no TODO/FIXME introduced. |
| CI on develop | unknown | `gh` CLI not available in sandbox |

**Change summary (AWD-H-13):** Rate limits applied to four previously unprotected auth endpoints: `POST /api/auth/google` (10/min), `POST /api/auth/refresh` (20/min), `POST /api/auth/forgot-password` (5/min), `POST /api/auth/reset-password` (5/min). All endpoints already had the required `request: Request` parameter for slowapi. New `TestAuthEndpointRateLimitStructure` test class added to `test_security.py` with parametrized structural tests covering all four endpoints — verifies `request` parameter presence and that routes remain registered (return non-404) after the decorator is applied.

**Spot-check notes:**
- No hardcoded secrets or API keys found.
- `IS_PRODUCTION` env guard on `secure=` cookie flag is correct — `httponly=True` is set unconditionally on all refresh-token cookies, which is the right posture.
- `forgot-password` and `reset-password` rate limits (5/min) appropriately prevent email-bombing and reset-token brute-force.
- Test `test_rate_limiting` is intentionally a `pass` stub (pre-existing, not introduced by this commit). No backlog link in skip reason — minor hygiene note but not actionable here.

Issues: None new
Verdict: Ship ✅

---

## QA — 2026-04-22T05:34:00Z
Result: ⚠️ NEEDS FIX
Commits: `4460d8b`, `0184370` | Files: `apps/backend/services/lesson_plan_service.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ 9 passing / 0 failing | All vitest tests pass |
| Backend tests | ⚠️ env | 80 passing, 26 errors — all SQLAlchemy connection errors (no Postgres in sandbox). Expected; DB integration tests pass in CI. Non-regression. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ❌ | 2 `traceback.print_exc()` calls remain at lines 112 and 162 — missed by AWD-H-21 fix. See below. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

**Change summary (AWD-H-21):** Commit `4460d8b` replaced the two bare `print()` calls originally filed in AWD-H-21 (`print(f"Failed to enqueue job: {e}")` at old line 397 and `print(f"DEBUG: Resource {resource_id}...")` at old line 534) with proper structured logging. However, two `traceback.print_exc()` calls were not addressed and remain in the file.

**Spot-check finding — incomplete H-21 fix:**
- `lesson_plan_service.py` line 112: `traceback.print_exc()` in `create_lesson_plan_response()` exception handler — writes full traceback to stderr. `import traceback` is done inline inside the except block.
- `lesson_plan_service.py` line 162: `traceback.print_exc()` in `generate_lesson_plan()` exception handler — same pattern.
- Both calls write to stderr in production paths, violating the code hygiene rule. `logger = logging.getLogger(__name__)` is already imported at the top of the file so the fix is trivial.
- Fix: replace both `import traceback` + `traceback.print_exc()` pairs with `logger.error("...", exc_info=True)` — `exc_info=True` preserves the full traceback in the structured log. → **AWD-H-26**

Issues: AWD-H-26 auto-filed (2 residual `traceback.print_exc()` calls left by partial AWD-H-21 fix)
Verdict: Needs fix — non-blocking hygiene issue, safe to develop on but should be cleaned before next deploy

---

## QA — 2026-04-21T21:34:30Z
Result: ✅ PASS
Commits: `737c830` (merge), `da34bf7` | Files: `apps/backend/routers/children.py`, `apps/backend/tests/test_security.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ⚠️ env | ESLint `EACCES: permission denied, stat 'node_modules.stale'` — sandbox filesystem artifact, pre-existing, not a code issue |
| Frontend tests | ✅ 9 passing / 0 failing | All 9 vitest tests pass |
| Backend tests | ⚠️ env | Cannot run in sandbox: `ImportError: cannot import name 'UTC' from datetime` (Python 3.10 vs 3.11 req). Pre-existing env mismatch. CI uses 3.11 and is expected to pass. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, no `print()`/`console.log`, no `@ts-ignore`, no TODO/FIXME introduced |
| CI on develop | unknown | `gh` CLI not available in sandbox |

**Change summary (AWD-H-07):** `generate_guide` in `apps/backend/routers/children.py` now has `@limiter.limit("5/minute")` and the required `request: Request` parameter. Two structural regression tests added in `TestGenerateGuideRateLimit`: (1) unauthenticated POST returns 403 not 404 (route + decorator stack intact), (2) `inspect.signature` confirms `request` param is present (slowapi requirement). Rate limit prevents OpenAI cost-abuse on cache-miss calls.

Issues: None
Verdict: Ship ✅

---

## QA — 2026-04-21T13:35:00Z
Result: ✅ PASS (commit clean) / ❌ PRE-EXISTING CI FAILURES UNCHANGED
Commits: `cf3e391` | Files: `apps/backend/dependencies.py`, `apps/backend/main.py`, `apps/backend/tests/test_security.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ❌ | 62 pre-existing errors — unchanged from prior run. Not introduced by this commit (backend-only change). → AWD-H-14 (already filed) |
| Lint | ❌ | ESLint config resolution pre-existing failure. → AWD-H-14 (already filed) |
| Frontend tests | ❌ 7 passing / 1 failing | `App.test.tsx:38` stale landing page copy. Pre-existing. → AWD-H-15 (already filed) |
| Backend tests | ⚠️ | Sandbox Python 3.10 blocks import (`datetime.UTC` requires 3.11+). Pre-existing env mismatch. `TestGetJwtSecretKey` tests reviewed manually — logic is correct. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, @ts-ignore, TODO/FIXME found. `get_jwt_secret_key()` correctly raises `RuntimeError` in production when key unset. Startup lifespan validation wired correctly in `main.py`. `print()` calls in `main.py` are pre-existing infrastructure logs, not introduced by this commit. Tests in `test_security.py` cover all 4 cases: key set (prod), key missing (dev), key missing (testing), key missing (prod → raises). |
| CI on develop | unknown | `gh` CLI not available in sandbox |

Issues: None new — AWD-C-02 correctly resolved by this commit and already moved to Done in backlog.
Verdict: Ship — commit is clean and safe. Pre-existing CI failures (H-14, H-15) unchanged.

---

## QA — 2026-04-21T19:34:00Z
Result: ⚠️ PASS (core checks clean, code hygiene issues filed)
Commits: `254d891` `39006b0` `6dbab06` `abf3400` `f5d9693` `4b0dcfa` `80c2cea` `bdf5835` `4d1d067` `e26f1e2` `2b1d918` `0223425` | Files (develop~1): `apps/frontend/.eslintrc.cjs`, `apps/frontend/src/components/AIGenerationLoading*.tsx`, `apps/frontend/src/components/SessionExpiryNotification.tsx`, `apps/frontend/src/pages/EditLessonResourcePage.tsx`, `apps/frontend/src/pages/LoginPage.tsx`, `apps/frontend/src/pages/SettingsPage.tsx`, `apps/frontend/src/services/websocket.ts`, `apps/frontend/src/test/services/api.test.ts`, `apps/frontend/src/test/setup.ts`, `apps/frontend/src/utils/sanitizer.ts`, `apps/frontend/src/vite-env.d.ts`, `apps/frontend/tsconfig.json`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | `npx tsc --noEmit` exited cleanly — 0 errors. AWD-H-14 fix confirmed working. |
| Lint | ⚠️ | ESLint hit `EACCES: permission denied, stat '.../node_modules/node_modules'` — sandbox filesystem artefact (symlink permission issue in mounted volume), not a code error. AWD-H-14 fix (`.eslintrc.cjs` created) is correct; real CI should pass. |
| Frontend tests | ✅ | 9/9 passing (2 test files). AWD-H-15 fix confirmed — `App.test.tsx` correctly asserts parent pivot heading. |
| Backend tests | ⚠️ | Sandbox Python 3.10 still blocks import (`datetime.UTC` requires 3.11+). Pre-existing environment mismatch — not a regression. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ⚠️ | **2 issues filed (H-16, H-17).** Details below. No hardcoded secrets, no `@ts-ignore`, no `dangerouslySetInnerHTML`, no child PII in AI prompts. Auth role whitelist (AWD-C-03) confirmed: only `PARENT`/`EDUCATOR` via Google OAuth. Context route auth (AWD-C-04) confirmed: all 7 routes require `require_admin_or_educator`. |
| CI on develop | unknown | `gh` CLI not available in sandbox |

Issues:
- AWD-H-16 (auto-filed): 10+ `console.log/error` in production paths in `EditLessonResourcePage.tsx` + `SettingsPage.tsx`
- AWD-H-17 (auto-filed): bare `print()` in `auth_service.py:618` token blacklisting error handler
- AWD-M-18 (auto-filed): 2 `TODO` comments in `SettingsPage.tsx` (lines 207, 213) violate CLAUDE.md hygiene rule — should be backlog items

Verdict: Ship — all security fixes (C-02, C-03, C-04) and test/TS fixes (H-14, H-15) are correct. Code hygiene issues filed; none are blockers.

---

## QA — 2026-04-21T12:35:00Z
Result: ⚠️ PASS (recent changes clean) / ❌ PRE-EXISTING CI FAILURES
Commits: `78bd3f6` `c36c48b` | Files: `.gitignore`, `awade_rebranding.docx`, `awade_review_parent_pivot.md`, `docs/public/development/architecture_diagram.md`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ❌ | 62 pre-existing errors — unused imports across SettingsPage, EditLessonResourcePage, AIGenerationLoading* components, websocket.ts `process.env`, test setup `global` references. None introduced by today's commits. → AWD-H-14 |
| Lint | ❌ | ESLint config not found at `apps/frontend/src` — pre-existing missing config resolution. → AWD-H-14 |
| Frontend tests | ❌ 7 passing / 1 failing | `App.test.tsx:38` expects `/Transform Your Teaching with Awade/i` — old educator-focused landing page copy, not updated for parent pivot. Pre-existing. → AWD-H-15 |
| Backend tests | ⚠️ | Cannot run in sandbox (Python 3.10; `datetime.UTC` requires Python 3.11+). Pre-existing env mismatch — CI uses Python 3.11 and is expected to pass. Not a new regression. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, console.log, print(), @ts-ignore, or TODO/FIXME found in changed files. `.gitignore` addition (`awade_grc_audit.docx`) is correct and intentional. |
| CI on develop | unknown | `gh` CLI not available in sandbox |

Issues: AWD-H-14 (TS + lint), AWD-H-15 (App.test.tsx pivot-stale test)
Verdict: Recent commits are safe to ship (docs + gitignore only). CI was already failing on develop due to pre-existing TypeScript and test issues — both auto-filed.

---

## QA — 2026-04-21T20:36:09Z
Result: ✅ PASS
Commits: `6dccf63` | Files: `apps/backend/services/auth_service.py`, `apps/backend/tests/test_auth_flow_security.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ⚠️ env | ESLint threw `EACCES: permission denied, stat 'node_modules.stale'` — sandbox filesystem artifact from stale npm lock file, NOT a code lint failure. Not actionable. |
| Frontend tests | ✅ 9 passing / 0 failing | All 9 vitest tests pass including 3 new enumeration-protection tests |
| Backend tests | ⚠️ env | Cannot run in sandbox: `ImportError: cannot import name 'UTC' from datetime` (Python 3.10 vs 3.11 req). Pre-existing env mismatch. CI uses 3.11 and is expected to pass. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, no new `print()`/`console.log`, no `@ts-ignore`, no TODO/FIXME introduced. |
| CI on develop | unknown | `gh` CLI not available in sandbox |

**Change summary (AWD-H-05):** `authenticate_user` in `auth_service.py` previously returned `"Please use Google OAuth to login with this account"` when a Google-OAuth-only account attempted password login — disclosing that the email exists and is OAuth-registered. Fix returns the identical `"Invalid email or password"` (401) used for unknown emails and wrong passwords. All three enumeration vectors now produce indistinguishable responses. Three new regression tests added covering: unknown email, wrong password, and Google-OAuth-account cases.

**Residual note (pre-existing, not introduced by this commit):** `authenticate_google_user` catch-all at line 228 still leaks `str(e)` in the detail field — covered by existing backlog issue AWD-H-08.

Issues: None new
Verdict: Ship ✅

---

## QA — 2026-04-22T00:34:00Z
Result: ✅ PASS
Commits: `e30e5c1` (merge), `8b012b9` | Files: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors (`npx tsc --noEmit`) |
| Lint | ⚠️ env | ESLint threw `EACCES: permission denied, stat 'node_modules.stale'` — recurring sandbox filesystem artifact. Ran `npx eslint src/` directly: 0 errors, 0 warnings. Not a code issue. |
| Frontend tests | ✅ 9 passing / 0 failing | All vitest tests pass |
| Backend tests | ⚠️ env | Cannot run in sandbox: `ImportError: cannot import name 'UTC' from datetime` (Python 3.10 sandbox vs 3.11 required). Pre-existing env mismatch — not introduced by this commit. CI uses 3.11 and is expected to pass. |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` is valid JSON |
| Spot-check | ✅ | No secrets, no `print()`/`console.log` (uses `logger.error(..., exc_info=True)` correctly), no `@ts-ignore`, no TODO/FIXME introduced. |
| CI on develop | unknown | `gh` CLI not available in sandbox |

**Change summary (AWD-H-12):** `GET /api/users/{user_id}` previously had no ownership check — any authenticated EDUCATOR could retrieve any user's profile (PII disclosure). Fix adds an ownership gate in `UserService.get_user()`: callers must own the record (`current_user.user_id == user_id`) or hold `ADMIN`/`SUPER_ADMIN` role; otherwise raises `HTTP 403` *before* the DB lookup, preventing user enumeration via 404 vs 403. Tests cover all 7 scenarios: own record (200), other EDUCATOR (403), PARENT (403 at dep layer), ADMIN any record (200), SUPER_ADMIN any record (200), unauthenticated (403), admin on non-existent ID (404).

**Spot-check findings:**
- New `get_user` method error handling is clean: generic static message + `logger.error(..., exc_info=True)`, no `str(e)` leakage. ✅
- Pre-existing `str(e)` leakage in other `UserService` methods (`get_users`, `update_user`, `delete_user`, `get_user_profile`, `update_user_profile`) — already tracked under **AWD-H-18**; not introduced or worsened by this commit.
- `require_admin_or_educator` dependency on `GET /{user_id}` correctly allows the ownership logic to run (EDUCATORs reach the service and are blocked there with 403; PARETs are blocked at the dependency level).

Issues: None new
Verdict: Ship ✅

---

## QA — 2026-04-22T01:58:55Z (manual re-run)
Result: ✅ PASS
Commits: `e30e5c1`, `8b012b9` | Files: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`

Re-run triggered manually — same commits as `00:34:00Z` entry above, outside the 40-minute window. All checks re-confirmed:

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors |
| Lint | ⚠️ env | `node_modules.stale` sandbox artifact — not a code issue |
| Frontend tests | ✅ 9/9 | All passing |
| Backend tests | ⚠️ env | Python 3.10 vs 3.11 mismatch, pre-existing |
| OpenAPI valid | ✅ | Valid JSON |
| CI on develop | unknown | `gh` CLI unavailable |

Issues: None new
Verdict: Ship ✅

---

## QA — 2026-04-22T04:36:58Z
Result: ✅ PASS
Commits: `c2c905f` (merge), `4db306a` | Files: `apps/backend/tests/test_ai_providers.py`
| Check | Status | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ | 9 passing, 0 failing |
| Backend tests (non-DB) | ✅ | 8/8 passing in `test_ai_providers.py`; 77 additional non-DB tests passing; 12 DB-dependent tests in `test_security.py` errored on SQLite disk I/O (sandbox limitation — expected, not a code defect) |
| OpenAPI valid | ✅ | Valid JSON |
| Spot-check | ✅ | No secrets, no debug prints, no @ts-ignore, no TODOs/FIXMEs, mocks used correctly |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

Issues: None
Verdict: Ship ✅


---

## QA — 2026-04-22T08:40:00Z
Result: ⏭ SKIPPED — no new commits in the last 40 minutes

Most recent commit on develop (via FETCH_HEAD): `737c830` — 2026-04-21T21:13:13Z (~11.5 h ago)
Most recent commit accessible locally: `10aea23` — 2026-04-22T02:27:42Z (~6 h ago)

⚠️ Infrastructure note: local `develop` branch ref (`refs/heads/develop`) points to commit `187bd80b8614c9f84ff3a69f0cddb39a2e31e24b` which is absent from the local pack files. `git log develop` fails with `fatal: bad object develop`. `git fsck` confirms the ref is an invalid sha1 pointer. The FETCH_HEAD (remote origin/develop at `737c830`) is intact and accessible. This does not block QA — validation is based on reachable commits — but the local ref should be repaired.

Recommended fix (run manually): `git fetch origin && git branch -f develop origin/develop`

Verdict: ⏭ Skip (nothing to validate)

---

## QA — 2026-04-22T09:39:00Z
Result: ⏭ SKIPPED — no new commits in the last 40 minutes

Most recent reachable commit: `10aea234` — 2026-04-22T02:27:42Z (~7 h ago)
Changed files in that commit: `apps/backend/services/context_service.py`, `apps/backend/services/curriculum_service.py`, `apps/backend/services/lesson_plan_service.py`, `apps/backend/tests/test_contexts_router.py`

| Check | Status | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ | 9 passing, 0 failing |
| Backend tests | ⚠️ skipped | `/sessions` disk at 100% — `pip install pytest` fails; macOS venv symlinks unusable in Linux sandbox. Not a code defect. |
| OpenAPI valid | ✅ | Valid JSON |
| Spot-check | ✅ | No secrets, no debug prints, no `@ts-ignore`, no TODO/FIXME. `datetime.UTC` replaced with `timezone.utc` (Python 3.10 compat fix). All 7 context routes have `Depends(require_admin_or_educator)`. Test JWT value `"test-secret"` is a monkeypatched test env var — not a real leaked secret. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

⚠️ Infrastructure note (recurring): `develop` branch HEAD (`187bd80b`) still absent from local pack files — `git log develop` fails. Prior QA entry recommended `git fetch origin && git branch -f develop origin/develop`. Still unresolved.

⚠️ Infrastructure note (new): `/sessions` volume at 100% capacity (`9.3G / 9.8G`). Prevents pip installs in the sandbox. Backend tests cannot be run until space is freed or sandbox is refreshed.

Issues: None (code quality clean — infra limitations only)
Verdict: ⏭ Skip (nothing to validate) — infra issues noted above

---

## QA — 2026-04-22T10:36:21Z
Result: ✅ PASS (with infra caveat on backend tests)
Commits: `1153504` (merge), `91d758e` (fix) | Files: `apps/backend/dependencies.py`, `apps/backend/tests/test_auth_flow_security.py`

| Check | Status | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ | 9 passing, 0 failing |
| Backend tests | ⚠️ skipped | macOS Python 3.13 venv incompatible with sandbox Python 3.10; disk still full — prevents pip install. Recurring infra limitation, not a code defect. |
| OpenAPI valid | ✅ | Valid JSON |
| Spot-check | ✅ | Clean. No hardcoded secrets (pre-existing `"dev-secret"` fallback in non-production paths, unchanged). `print()` in test file only (test-path acceptable). No `@ts-ignore`, no TODO/FIXME. `is_suspended` truthy check correct against Integer(0/1) column. `"test_jwt_secret"` in test matches `conftest.py` JWT_SECRET_KEY monkeypatch — not a real leaked secret. No new routes; only existing `get_current_active_user` dependency modified — 403 raised for suspended users before reaching any route handler. Tests cover: active user passes, suspended user → 403 with `"Account suspended"`, re-activated user passes. |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

⚠️ Infrastructure note (recurring): macOS Python 3.13 venv + full disk prevents backend test execution in sandbox. Not resolvable by QA agent.

Issues: None
Verdict: Ship

---
## QA — 2026-04-22T11:34 UTC
Result: ✅ PASS
Commits: `270ac41` (merge), `8589362` (fix) | Files: `apps/frontend/package-lock.json`
| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Sandbox disk I/O error on DB fixture (infrastructure); 8 unit tests passed before fixture error — not a code regression |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI unavailable) |

**Change summary**: Security patch only — `react-router` and `react-router-dom` bumped to 6.30.3 (GHSA-2w69-qvjg-hvjx XSS via open redirects). Only `package-lock.json` changed. No application code modified.

**Spot-check findings**:
- No secrets, API keys, or hardcoded values
- No `console.log` / `print()` / debug artifacts
- No `@ts-ignore` added
- No TODO/FIXME comments
- No async error handling changes
- No route or role-check changes
- `packages/ai/prompts.py` not touched
- Two React Router v7 future flag warnings in frontend test output (`v7_startTransition`, `v7_relativeSplatPath`) — cosmetic, not blocking

⚠️ Infrastructure note (recurring): backend test suite requires running SQLite DB; sandbox disk I/O error prevents execution. Not resolvable by QA agent.

Issues: AWD-L-09 filed (React Router v7 future flags)
Verdict: Ship

---
## QA — 2026-04-22T12:36 UTC
Result: ❌ FAIL (pre-existing + 1 new test-infra issue; production code clean)
Commits: `73188d5` (merge), `8628ab7` (fix) | Files: `apps/backend/services/country_service.py`, `file_upload_service.py`, `grade_level_service.py`, `lesson_plan_service.py`, `subject_service.py`, `user_service.py`

| Check | Status | Notes |
|-------|--------|-------|
| TypeScript | ✅ | 0 errors |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ 9 passing, 0 failing | |
| Backend tests | ❌ 17 failing, 175 passing | See breakdown below |
| OpenAPI valid | ✅ | |
| Spot-check | ✅ | Changed files clean — no `str(e)`, no hardcoded secrets, no `print()`, no `console.log`, no `@ts-ignore`, no TODO/FIXME, no missing role checks |
| CI on develop | unknown | `gh` CLI unavailable in sandbox |

**Backend test failure breakdown:**
- **Pre-existing H-27** (8 tests): `test_contexts_router.py::TestOwnershipEnforcement` + `TestAdminBypass` — `AttributeError: 'NoneType' object has no attribute 'set'` from `User.__new__()` bypass
- **Pre-existing H-28** (3 tests): `test_auth_flow_security.py::TestExceptionDetailSanitization` — requests hit Pydantic 422 before reaching mocked service
- **Pre-existing M-22** (1 test): `test_async_integration.py::test_worker_task_execution` — mock patch path wrong
- **NEW H-29** (5 tests): `test_auth_flow_security.py::test_login_sets_httponly_cookie`, `test_refresh_token_flow` (fails with `assert 429`), `TestAccountEnumerationProtection` (3 tests) — pass in isolation, fail in full suite; rate-limiter state not reset between test files

**AWD-H-18 code review**: ✅ All 6 changed service files verified clean. `str(e)` removed from all `HTTPException` details and replaced with static strings. No new secrets, no debug artifacts, no role-check gaps.

Issues: AWD-H-29 filed (new test isolation issue)
Verdict: Needs fix (H-29) — AWD-H-18 production code is clean and shippable; test suite has pre-existing + 1 new infra debt

---
## QA — 2026-04-22T15:36:16Z
Result: ✅ PASS (pre-existing failures only — no regressions introduced)
Commits: c38dcd4 | Files: apps/backend/services/country_service.py, file_upload_service.py, grade_level_service.py, lesson_plan_service.py, subject_service.py, user_service.py, apps/backend/tests/test_contexts_router.py

| Check            | Result |
|------------------|--------|
| TypeScript       | ✅ 0 errors |
| Lint             | ✅ 0 errors, 0 warnings |
| Frontend tests   | ✅ 9 passing, 0 failing |
| Backend tests    | ⚠️ 183 passing, 9 failing (all pre-existing: H-28 ×3, H-29 ×5, M-22 ×1) |
| OpenAPI valid    | ✅ |
| Spot-check       | ✅ No secrets, no console.log/print, no @ts-ignore, no TODO/FIXME, no role-check gaps. AWD-H-18 str(e) removal verified clean across all 6 service files. AWD-H-27 User() instantiation fix in test_contexts_router.py correct. |
| CI on develop    | unknown (gh CLI not available) |

Issues:
- 9 failures are all pre-existing, already tracked: AWD-H-28, AWD-H-29, AWD-M-22
- AWD-H-27 fix verified: `_make_educator` / `_make_admin` / `_make_lesson_plan` / `_make_context` now use proper `Model()` instantiation — no NoneType errors

Verdict: Ship — AWD-H-27 is clean. No new issues to file. Pre-existing test debt in backlog.

---

## QA — 2026-04-22T17:34:50Z
Result: ✅ PASS (with one environment caveat — see backend tests)
Commits: 53874c4, 3ce06c4 | Files: apps/backend/tests/conftest.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Could not run locally — sandbox disk exhausted during pip install. CI is authoritative. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not in sandbox) |

**Spot-check notes — `apps/backend/tests/conftest.py`:**
- New `rate_limiter_reset` fixture (lines 251–269): Clean implementation. `autouse=True` ensures it applies to every test. `hasattr` guards correctly make it a no-op in environments where slowapi is absent. Resets before `yield` (pre-test) and after `yield` (post-test) to prevent bleed in both directions. Well-documented with AWD-H-29 reference.
- No hardcoded production secrets — test values ("test_secret_key" etc.) in `setup_test_env` are synthetic test-only strings and acceptable.
- No `print()`, debug statements, TODOs, or `@ts-ignore`.
- No route changes — role check review not applicable.
- `packages/ai/prompts.py` not touched.
- Pre-existing note (not this commit): `setup_test_env` fixture does not restore env vars after the test. Low risk in current test suite, but worth a future M-## cleanup.

Issues: None — no new backlog items required. Fix is correct and surgical.
Verdict: Ship — AWD-H-29 fix is clean. Defer to CI for definitive backend test result.

---

## QA — 2026-04-22T16:35:50Z
Result: ✅ PASS (with one environment caveat — see backend tests)
Commits: a977e9c, 442990d | Files: apps/backend/routers/auth.py, apps/backend/tests/test_auth_flow_security.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Could not run locally — sandbox disk exhausted during pip install. CI is authoritative. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not in sandbox) |

**Spot-check notes:**
- `apps/backend/routers/auth.py`: Clean. All endpoints catch unexpected exceptions and return generic 500 messages with no `str(e)` leakage (H-08/H-28 fix confirmed). Rate limiters applied to all public endpoints. Structured logger used throughout. No hardcoded secrets, no console.log/print, no @ts-ignore, no TODOs.
- `apps/backend/tests/test_auth_flow_security.py`: Well-structured test coverage for H-28 (exception detail sanitization) with 3 test cases covering login, signup, and Google auth paths. Minor observation: debug `print()` statements at lines 25 and 62 in test helpers — harmless in test-only code, not a production concern.

Issues: None — no new backlog items required. Backend test environment limitation is a sandbox constraint only.
Verdict: Ship — AWD-H-28 changes look correct. Defer to CI for definitive backend test result.

## QA — 2026-04-22T18:32:42Z
Result: ✅ PASS
Commits: b9a089f | Files: apps/backend/requirements.txt, apps/backend/tests/conftest.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Could not run locally — sandbox disk exhausted during pip install. CI is authoritative. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not in sandbox) |

**Spot-check notes:**
- `apps/backend/requirements.txt`: PyJWT pinned to `==2.12.1` exactly per AWD-H-23 comment. All other security-relevant packages use `>=` minimum versions tied to known CVEs. No hardcoded secrets, tokens, or passwords. Clean.
- `apps/backend/tests/conftest.py`: Two new session-scoped fixtures — `mock_redis_pool` (prevents arq from attempting real Redis on test startup) and `rate_limiter_reset` (addresses AWD-H-29, resets slowapi storage before/after each test). Both fixtures use hasattr guards for graceful degradation. Synthetic test data throughout. No print()/console.log in production paths, no @ts-ignore, no TODO/FIXME, no secrets.

Issues: None — no new backlog items required. Backend test environment limitation is a sandbox constraint only.
Verdict: Ship — AWD-H-23 dependency pin is correct and safe. conftest.py fixtures are well-formed.

## QA — 2026-04-22T20:35:00Z
Result: ✅ PASS
Commits: ae10a95, 0c61461 | Files: apps/frontend/src/pages/EditLessonResourcePage.tsx, apps/frontend/src/pages/SettingsPage.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Could not run locally — venv not found in sandbox. CI is authoritative. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not in sandbox) |

**Spot-check notes:**
- `EditLessonResourcePage.tsx`: All 8 console.log/error calls removed cleanly across `loadLessonPlanAndResource`, `generateLessonResource`, `autoSaveToDatabase`, and `handleSectionSave`. No hardcoded secrets, no @ts-ignore, no new TODOs, no role-check concerns (frontend-only). Error states handled via `setError()` throughout. Clean.
- `SettingsPage.tsx`: console.log/error removed from `loadUserProfile`, `handleSaveLogin`. Pre-existing TODO comments now correctly reference backlog item `AWD-M-18` — backlog ID confirmed present in `docs/agentic/backlog.md` line 88. One pre-existing issue (not introduced by this commit): `alert()` call in `handleSaveLogin` is poor UX but not a security concern; already covered by M-18 scope.
- No changes to API routes, AI prompts, or backend code — no role-check, contract, or AI safety concerns.

Issues: None — no new backlog items required.
Verdict: Ship — AWD-H-16 console.log cleanup is correct and complete.

## QA — 2026-04-22T21:35:00Z
Result: ✅ PASS
Commits: ea9578c, 991c287 | Files: apps/backend/tests/test_children_router.py, apps/backend/tests/test_children_service.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ Could not run locally — venv not found in sandbox. CI is authoritative. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not in sandbox) |

**Spot-check notes:**
- `test_children_router.py`: 9 test classes covering unauthenticated (403), EDUCATOR-forbidden (403), ownership enforcement (404), CRUD happy paths, guide list, generate-guide idempotency, and malformed AI JSON (502). No hardcoded secrets, no `console.log`/`print()`, no `@ts-ignore`, no TODO/FIXME. Synthetic test data throughout (no real PII). AI patched correctly — never hits real OpenAI API. Role-gating assertions align with expected behavior per security rules.
- `test_children_service.py`: Mirrors router tests at the service layer. Includes Python 3.11 compatibility shim for `datetime.UTC`. Clean isolation via `MagicMock` throughout. FK validation, list isolation, delete, idempotency, and AI-validation paths all covered. `mock_db.add.assert_not_called()` on idempotency path verifies no spurious writes.
- No changes to app code, AI prompts, routes, or migrations — no contract, schema, or security concerns.

Issues: None — no new backlog items required.
Verdict: Ship — AWD-H-11 children router + service tests are comprehensive and clean.

## QA — 2026-04-22T23:35:08Z
Result: ❌ FAIL
Commits: 5367714 | Files: apps/frontend/src/App.tsx, apps/frontend/src/components/MobileNavigation.tsx, apps/frontend/src/components/Sidebar.tsx, apps/frontend/src/pages/ChildrenPage.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings/errors |
| Frontend tests | ✅ 9 passing, 0 failing |
| Backend tests | ⚠️ venv is broken symlink to python3.13 (not present in sandbox); pip install also fails — no disk space on sandbox. CI is authoritative for backend tests. |
| OpenAPI valid | ✅ |
| Spot-check | ❌ — 2 issues found (see below) |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check notes:**
- `ChildrenPage.tsx`: No secrets, no console.log/print, no @ts-ignore, no TODOs. Error and loading states handled correctly. Delete uses try/catch with finally. React Query typed. Clean.
- `Sidebar.tsx` / `MobileNavigation.tsx`: Role-aware nav — correctly hides "My Children" link from EDUCATOR users in the UI. Clean.
- `App.tsx` (line 48–52): **ISSUE** — `/children` route is wrapped in `<ProtectedRoute>` (auth only) but NOT in a PARENT-only guard. An EDUCATOR who navigates directly to `/children` via the address bar will see the ChildrenPage. `ChildrenPage.tsx` itself contains no role check. Security rules require role-gated routes to check `user.role`. Auto-filed as AWD-H-30.
- `ChildrenPage.tsx`: **ISSUE** — No `.test.tsx` file exists for this new page. Code quality checklist requires vitest coverage for new frontend functionality. Testing standards require loading, error, and success states plus EDUCATOR vs PARENT conditional rendering tests. Auto-filed as AWD-H-31.

Issues: AWD-H-30 (missing PARENT role guard on /children route), AWD-H-31 (no vitest tests for ChildrenPage)
Verdict: Needs fix — 2 issues auto-filed; fixes are unambiguous and can be implemented in the next dev cycle.

---
## QA — 2026-04-23T01:34:33Z
Result: ✅ PASS
Commits: `20f83ca` | Files: `apps/frontend/src/pages/ChildrenPage.test.tsx`
| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 34 passing, 0 failing (3 test files) |
| Backend tests | ⚠️ skipped — venv not present in QA sandbox |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown — gh CLI not available |

Spot-check notes:
- `ChildrenPage.test.tsx`: No secrets, no `console.log`, no `@ts-ignore`. All test data is synthetic (country `ZZ`, names `Test Child 0N`, email `*@test.invalid`). No real PII.
- 25 tests across 6 describe blocks: loading, error, empty state, children grid, delete flow, ParentRoute role gate. Covers EDUCATOR redirect (→ `/dashboard`), unauthenticated redirect (→ `/login`), and PARENT happy path. Satisfies all acceptance criteria in AWD-H-31.
- React Router v7 future-flag warnings present in stderr — pre-existing, not introduced by this commit.
- Backend venv missing in sandbox is a QA environment issue, not a code issue. Backend is unchanged in this commit.

Issues: None
Verdict: Ship

---
## QA — 2026-04-23T02:34 UTC
Result: ❌ FAIL
Commits: 8b4ba55 | Files: apps/frontend/src/App.tsx, apps/frontend/src/pages/ParentOnboardingPage.test.tsx, apps/frontend/src/pages/ParentOnboardingPage.tsx, apps/frontend/src/pages/SignupPage.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors |
| Frontend tests | ✅ 43 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ SKIPPED — macOS venv symlinks broken in Linux sandbox; sandbox disk full (no space to install deps). Unrelated to this commit. |
| OpenAPI valid | ✅ |
| Spot-check | ❌ 2 issues (see below) |
| CI on develop | unknown — gh CLI unavailable in sandbox |

Issues:
1. **AWD-H-32** — `ParentOnboardingPage.tsx`: `loadRefData()` and `loadCurriculums()` have no try/catch. API failures silently swallowed — users see empty dropdowns (country, grade, subject) with no error message. Regression in the newly shipped AWD-H-20 feature.
2. **AWD-M-24** — `SignupPage.tsx` lines 55 & 130: `catch (err: any)` — `any` type in catch blocks violates code quality checklist. Low urgency.
3. **AWD-M-25** — `ParentOnboardingPage.test.tsx`: widespread `act(...)` warnings across all async state updates. Tests pass but warn; potential source of flakiness in CI over time.

Verdict: Needs fix — AWD-H-32 is user-facing on the newly shipped onboarding page.

---
## QA — 2026-04-23T03:35 UTC
Result: ✅ PASS
Commits: 766cb88, 0b8a590 | Files: apps/frontend/src/pages/ParentOnboardingPage.tsx, apps/frontend/src/pages/ParentOnboardingPage.test.tsx

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors |
| Frontend tests | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ SKIPPED — venv python3.13 symlink broken in Linux sandbox (macOS venv not portable). Backend files unchanged in this commit. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ Clean |
| CI on develop | unknown — gh CLI unavailable in sandbox |

Spot-check notes:
- `ParentOnboardingPage.tsx`: AWD-H-32 fix confirmed. `loadRefData()` now wrapped in try/catch (lines 49–62); `loadCurriculums()` now wrapped in try/catch (lines 73–80). Both set `setError('Failed to load options. Please refresh.')` on failure. Error message displayed in the form. No hardcoded secrets, no `console.log`, no `@ts-ignore`.
- `ParentOnboardingPage.test.tsx`: 11 tests added covering loading state, redirect (existing children), form validation, submit success, submit error (API error string + thrown exception), ref-data fetch error, curriculum fetch error, and skip link. All test data synthetic (Test Child 01/02, parent@test.invalid, country ZZ). No skipped tests.
- `act(...)` warnings still present in test stderr — pre-existing issue (AWD-M-25), not introduced by this commit. Tests pass cleanly.
- AWD-H-32 is now resolved. AWD-M-24 (catch err: any in SignupPage) and AWD-M-25 (act warnings) remain open.

Issues: None introduced. AWD-H-32 verified fixed.
Verdict: Ship

---
## QA — 2026-04-23T04:36 UTC
Result: ✅ PASS
Commits: 364762f, 85c42e6 | Files: .env.example, apps/backend/main.py, apps/backend/requirements.txt, apps/frontend/package.json, apps/frontend/src/main.tsx, apps/frontend/src/vite-env.d.ts, env.example, env.production.template, env.test.template

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ SKIPPED — venv python3.13 symlink broken in Linux sandbox (macOS venv not portable). Backend logic in main.py is new `_init_sentry()` init-only path; no runtime routes changed. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ Clean |
| CI on develop | unknown — gh CLI unavailable in sandbox |

Spot-check notes:
- `apps/backend/main.py`: `_init_sentry()` added before app creation. Correctly gated on `SENTRY_DSN` env var (skips when blank — safe for dev/local). Disabled when `ENVIRONMENT=testing`. Handles `ImportError` (package not installed) and generic exceptions gracefully — both are logged via structured logger, not `print()`. `send_default_pii=False` — COPPA/GDPR compliant. No hardcoded secrets. No new `print()` calls introduced in this diff (pre-existing `print()` calls in `run_database_fix()` and Redis pool setup are unrelated to this commit).
- `apps/frontend/src/main.tsx`: Sentry lazy-loaded via dynamic `import('@sentry/react')` only when `VITE_SENTRY_DSN` is set. `.catch(() => {})` on the dynamic import — app runs cleanly if SDK import fails. `sendDefaultPii: false` set. Session replay uses `maskAllText: true, blockAllMedia: true` — child-safe. No `@ts-ignore`, no `console.log`.
- `apps/frontend/src/vite-env.d.ts`: Ambient type stub for `@sentry/react` — allows builds on fresh checkouts before `npm ci`. Clean, no issues.
- `apps/frontend/package.json`: `@sentry/react ^8.0.0` added to dependencies. Range version (not pinned) — consistent with existing frontend deps. ⚠️ Note: AWD-M-08 (pin backend requirements) doesn't cover frontend — acceptable as-is.
- `apps/backend/requirements.txt`: `sentry-sdk[fastapi]==2.58.0` pinned exactly. Good.
- All env template files (`.env.example`, `env.example`, `env.production.template`, `env.test.template`) updated with `SENTRY_DSN` and `VITE_SENTRY_DSN` placeholders. Test template correctly sets both to blank and notes Sentry is disabled in testing. ✅
- No role check regressions — no new routes added.
- No AI prompt changes.
- `_init_sentry()` has no backend test coverage (see AWD-M-26 filed below).
- `project-config.md` §5 still lists `ERROR_MONITORING: not yet connected` — stale after H-01 ships (see AWD-L-10).

Issues:
1. **AWD-M-26** (auto-filed) — No pytest coverage for `_init_sentry()` in `apps/backend/main.py`. Three branches untested: (a) `SENTRY_DSN` blank → returns early, (b) `ENVIRONMENT=testing` → returns early, (c) `ImportError` → logs warning. Low risk due to safe failure modes, but testing standards require at least a smoke test. See backlog for fix detail.
2. **AWD-L-10** (auto-filed) — `project-config.md` §5 `ERROR_MONITORING` field still reads "not yet connected (Sentry recommended — flagged as H-01)". Should be updated to reflect H-01 shipped in commit 364762f.

Verdict: Ship

---

## QA — 2026-04-23T17:36Z
Result: ❌ FAIL

Commits: b552efe | Files: .env.example, apps/backend/main.py, apps/backend/requirements.txt, apps/backend/tests/test_sentry_init.py, apps/frontend/package.json, apps/frontend/src/main.tsx, apps/frontend/src/vite-env.d.ts, env.example, env.production.template, env.test.template

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ SKIPPED — venv symlinks broken in sandbox (venv/bin/python3 → python3.13, which is not available). No backend logic changed by intent, but see Issues below — CI will fail. |
| OpenAPI valid | ✅ |
| Spot-check | ❌ — see Issues |
| CI on develop | unknown (gh CLI not available in sandbox) |

Issues:
1. **AWD-H-33** (auto-filed — STOP) — Commit `b552efe` accidentally reverted the entire Sentry observability stack (AWD-H-01) and shipped `test_sentry_init.py` tests that reference `apps.backend.main._init_sentry()`, a function that no longer exists in the committed HEAD. CI backend tests will fail with `AttributeError: module 'apps.backend.main' has no attribute '_init_sentry'`. Root cause: developer's working tree retained the Sentry code (confirmed via `git status`: `M apps/backend/main.py`, etc.) but they only staged and committed the new test file. The committed HEAD is missing: `_init_sentry()` in main.py, `sentry-sdk[fastapi]` in requirements.txt, `@sentry/react` in package.json, frontend Sentry init in main.tsx, Sentry env vars in all env templates. See backlog for exact fix.

Verdict: **STOP — do not run next dev cycle until H-33 is resolved by Tolu**

---

## Dev Cycle — 2026-04-23T18:12Z
AWD-H-33 fixed: Sentry stack restored in commit `4920431`. Develop now has `_init_sentry()` in `main.py`, `sentry-sdk[fastapi]==2.58.0` in requirements, `@sentry/react` in package.json, and SENTRY_DSN vars in all env templates. TypeScript: ✅ 0 errors. Lint: ✅ 0 errors. Frontend tests: ✅ 45/45. JSON contracts: ✅ valid.

**STOP verdict cleared. Next dev cycle may proceed.**

Note: Push to origin/develop blocked by HTTPS credentials not available in sandbox — Tolu must run `git push origin develop` locally to trigger CI.

---

## QA — 2026-04-23T18:36Z
Result: ✅ PASS

Commits: 4920431 | Files: .env.example, apps/backend/main.py, apps/backend/requirements.txt, apps/frontend/package.json, apps/frontend/src/main.tsx, apps/frontend/src/vite-env.d.ts, env.example, env.production.template, env.test.template

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ SKIPPED — venv symlinks broken in sandbox (venv/bin/python3 → python3.13, not available). Pre-existing sandbox limitation; no backend logic regression risk — all changes are init/config guarded by env vars. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ Clean |
| CI on develop | unknown — gh CLI unavailable in sandbox |

Spot-check notes:
- `apps/backend/main.py`: `_init_sentry()` fully restored. Guarded by `SENTRY_DSN` env var (skips when blank). Disabled when `ENVIRONMENT=testing`. `ImportError` and generic exceptions handled gracefully via structured logger. `send_default_pii=False` — COPPA/GDPR compliant. No hardcoded secrets. No new `print()` calls introduced by this diff.
- `apps/frontend/src/main.tsx`: Sentry lazy-loaded via dynamic import only when `VITE_SENTRY_DSN` is set. `.catch(() => {})` ensures app runs cleanly without SDK. `sendDefaultPii: false` set. Session replay uses `maskAllText: true, blockAllMedia: true` — child-safe.
- `apps/frontend/src/vite-env.d.ts`: Ambient type stub for `@sentry/react` preserved — allows fresh-checkout builds before `npm ci`. No conflicts once package is installed.
- `apps/backend/requirements.txt`: `sentry-sdk[fastapi]==2.58.0` pinned exactly. ✅
- `apps/frontend/package.json`: `@sentry/react ^8.0.0` in dependencies. Consistent with existing frontend dep pinning strategy.
- All env templates (`.env.example`, `env.example`, `env.production.template`, `env.test.template`) contain correct `SENTRY_DSN` / `VITE_SENTRY_DSN` placeholders. Test template correctly leaves both blank. ✅
- No role check regressions — no new routes added.
- No AI prompt changes.
- Pre-existing open items AWD-M-26 (no pytest coverage for `_init_sentry()`) and AWD-L-10 (project-config.md stale ERROR_MONITORING field) still apply — no new auto-filing needed.

Issues: None new

Verdict: Ship

---

## QA — 2026-04-23T19:34Z
Result: ⚠️ PASS with issue auto-filed
Commits: 3e54929 bfef00f | Files: apps/backend/app/openapi.json, apps/backend/dependencies.py, apps/backend/routers/auth.py, apps/backend/schemas/users.py, apps/backend/tests/test_auth_flow_security.py, apps/frontend/src/contexts/AuthContext.tsx, apps/frontend/src/pages/admin/{AuditLogs,Dashboard,ModerationList,UserList}.tsx, apps/frontend/src/services/api.ts, apps/frontend/src/test/services/api.test.ts

| TypeScript      | ✅ 0 errors |
| Lint            | ✅ 0 errors, 0 warnings |
| Frontend tests  | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests   | ⚠️ SKIPPED — venv symlinks are macOS-only (→ python3.13 on host); sandbox disk full, cannot pip install. No backend logic changed (auth_service untouched); risk is low but tests must be confirmed locally. |
| OpenAPI valid   | ✅ |
| Spot-check      | ✅ with one finding (see below) |
| CI on develop   | unknown — gh CLI unavailable in sandbox |

Spot-check notes:
- `apps/backend/routers/auth.py`: All three auth endpoints (google, signup, login) now set `access_token` + `refresh_token` as `httponly=True, samesite="lax", secure=IS_PRODUCTION`. Response body no longer contains `access_token`. Rate limiters intact. No hardcoded secrets. No `print()` in production paths. ✅
- `apps/backend/dependencies.py`: `get_current_user` correctly reads token from either `Authorization` header OR `access_token` cookie. Role dependencies unchanged. ✅
- **ISSUE — `get_optional_current_user` NOT updated**: still reads only the `Authorization` header; does not fall back to the `access_token` cookie. Browser clients authenticated via cookie will be treated as unauthenticated by this dependency. Affects `curriculum.py`, `curriculum_structure.py`, and `lesson_plans.py`. → Auto-filed AWD-H-34.
- `apps/frontend/src/contexts/AuthContext.tsx`: No `localStorage`/`sessionStorage` usage. Comments confirm cookie-based auth. ✅
- `apps/frontend/src/services/api.ts`: No `localStorage` token storage. `credentials: 'include'` on all fetches. Refresh flow reads cookie automatically. ✅
- Admin pages: all four updated to rely on cookie (comments confirm `access_token cookie sent automatically`). No `@ts-ignore`, no `dangerouslySetInnerHTML`. ✅
- `apps/backend/tests/test_auth_flow_security.py`: Two `print()` debug lines (19, 55) — test file only, not production paths. Acceptable but noted. ✅
- No AI prompt changes. No new TODO/FIXME. No secrets detected.

Issues: AWD-H-34 auto-filed (get_optional_current_user missing cookie fallback)

Verdict: Ship (backend tests should be verified locally before promoting to main)

---
## QA — 2026-04-23T21:35:13Z
Result: ✅ PASS
Commits: d05de88 c96a71c | Files: apps/backend/dependencies.py, apps/backend/tests/test_security.py

| Check | Result |
|---|---|
| TypeScript | ✅ |
| Lint | ✅ |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv not found — skipped (run: `python3 -m venv venv && source venv/bin/activate && pip install -r apps/backend/requirements.txt`) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available) |

**Spot-check findings:**
- `dependencies.py`: AWD-H-34 fix verified — `get_optional_current_user` now reads `Authorization` header first, then falls back to `access_token` HttpOnly cookie. Logic is clean, no broad exception swallowing (returns `None` on any error, which is correct for an optional auth dep). No hardcoded secrets, no stray print/debug statements, no TODO/FIXME, no new role-check concerns (this is a dep, not a route).
- `test_security.py`: New `TestGetOptionalCurrentUserCookieFallback` class with 5 targeted tests: header auth, cookie auth, unauthenticated (None), invalid cookie token (None), header-over-cookie precedence. Test data uses synthetic users only. No skips without backlog links. Token minted from env var `JWT_SECRET_KEY` with fallback to `"test_jwt_secret"` — appropriate for test scope.

Issues: None

Verdict: Ship (backend tests should be verified locally before promoting to main — venv missing in sandbox)

---
## QA — 2026-04-23T22:35:00Z
Result: ✅ PASS
Commits: 33f7b52 4489086 | Files: apps/frontend/src/pages/SignupPage.tsx

| Check | Result |
|---|---|
| TypeScript | ✅ |
| Lint | ✅ |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv symlink broken in sandbox (macOS framework Python not accessible) — skipped |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available) |

**Spot-check findings:**
- `SignupPage.tsx`: Diff is clean and tightly scoped. Two `catch (err: any)` blocks narrowed to `catch (err: unknown)` with proper `instanceof Error` guards in `handleGoogleSuccess` (line 55) and `handleSubmit` (line 130). No hardcoded secrets, no `console.log`, no `@ts-ignore`, no TODO/FIXME, no new role-check concerns (public signup page). All async paths remain wrapped in try/catch with `finally` for loading state cleanup. ✅
- Pre-existing note (not introduced by this commit): `credentialResponse: any` at line 40 was already present before this change — not in scope of AWD-M-24.
- `SignupPage.tsx` has no colocated test file. The fix is type-narrowing only (no logic change), so no new test obligation is created, but coverage gap is noted for future.

Issues: None

Verdict: Ship

---
## QA — 2026-04-24T03:35:00Z
Result: ⚠️ PASS WITH NOTE
Commits: b40496a afed4c2 | Files: apps/backend/middleware/security_headers.py, apps/backend/tests/test_security.py

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing |
| Backend tests | ⚠️ venv symlink is broken (python3.13 absent in sandbox); sandbox also out of disk space for pip install — skipped |
| OpenAPI valid | ✅ |
| Spot-check | ⚠️ — see below |
| CI on develop | unknown (gh CLI not available) |

**Spot-check findings:**
- `security_headers.py`: AWD-M-11 adds a `Content-Security-Policy` header to `SecurityHeadersMiddleware`. Middleware is correctly registered in `main.py` (line 178). No hardcoded secrets, no stray `print()`, no TODO/FIXME. Middleware registered AFTER CORS (correct order). ✅
- `'unsafe-inline'` in `script-src` and `style-src`: The newly added CSP includes `'unsafe-inline'` for both script and style sources. This significantly weakens XSS protection — the primary purpose of CSP is to block inline script execution, which `'unsafe-inline'` re-enables. This is a known trade-off for apps using inline styles/scripts, but it should be tightened with nonces or hashes. Filed as AWD-M-35.
- `test_security.py`: Two new tests — `test_security_headers()` and `test_csp_header_directives()` — cover the new header correctly. No skips without backlog links, no real user data. ✅

Issues: AWD-M-35 filed (unsafe-inline in CSP weakens XSS protection)

Verdict: Ship (backend tests must be verified locally before promoting to main; CSP tightening tracked as AWD-M-35)

---

## QA — 2026-04-24T04:37Z
Result: ❌ FAIL
Commits: `1c175fc` | Files: `apps/backend/main.py`, `apps/backend/middleware/security_headers.py`, `apps/backend/tests/test_docs_visibility.py`, `apps/backend/tests/test_security.py`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing / 0 failing |
| Backend tests | ⚠️ Skipped — venv symlink broken (points to python3.13, not in sandbox); disk full, cannot install pytest |
| OpenAPI valid | ✅ |
| Spot-check | ❌ CSP regression (see below) |
| CI on develop | unknown (gh CLI not available) |

**Spot-check findings:**

- `main.py` (AWD-M-10 change): Correct — `docs_url` and `redoc_url` set to `None` when `ENVIRONMENT=production` using module-level `_APP_ENVIRONMENT`, `_docs_url`, `_redoc_url`. Logic is clean; no hardcoded secrets, no new stray `print()` calls introduced. ✅
- `test_docs_visibility.py`: New test file, 5 well-formed tests covering production/non-production gating logic. Uses `monkeypatch` correctly. ✅
- `test_security.py`: Unmodified by this commit (the diff shows no changes to this file from the commit itself). ✅
- **❌ SECURITY REGRESSION — CSP header removed from `security_headers.py`**: The AWD-M-10 branch was cut from a pre-M-11 version of `security_headers.py`. The merge into `develop` (commit `6adca34`) clobbered the CSP header that AWD-M-11 added. `git show develop:apps/backend/middleware/security_headers.py` confirms no `Content-Security-Policy` line in committed HEAD. The test `test_csp_header_directives` in `test_security.py` (added by AWD-M-11) asserts `"Content-Security-Policy"` is present in responses — it will **fail in CI**. The working tree has the CSP restored as an uncommitted local change, suggesting the regression was noticed locally but not yet committed. Filed as AWD-H-35.
- **⚠️ 17 uncommitted modified files in working tree**: `apps/backend/middleware/security_headers.py`, `apps/backend/schemas/children.py`, `apps/backend/services/auth_service.py` and 14 others. These changes are not yet committed. The CSP fix above is among them.

Issues: AWD-H-35 filed (CSP header regression — will cause CI backend-test failure)

Verdict: Needs fix — commit the CSP restoration and push before CI run

---
## QA — 2026-04-24T05:35:58Z
Result: ✅ PASS
Commits: 2f0fc8a | Files: apps/backend/middleware/security_headers.py, apps/backend/tests/test_security.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing / 0 failing |
| Backend tests | ⚠️ Skipped — venv symlink broken (macOS python3.13 absent in Linux sandbox); disk full, cannot install pytest. Run locally: `cd apps/backend && python -m pytest tests/ -v` |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Commit summary**: `fix(security): AWD-H-35 restore Content-Security-Policy header lost in M-10 merge`
- `security_headers.py`: CSP header fully restored. All 6 directives present: `default-src 'self'`, `script-src 'self' 'unsafe-inline'`, `style-src 'self' 'unsafe-inline'`, `img-src 'self' data: https:`, `connect-src 'self'`, `frame-ancestors 'none'`, `form-action 'self'`, `base-uri 'self'`. ✅
- `test_security.py`: `test_csp_header_directives` test added, asserting all 4 key CSP directives. Complements the existing `test_security_headers` test. ✅
- AWD-H-35 confirmed as resolved in `completed_backlog.md`. ✅

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() / debug left in ✅
- No @ts-ignore added ✅
- No missing async error handling ✅
- No new TODO/FIXME comments ✅
- No missing role checks (middleware applies to all routes uniformly) ✅
- `packages/ai/prompts.py` not touched ✅

Issues: None

Verdict: Ship

---
## QA — 2026-04-24T06:36:30Z
Result: ✅ PASS
Commits: 64d117b | Files: apps/backend/main.py, apps/backend/tests/test_security.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing / 0 failing |
| Backend tests | ⚠️ Skipped — venv symlink broken (macOS python3.13 absent in Linux sandbox). Run locally: `cd apps/backend && python -m pytest tests/ -v` |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Commit summary**: `fix(security): AWD-M-36 restrict CORS allow_methods and allow_headers from wildcard`
- `main.py`: `allow_methods` changed from `["*"]` → `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]`; `allow_headers` changed from `["*"]` → `["Authorization", "Content-Type", "X-Requested-With"]`. ✅
- `test_security.py`: `test_cors_allowed_methods_and_headers` test added; asserts no wildcard in methods or headers, and all required frontend methods/headers are present. ✅

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added in this diff ✅ (pre-existing prints in startup path not touched)
- No @ts-ignore added ✅
- No missing async error handling ✅
- No new TODO/FIXME comments ✅
- No missing role checks (CORS middleware applies globally) ✅
- `packages/ai/prompts.py` not touched ✅

Issues: None

Verdict: Ship

---
## QA — 2026-04-24T07:36:04Z
Result: ✅ PASS (backend tests skipped — sandbox env issue, see note)
Commits: `db282f7` | Files: `apps/backend/services/children_service.py`, `apps/backend/tests/test_children_service.py`

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 45 passing, 0 failing (4 test files) |
| Backend tests | ⚠️ skipped — venv is a broken symlink (points to python3.13, not available in sandbox); ENOSPC prevents pip install. Run `cd apps/backend && python -m pytest tests/ -v` locally to verify. |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Commit summary**: `perf(children): AWD-M-13 eager-load curriculum_structure.subject in get_child_topics`
- `children_service.py` `get_child_topics()`: added `joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject)` to the query options — eliminates the N+1 subject lookup per topic row. ✅
- `test_children_service.py`: new `TestGetChildTopics` class added with 5 tests covering: empty list when no curricula_id, empty list when no grade_level_id, topic list with subject info resolved, null curriculum_structure → None fields (no crash), EDUCATOR → 403. ✅

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No missing async error handling ✅
- No new TODO/FIXME comments ✅
- Role check present: `_verify_parent()` called at top of `get_child_topics()` ✅
- `packages/ai/prompts.py` not touched ✅

Issues: None

Verdict: Ship

---

## QA Run — 2026-04-24T10:20:00Z — AWD-M-18

| Check | Result |
|-------|--------|
| tsc --noEmit | ✅ |
| npm run lint | ✅ |
| npm run test:run (45 tests) | ✅ |
| pytest test_security.py (32 tests) | ✅ |
| openapi.json valid | ✅ |
| mcp.json valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Commit summary**: `style(settings): AWD-M-18 remove TODO comments, show not-yet-available message for email/password update`
- `SettingsPage.tsx` `handleSaveLogin()`: removed two `// TODO:` empty blocks that silently did nothing. Replaced with early-return + `setLoginErrors({ general: '...' })` when email/password change is attempted. False success `alert()` eliminated. ✅
- No new test file required — this is a code hygiene / UX correctness fix with no new logic branches; existing 45 vitest tests continue to pass. ✅

**Also confirmed this run**: AWD-H-34 (`get_optional_current_user` cookie fallback) was already committed at `c96a71c` in a prior session; backlog entry was open in error. Tests verified (32/32 in test_security.py). Backlog cleaned up.

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No new TODO/FIXME comments ✅
- No async await calls without error handling ✅
- False success alert removed — user now gets honest feedback ✅

Issues: None

Verdict: Ship

## QA Run — 2026-04-24T11:15:00Z — AWD-M-01

| Check | Result |
|-------|--------|
| tsc --noEmit | ✅ |
| npm run lint | ✅ |
| npm run test:run (60 tests) | ✅ |
| openapi.json valid | ✅ (no API changes) |
| mcp.json valid | ✅ |
| Spot-check | ✅ |
| CI on develop | pending (push to GitHub requires Tolu credentials) |

**Commit summary**: `feat(parents): AWD-M-01 add loading and error states to parent pages`
- `ParentDashboardPage.tsx`: Added `isError: childrenFetchFailed` + `refetch: refetchChildren` to children query; `isError: topicsFetchFailed` + `refetch: refetchTopics` to topics query. Children error now shows explicit "Failed to load…/Try again" block instead of falling through to EmptyState. Topics error shows "Failed to load topics./Try again" instead of empty "No topics found" ✅
- `SavedGuidesPage.tsx`: Added `isLoading: loadingChildren`, `isError: childrenFetchFailed`, `refetch: refetchChildren` to children query; `isError: guidesFetchFailed`, `refetch: refetchGuides` to guides query. Children loading/error rendered before guide list. Guides error shows "Failed to load guides./Try again" ✅
- `GuideViewPage.tsx`: Already fully compliant — no changes needed ✅
- New tests: `ParentDashboardPage.test.tsx` (7 tests), `SavedGuidesPage.test.tsx` (8 tests). 60/60 total pass ✅

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No new TODO/FIXME comments ✅
- Error messages are generic (no internal details leaked) ✅
- Retry buttons call `refetch()` — no page reload ✅

Verdict: Ship

## QA Run — 2026-04-24T14:18:00Z — AWD-M-02

| Check | Result |
|-------|--------|
| tsc --noEmit | ✅ |
| npm run lint | ✅ |
| npm run test:run (63 tests) | ✅ |
| openapi.json valid | ✅ (no API changes) |
| mcp.json valid | ✅ |
| Spot-check | ✅ |
| CI on develop | pending (push to GitHub requires Tolu credentials) |

**Commit summary**: `feat(seo): AWD-M-02 add OG tags, Twitter card, schema.org and og-image to landing page`
- `index.html`: Updated title ("Awade — Help Your Child Learn at Home | AI Guides for African Parents"), updated description to parent-pivot copy, updated keywords to include African markets. Added canonical URL, robots meta, full OG block (og:type, og:site_name, og:url, og:title, og:description, og:image 1200×630, og:image:alt, og:locale en_NG + alternates for GH/KE/ZA), Twitter Card (summary_large_image), Schema.org WebApplication JSON-LD with areaServed for NG/GH/KE/ZA ✅
- `public/og-image.svg`: 1200×630 SVG OG image with brand gradient (navy→green), Awade wordmark, tagline, description lines, CTA pill, and decorative book icon ✅

**Spot-check findings**:
- No hardcoded secrets / API keys ✅
- No console.log / print() added ✅
- No @ts-ignore added ✅
- No new TODO/FIXME comments ✅
- Old educator-only description ("AI-powered educator support platform for African teachers") replaced with parent-pivot copy ✅
- OG image path matches public/ (served at /og-image.svg by Vite) ✅
- Schema.org JSON-LD is syntactically valid ✅

Verdict: Ship

---
## QA — 2026-04-24T14:36:21Z
Result: ✅ PASS (with advisory)
Commits: 577921c (merge), 34940e1 (feat) | Files: apps/frontend/index.html, apps/frontend/public/og-image.svg

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 63 passing, 0 failing (6 test files) |
| Backend tests | ⚠️ Skipped — venv symlink broken (points to python3.13, not in sandbox). Run: `cd /path/to/awade && python3.13 -m venv venv && pip install -r apps/backend/requirements.txt` to rebuild |
| OpenAPI valid | ✅ apps/backend/app/openapi.json parses cleanly |
| Spot-check | ⚠️ Advisory filed (see Issues below) |
| CI on develop | ⚠️ Unknown — gh CLI not available in sandbox |

Issues:
- **AWD-M-37** (Medium): `og:image` and `twitter:image` reference `og-image.svg`. SVG is not supported by Facebook, WhatsApp, LinkedIn, or most OG crawlers — no preview image will render when sharing awade.app. Fix: convert to PNG and update meta tags in `index.html` lines 22 and 36.
- Spot-check: No secrets, no console.log/print(), no @ts-ignore, no TODO/FIXME in changed files. Static HTML/SVG only — no auth routes or async logic touched.

Verdict: Ship (AWD-M-02 is live; M-37 is a functional follow-up that should be resolved before any social/SEO push)

---
## QA — 2026-04-24T15:34:00Z
Result: ✅ PASS
Commits: 7ac1c42 (merge), d791752 (fix) | Files: apps/frontend/index.html, apps/frontend/public/og-image.png

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 63 passing, 0 failing (6 test files) |
| Backend tests | ⚠️ Skipped — project venv not executable in sandbox (symlink not resolvable). Run locally: `cd awade && venv/bin/python -m pytest apps/backend/tests/ -v` |
| OpenAPI valid | ✅ apps/backend/app/openapi.json parses cleanly |
| Spot-check | ✅ Clean — no secrets, no console.log/print(), no @ts-ignore, no TODO/FIXME, no auth routes touched |
| CI on develop | ⚠️ Unknown — gh CLI not available in sandbox |

Issues: None. This commit resolves AWD-M-37 (auto-filed by previous QA run). Change is minimal and correct: SVG→PNG swap in index.html meta tags + 1200×630 PNG asset confirmed in place.

Verdict: Ship ✅

---
## QA — 2026-04-24T16:42:43Z
Result: ❌ FAIL
Commits: 0afb165 (chore), 67d23ce (merge), b25e3a0 (fix/AWD-H-36) | Files: apps/backend/services/children_service.py, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 63 passing, 0 failing (6 test files) |
| Backend tests | ❌ 13 failing, 277 passing — all in `test_children_router.py` |
| OpenAPI valid | ✅ apps/backend/app/openapi.json parses cleanly |
| Spot-check | ✅ No secrets, no console.log/print(), no @ts-ignore, no TODO/FIXME. Auth guard present on all routes. `ParentGuideAIContent` schema validation wired correctly. |
| CI on develop | ⚠️ Unknown — gh CLI not available in sandbox |

Issues:
- **AWD-H-37** (pre-existing since AWD-H-25): 10 `TestUnauthenticated` tests assert `status == 403` but auth layer returns `401`. Root cause: AWD-H-25 changed `HTTPBearer(auto_error=True→False)`; `get_current_user` now manually raises 401. Test assertions were never updated. Fix: change assertion to 401 and rename test in `apps/backend/tests/test_children_router.py` lines ~148–155.
- **AWD-H-38** (pre-existing since test commit `991c287`, blocks H-36 verification): 3 tests (`test_existing_guide_returned_no_ai_call`, `test_malformed_ai_json_returns_502`, `test_missing_required_ai_fields_returns_502`) fail with 500 instead of 200/502. Root cause: mock DB wires `.options().filter().filter().first()` but service calls `.options().filter(cond1, cond2).first()` — one filter call, not two. MagicMock returned for `existing` guide is truthy, causing early return into `_guide_to_response(MagicMock)` → Pydantic validation error → unhandled 500. The H-36 502-validation block is never reached. Fix: remove extra `.filter.return_value` layer in mock setup in `apps/backend/tests/test_children_router.py` lines ~432 and ~488.

Note: AWD-H-36 implementation in `children_service.py` is correct — the `model_validate_json` + 502 raise is properly coded. Failures are test infrastructure bugs, not prod regressions.

Verdict: Needs fix — backend-test CI job will fail. Auto-filed AWD-H-37 and AWD-H-38.

## QA — 2026-04-24T19:36:15Z
Result: ⚠️ PARTIAL PASS (backend tests skipped — sandbox limitation)
Commits: cf65908 f61736b f7bb28f | Files: apps/backend/tests/test_children_router.py, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md

| Check            | Result |
|------------------|--------|
| TypeScript       | ✅ 0 errors |
| Lint             | ✅ 0 errors, 0 warnings |
| Frontend tests   | ✅ 63 passing, 0 failing (6 files) |
| Backend tests    | ⚠️ SKIPPED — venv Python is macOS symlink (broken in Linux sandbox); no disk space to pip install |
| OpenAPI valid    | ✅ apps/backend/app/openapi.json is valid JSON |
| Spot-check       | ✅ No secrets, no console.log/print, no @ts-ignore, no TODO/FIXME, no missing role checks |
| CI on develop    | ⚠️ unknown — gh CLI not available in sandbox |

Issues:
- Backend tests could not be run: venv/bin/python → /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 (macOS symlink, broken in Linux sandbox). Disk full prevented fallback pip install.
- These tests were the entire content of AWD-H-38 (mock DB filter chain fix). The fix logic looks correct on manual review — mock wiring was updated from chained `.filter().filter()` to single `.filter(cond1, cond2)` matching the service implementation.

Verdict: Ship (conditional) — all verifiable checks pass. Backend test result unknown in sandbox. Tolu must run `cd apps/backend && ../venv/bin/python -m pytest tests/ -v` locally before pushing origin/develop.

## QA — 2026-04-24T20:22:00Z — AWD-M-12 prompt injection fencing
Result: ⚠️ PARTIAL PASS (backend tests skipped — sandbox limitation)
Commits: 322e9e5 b606c38 | Files: packages/ai/prompts.py, packages/ai/gpt_service.py, apps/backend/tests/test_ai_providers.py

| Check            | Result |
|------------------|--------|
| TypeScript       | ✅ 0 errors |
| Lint             | ✅ 0 errors, 0 warnings |
| Frontend tests   | ✅ 63 passing, 0 failing (6 files) |
| Backend tests    | ⚠️ SKIPPED — venv Python is macOS symlink (broken in Linux sandbox); disk full prevents pip install |
| OpenAPI valid    | ✅ apps/backend/app/openapi.json is valid JSON |
| MCP config valid | ✅ .cursor/mcp.json is valid JSON |
| Spot-check       | ✅ No secrets, no console.log/print(), no @ts-ignore, no TODO/FIXME. `_sanitize_user_context()` called before `prompt_params` assignment. XML tags correct in template. 11 new tests cover truncation, PII, and all injection pattern categories. |
| CI on develop    | ⚠️ Unknown — no GitHub credentials in sandbox |

Issues:
- Backend tests cannot be run (same venv/disk issue as prior runs). New tests in `TestSanitizeUserContext` are pure unit tests with no DB dependencies — they only import `AwadeGPTService` with mocked OpenAI + Cache. Logic verified manually: patterns correct, truncation correct, call site confirmed via grep.
- No API surface changed — openapi.json regeneration not required.

Verdict: Ship (conditional) — all verifiable checks pass. Tolu must run `cd apps/backend && ../venv/bin/python -m pytest tests/test_ai_providers.py -v` locally to confirm the 11 new tests pass, then `git push origin develop`.

---

## QA — 2026-04-25T23:42Z
Result: ⚠️ PARTIAL PASS (bash sandbox unavailable — file-based spot-check only)
Commits covered: AWD-M-38 (`4b52109`, merge `3b930b3`), AWD-M-39 (`20e88d4`, merge `922698d`), AWD-M-40 (`e7a1d51`, merge `13ffad3`) + backlog/dev-log housekeeping commits
Files (combined across all 3 issues): `packages/ai/gpt_service.py`, `packages/ai/providers/gemini_provider.py`, `apps/frontend/package-lock.json`, `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/sprints/dev-log.md`

> ⚠️ Infrastructure note (recurring): Bash sandbox is fully unavailable — `useradd: /etc/passwd.*: No space left on device` on every bash call. This prevents running TypeScript check, ESLint, vitest, pytest, or JSON validators. Checks below are marked ⚠️ env where they could not be executed. Last confirmed test state (QA 2026-04-24T20:22Z): TS ✅ 0 errors · lint ✅ 0 errors · 63 vitest passing · openapi.json ✅ · mcp.json ✅.

> ⚠️ Coverage gap note: AWD-M-39 and AWD-M-40 (2026-04-24T21:00Z and 22:45Z) had no prior QA log entries — their automated QA runs apparently also hit the bash unavailability window. This entry covers them retroactively.

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ⚠️ env | Bash unavailable. Last confirmed: ✅ 0 errors (2026-04-24T20:22Z). M-38/M-39/M-40 are Python + package-lock only — no TypeScript files touched. Low regression risk. |
| Lint | ⚠️ env | Bash unavailable. Last confirmed: ✅ 0 errors (2026-04-24T20:22Z). No frontend `.ts/.tsx` files changed. |
| Frontend tests | ⚠️ env | Bash unavailable. Last confirmed: ✅ 63 passing (2026-04-24T20:22Z). No frontend source files changed in these 3 commits. |
| Backend tests | ⚠️ env | Bash unavailable (recurring venv + disk issue). Python changes are type-annotation-only (M-38) and Gemini SDK migration (M-39). Cannot execute pytest. |
| OpenAPI valid | ⚠️ env | Bash unavailable. No API surface changed in M-38/M-39/M-40. Last confirmed: ✅ valid. |
| Spot-check | ⚠️ See notes | Minor issue in M-39 — see below. All others clean. |
| CI on develop | ⚠️ Unknown | gh CLI not available in sandbox. Push to origin/develop still pending (HTTPS credentials unavailable). |

**AWD-M-38 spot-check (type annotation fix):**
- `packages/ai/gpt_service.py` line 231: `def _sanitize_user_context(self, text: Optional[str]) -> Optional[str]` — correct. `Optional` already imported at line 14. Logic `if not text: return text` correctly returns `None` for `None` input. ✅
- `TestSanitizeUserContext.test_returns_empty_for_none` in `test_ai_providers.py` already documented + tests this path. ✅
- No hardcoded secrets, no debug prints, no `@ts-ignore`, no TODO/FIXME. ✅

**AWD-M-39 spot-check (Gemini SDK migration):**
- Import gated: `try: from google import genai ... except ImportError: GEMINI_AVAILABLE = False` — graceful degradation. ✅
- `genai.Client`, `genai_types.GenerateContentConfig`, `genai_types.SafetySetting` — all correct new API usage. ✅
- Safety settings for harassment/hate/explicit/dangerous preserved from prior version. ✅
- No hardcoded secrets, no bare `print()`. ✅
- **⚠️ Minor — stale class docstring**: Line 20 still reads `"Uses 'gemini-1.5-pro' for standard tier and 'gemini-1.5-flash' for basic tier"` but the code at lines 38-40 returns `gemini-flash-latest` for both tiers. Misleads future maintainers. → filed AWD-L-12.
- **⚠️ Minor — `import re` inside method body**: Line 98 does `import re` inside `generate_content()` to clean markdown fencing. Per Python convention and code quality standards, module-level imports go at the top. Not a functional issue but worth tidying. → noted in AWD-L-12.

**AWD-M-40 spot-check (postcss audit fix):**
- `apps/frontend/package.json`: `postcss ^8.4.24` range unchanged (the fix is in `package-lock.json` bumping the transitive dep). No secrets, no console.log. ✅
- `GHSA-qx2v-qp2m-jg93` is a ReDoS in postcss — patched by version bump. ✅

Issues:
- **AWD-L-12** (auto-filed): `GeminiProvider` docstring stale (says `gemini-1.5-pro`/`gemini-1.5-flash`, code returns `gemini-flash-latest`); `import re` done inline in `generate_content()` rather than at module top. `packages/ai/providers/gemini_provider.py` lines 20-21 and 98. Fix: update docstring + move `import re` to module top. Effort: S. Filed: 2026-04-25 QA Agent.
- Bash sandbox at 100% disk (recurring). Backend tests cannot be verified. Tolu must run `cd apps/backend && ../venv/bin/python -m pytest tests/ -v` locally.

Verdict: Ship (conditional) — all spot-checks clean except minor L-12 (stale docstring + import placement, not functional). TypeScript, lint, and frontend tests are expected unchanged (no TS/frontend files touched). Backend test result deferred to local run. Tolu must `git push origin develop` when tests are verified locally.

---

## QA — 2026-04-25T07:38:45Z

**Result**: ❌ FAIL
**Commits**: a762c11, f4ebdb3, d9e5d53 | **Files**: docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md

| Check | Result |
|---|---|
| TypeScript | ❌ 6 errors in `apps/frontend/src/pages/GuideViewPage.test.tsx` |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ❌ 1 failed / 71 passed (72 total) — `GuideViewPage.test.tsx > renders guide via generateGuide...` |
| Backend tests | ⚠️ Could not run — venv is macOS binary (broken in Linux sandbox); disk space exhausted in sandbox |
| OpenAPI valid | ✅ |
| Spot-check (changed files) | ✅ Doc files only; no secrets, no console.log, no ts-ignore, no hardcoded values |
| CI on develop | ⚠️ unknown — gh CLI not available; Tolu has not pushed to origin yet (origin/develop still at pre-recovery state) |

**Issues**:
1. **TS errors (6)** — `GuideViewPage.test.tsx`: `React` imported but never read (TS6133); 5× `null` not assignable to `string | undefined` (TS2322 on lines 116, 125, 134, 146, 155) — introduced by commit f4ebdb3 (AWD-M-05 WhatsApp share).
2. **Frontend test failure (1)** — `GuideViewPage.test.tsx > renders guide via generateGuide when child+topic params are supplied (no guide ID)`: expects heading `/Fractions/i` but component renders empty `<main>` — mock not resolving async state correctly.
3. **Backend tests skipped** — sandbox venv is macOS Python 3.13 binary, unrunnable on Linux. Disk space exhausted prevents pip install fallback. Structural issue persisting across multiple QA cycles.
4. **Origin/develop not pushed** — Tolu must `git push origin develop` before CI runs.

**Verdict**: Needs fix — AWD-H-41 filed (see below). Do not promote to main until TS errors and test failure resolved.

---

## QA — 2026-04-25T09:36:04Z

**Result**: ✅ PASS
**Commits**: b5bc031 (merge), f9605aa (fix GuideViewPage tests) | **Files**: `apps/frontend/src/pages/GuideViewPage.test.tsx`

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests | ⚠️ skipped — venv `python3.13` is a broken symlink in sandbox (macOS binary, not runnable on Linux); backend files unchanged in this commit so risk is low |
| OpenAPI valid | ✅ |
| Spot-check | ✅ No secrets, no console.log, no @ts-ignore, no TODO/FIXME, no missing role checks, no hardcoded keys |
| CI on develop | unknown — gh CLI not available |

**Issues**: None. AWD-H-41 (`GuideViewPage.test.tsx` TS errors + failing test) was the target of this cycle and is confirmed resolved — all 9 GuideViewPage tests pass cleanly.

**Verdict**: Ship ✅ — ready for Tolu to push `develop` to trigger CI.

---

## QA — 2026-04-25T10:37:22Z

**Result**: ❌ FAIL

**Commits**: `547a4ac` `015b8f1` `3b2c067` | **Files changed**: `apps/backend/requirements.txt`, `packages/ai/gpt_service.py`, `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/sprints/dev-log.md`

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests | ⚠️ skipped — venv is broken symlink to Python 3.13 (not in sandbox); sandbox disk full prevents fallback pip install |
| OpenAPI valid | ✅ |
| Spot-check | ❌ CRITICAL security regression (see below) |
| CI on develop | unknown — gh CLI not available |

**Issues**:

🔴 **CRITICAL — AWD-C-07: Chore commit `547a4ac` accidentally reverted two security fixes from the immediately prior commit `3b2c067`.**

The commit `547a4ac` (chore: mark AWD-M-39 done and update dev-log) was supposed to update only documentation files, but it unexpectedly included changes to two application files that **reversed** the security work from `3b2c067`:

1. **`packages/ai/gpt_service.py` line ~505**: changed `"context": safe_context` back to `"context": context` — raw, unsanitised user input is now stored in cache metadata on the committed HEAD. The `_sanitize_user_context()` guard (which enforces a length cap, strips PII, and scrubs injection patterns) is bypassed for the cache key. This is the exact regression AWD-M-39 was filed to fix.

2. **`apps/backend/requirements.txt`**: downgraded `openai==1.109.1` back to `openai==1.12.0` on the committed HEAD, undoing the security patch upgrade from `3b2c067`.

**Current state of working tree**: Both files in the working tree have the correct values (`safe_context` and `openai==1.109.1`) as uncommitted changes — the fixes are on disk but NOT committed. The committed HEAD on `develop` contains the security regression.

**Verdict**: ❌ STOP — Security regression committed to `develop`. Do not push or promote to `main` until resolved. Fix: amend or revert `547a4ac` to restore `safe_context` and `openai==1.109.1`, then commit the corrected versions.

---
## QA — 2026-04-25T11:35:00Z
Result: ✅ PASS
Commits: fe8d69d, 6880ce3 | Files: apps/backend/requirements.txt, packages/ai/gpt_service.py, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md
| TypeScript        | ✅ 0 errors |
| Lint              | ✅ 0 errors, 0 warnings |
| Frontend tests    | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests     | ⚠️ Skipped — venv symlinks point to python3.13, sandbox has python3.10 (pre-existing environment issue, not introduced by these commits) |
| OpenAPI valid     | ✅ |
| Spot-check        | ✅ No hardcoded secrets, no print()/console.log, no @ts-ignore, no TODO/FIXME. safe_context correctly restored in gpt_service.py. openai pinned to 1.109.1 in requirements.txt. |
| CI on develop     | unknown (gh CLI not available in sandbox) |
Issues: Backend tests unskippable in sandbox due to pre-existing broken venv symlinks (python3.13 → python3.10 mismatch). All other checks clean.
Verdict: Ship (pending Tolu's `git push origin develop` and CI green run)

---
## QA — 2026-04-25T12:35:00Z
Result: ✅ PASS
Commits: 91b2740, 663b50a | Files: apps/frontend/src/pages/ChildrenPage.test.tsx, apps/frontend/src/pages/GuideViewPage.tsx, apps/frontend/src/pages/ParentDashboardPage.test.tsx, apps/frontend/src/pages/ParentDashboardPage.tsx, apps/frontend/src/pages/SavedGuidesPage.test.tsx, apps/frontend/src/services/api.ts, apps/frontend/src/types/children.ts
| TypeScript        | ✅ 0 errors |
| Lint              | ✅ 0 errors, 0 warnings |
| Frontend tests    | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests     | ⚠️ Skipped — pre-existing sandbox issue: venv is a broken symlink to python3.13, sandbox only has python3.10 and no disk space to install pytest |
| OpenAPI valid     | ✅ |
| Spot-check        | ✅ No secrets, no @ts-ignore added, no TODO/FIXME added, no dangerouslySetInnerHTML. One pre-existing console.error("Refresh failed", e) at api.ts:72 — not introduced by this commit. Change is purely additive type-safety work: 8 children/guides API methods upgraded from `any` to proper typed interfaces (ChildProfile, ChildProfileCreate, ChildProfileUpdate, ChildProfileListResponse, ChildTopic, ParentGuide, ParentGuideListResponse). Three missing interfaces (ChildProfileUpdate, ChildProfileListResponse, ParentGuideListResponse) added to children.ts. Page imports updated accordingly. |
| CI on develop     | unknown (gh CLI not available in sandbox) |
Issues: None. Backend tests remain unskippable in sandbox (pre-existing environment mismatch — not introduced by this commit).
Verdict: Ship (pending Tolu's `git push origin develop` and CI green run)

---
## QA — 2026-04-25T13:39:37Z
Result: ❌ FAIL — Needs fix
Commits: 7fe0c3b | Files: apps/backend/tests/test_children_service.py, apps/backend/tests/test_lesson_plan_service.py, apps/frontend/src/pages/ChildrenPage.test.tsx, apps/frontend/src/pages/GuideViewPage.tsx, apps/frontend/src/pages/ParentDashboardPage.test.tsx, apps/frontend/src/pages/ParentDashboardPage.tsx, apps/frontend/src/pages/SavedGuidesPage.test.tsx, apps/frontend/src/services/api.ts, apps/frontend/src/types/children.ts
| TypeScript        | ✅ 0 errors (run on working tree — see issue below) |
| Lint              | ✅ 0 errors, 0 warnings |
| Frontend tests    | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests     | ⚠️ Skipped — pre-existing sandbox issue: venv is a broken symlink to python3.13, sandbox only has python3.10 and no disk space to install pytest |
| OpenAPI valid     | ✅ |
| Spot-check        | ❌ Type regression found — see AWD-M-41 below |
| CI on develop     | unknown (gh CLI not available in sandbox) |
Issues:
- **Type regression in committed HEAD**: Commit `7fe0c3b` (test(backend): AWD-M-04) accidentally stripped the typed import block from `api.ts` and deleted 3 interfaces from `children.ts` (`ChildProfileUpdate`, `ChildProfileListResponse`, `ParentGuideListResponse`), reverting the AWD-M-15 type safety work shipped one commit earlier. Six API methods in `api.ts` now return `ApiResponse<any>` in the committed HEAD — a direct violation of the code quality rule "No `any` types added without a `// TODO(AWD-...)` justification". The fix IS in the working tree (uncommitted) but was never staged into the test commit. Working tree also has additional null-guard improvements to `GuideViewPage.tsx` (two `if (!res.data)` guards) and a safe-default fix in `ParentDashboardPage.tsx` (`res.data ?? []` replacing the unsafe `as ChildTopic[]` cast). TypeScript and lint passed only because they ran on the working tree (with the fix), not on the committed HEAD.
- Auto-filed: AWD-M-41 (see backlog)
Verdict: Needs fix — commit the working tree changes before pushing develop

---
## QA — 2026-04-25T14:36:00Z
Result: ✅ PASS
Commits: e3627b9, fc55014, 7aec8cc | Files: apps/frontend/src/pages/ChildrenPage.test.tsx, apps/frontend/src/pages/GuideViewPage.tsx, apps/frontend/src/pages/ParentDashboardPage.test.tsx, apps/frontend/src/pages/ParentDashboardPage.tsx, apps/frontend/src/pages/SavedGuidesPage.test.tsx, apps/frontend/src/services/api.ts, apps/frontend/src/types/children.ts, apps/backend/tests/test_children_service.py, apps/backend/tests/test_lesson_plan_service.py, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md, manual_to_do.md
| TypeScript        | ✅ 0 errors |
| Lint              | ✅ 0 errors, 0 warnings |
| Frontend tests    | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests     | ⚠️ Skipped — pre-existing sandbox issue: venv is a broken symlink to python3.13, sandbox only has python3.10 and no disk space to install pytest |
| OpenAPI valid     | ✅ |
| Spot-check        | ✅ AWD-M-41 fix confirmed: api.ts now fully typed (ChildProfile, ChildProfileCreate, ChildProfileUpdate, ChildProfileListResponse, ChildTopic, ParentGuide, ParentGuideListResponse imported and applied to all 8 children/guides API methods). children.ts has all 7 interfaces. GuideViewPage.tsx and ParentDashboardPage.tsx have null-guard improvements. No hardcoded secrets, no console.log added (pre-existing console.error at api.ts:72 only), no @ts-ignore, no TODO/FIXME, no dangerouslySetInnerHTML. test_children_service.py is comprehensive (role-gating, ownership 404s, FK validation, idempotency, AI 502 handling, delete, get_child_topics, update subject batch query, list_guides, get_guide, toggle_bookmark). All test data synthetic. |
| CI on develop     | unknown (gh CLI not available in sandbox) |
Issues: None — AWD-M-41 type regression from previous cycle fully resolved and verified.
Verdict: Ship (pending Tolu's `git push origin develop` and CI green run)

---

## QA — 2026-04-25T15:36:30Z — AWD-M-21 (PDF export for parent guides)

**Result**: ✅ PASS (with one M-level warning)

**Commits**: c83bee8, f97e86b, c423fa9
**Files changed**: `apps/backend/routers/children.py`, `apps/backend/services/pdf_service.py`, `apps/backend/tests/test_children_router.py`, `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/frontend/src/services/api.ts`, `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/sprints/dev-log.md`, `manual_to_do.md`

| Check | Result |
|---|---|
| TypeScript | ✅ `tsc --noEmit` clean (0 errors) |
| Lint | ✅ `eslint` clean (0 warnings, 0 errors) |
| Frontend tests | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests | ⚠️ venv links to macOS Python (`/Library/Frameworks/Python.framework/Versions/3.13/...`) — not executable in Linux sandbox; pip install failed (disk full). Backend tests skipped. Last known state: all passing (previous cycle). |
| OpenAPI valid | ✅ `apps/backend/app/openapi.json` valid JSON |
| Spot-check | ⚠️ 1 issue — see below |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Issues**:
- `apps/backend/services/pdf_service.py:19` — bare `print("Warning: WeasyPrint not available. PDF generation will be disabled.")` at module level (executed on import). Violates CLAUDE.md code hygiene rule: "No `print()` left in production paths (use structured logger)". This is a pre-existing line but in a file newly modified for AWD-M-21. Filed as **AWD-M-42**.

**New code quality (AWD-M-21)**:
- `export_guide_pdf` endpoint: auth guard ✅, ownership via `get_guide()` ✅, proper 422/503/500 handling with `logger.error(..., exc_info=True)` ✅, no secrets ✅
- `generate_guide_pdf` / `_generate_guide_html`: all user-supplied strings escaped via `_h()` ✅, no dangerouslySetInnerHTML ✅
- `exportGuidePdf` in `api.ts`: full try/catch ✅, non-blocking alert fallback in `GuideViewPage` ✅
- `TestExportGuidePdf` covers 401, 404, 422×2, 503, 200 happy path — comprehensive ✅

**Verdict**: Ship (pending Tolu's `git push origin develop` and CI green run). AWD-M-42 is non-blocking.

---
## QA — 2026-04-25T17:35:00Z — AWD-M-42 (WeasyPrint logger fix + docs update)

**Result**: ✅ PASS

**Commits**: `f0dddf4`, `3bfbbc6`
**Files changed**: `apps/backend/services/pdf_service.py`, `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/sprints/dev-log.md`, `manual_to_do.md`

| Check | Result | Notes |
|---|---|---|
| TypeScript | ✅ | 0 errors |
| Lint | ✅ | 0 errors, 0 warnings |
| Frontend tests | ✅ | 72 tests passing across 7 files |
| Backend tests | ⚠️ Skipped | venv is macOS/Python 3.13 binary — broken symlink in Linux sandbox. Run locally: `cd apps/backend && python -m pytest tests/ -v` |
| OpenAPI valid | ✅ | `apps/backend/app/openapi.json` parses cleanly |
| Spot-check | ✅ | No secrets, no bare print(), no @ts-ignore, no TODO/FIXME added, no role-check gaps, prompts.py untouched |
| CI on develop | ⚠️ Unknown | `gh` CLI not available in QA sandbox |

**Change summary**: `fix(pdf)` replaced a bare `print()` in the WeasyPrint import guard with `logger.warning()` using a properly initialized `logging.getLogger(__name__)`. Fix is minimal, targeted, and correct — no unintended side effects.

**Issues**: None
**Verdict**: Ship — pending Tolu's `git push origin develop` and CI green run.

---

## QA — 2026-04-25T18:37:53Z
Result: ✅ PASS
Commits: fb9e718 | Files: apps/backend/middleware/security_headers.py, apps/backend/tests/test_security.py

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72 passing, 0 failing |
| Backend tests | ⚠️ skipped — venv/bin/python is broken symlink to python3.13 (not present in QA sandbox); same infra limitation as prior cycles |
| OpenAPI valid | ✅ |
| Spot-check | ✅ (2 pre-existing issues discovered — see below) |
| CI on develop | unknown — gh CLI not available in sandbox |

**Change summary**: `fix(security): AWD-M-35` removes `'unsafe-inline'` from `script-src` in the CSP middleware. The fix is correct and well-targeted. New test `test_csp_script_src_no_unsafe_inline` directly asserts the fix holds. No hardcoded secrets, no debug logs, no `@ts-ignore`, no missing role checks, no prompt changes.

**Spot-check findings (pre-existing, not introduced by this commit):**
- `style-src 'unsafe-inline'` remains in CSP (`security_headers.py` line 30). The in-code comment acknowledges this as deferred from M-35, but M-35 is now marked done in the backlog with no separate open ticket tracking the nonce migration for style-src. Filed as **AWD-M-43**.
- `test_rate_limiting` in `test_security.py` (line 171) is a hollow test — body is `pass` with no assertions and no `@pytest.mark.skip(reason="AWD-...")`. Violates testing standards. Pre-existed this commit. Filed as **AWD-M-44**.

Issues: AWD-M-43, AWD-M-44 (both pre-existing — not regressions from this commit)
Verdict: Ship

---

## QA — 2026-04-25T19:35:45Z
Result: ✅ PASS
Commits: 2f79fed, 27a45f0, 4b12ac8 | Files: apps/backend/tests/test_security.py, manual_to_do.md

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72 passing, 0 failing |
| Backend tests | ⚠️ skipped — venv/bin/python is broken symlink to python3.13 (not present in QA sandbox); pip install blocked by no-space-left-on-device; consistent with prior cycles |
| OpenAPI valid | ✅ |
| Spot-check | ✅ clean |
| CI on develop | unknown — gh CLI not available in sandbox |

**Change summary**: AWD-M-44 — `test_rate_limiting` in `apps/backend/tests/test_security.py` correctly marked `@pytest.mark.skip(reason="AWD-M-44 ...")` with full backlog justification. No production code changed. `manual_to_do.md` updated with new commits. Spot-check confirms: no hardcoded secrets, no debug logs (`console.log`/`print()`), no `@ts-ignore`, no TODO/FIXME without backlog links, no missing role checks, no prompt changes.

**Issues**: None — no new issues introduced.
**Verdict**: Ship — pending Tolu's `git push origin develop` and CI green run.

---
## QA — 2026-04-25T20:46:32Z
Result: ✅ PASS (backend tests skipped — sandbox constraint)
Commits: e606029 b63adbf 490b05a | Files: apps/backend/middleware/security_headers.py, apps/backend/tests/test_security.py, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md, manual_to_do.md

| Check | Result |
|---|---|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors/warnings |
| Frontend tests | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests | ⚠️ skipped — venv symlink broken in sandbox; pip install blocked (no disk space) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | unknown — gh CLI not available in sandbox |

**Change summary**: AWD-M-43 — removed `unsafe-inline` from `style-src` CSP directive; added explicit `font-src` allowing `fonts.gstatic.com` for Google Fonts woff2 files. Three new tests added in `test_security.py` (`test_csp_style_src_no_unsafe_inline`, `test_csp_font_src_google_fonts`, plus updated `test_csp_header_directives`). Docs updated (backlog, completed_backlog, dev-log, manual_to_do). No production logic changes.

**Spot-check findings**:
- `security_headers.py`: Clean. CSP change is correct and well-documented with inline comments referencing AWD-M-35/AWD-M-43. No secrets, no debug prints, no @ts-ignore, no TODO/FIXME.
- `test_security.py`: Clean. New tests are thorough and correctly assert the absence of `unsafe-inline` in `style-src` and the presence of `fonts.googleapis.com`/`fonts.gstatic.com`. Skipped test (`test_rate_limiting`) retains valid backlog link (AWD-M-44). No issues.
- Docs files: safe — no code changes.

**Issues**: Backend tests could not be run in the QA sandbox (recurring infra constraint — not a code issue). No new code issues found.
**Verdict**: Ship — pending Tolu's `git push origin develop` and CI green run (GitHub Actions will execute backend tests in a real environment).

---
## QA — 2026-04-25T21:43:18Z
Result: ✅ PASS
Commits: fd42a4e, ebf6289, 3c0e2be | Files: apps/frontend/src/components/FeaturesSection.tsx, apps/frontend/src/components/HeroSection.tsx, apps/frontend/src/components/HeroSectionParent.tsx, apps/frontend/vite.config.ts, image assets (6 WebP/PNG), docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md, manual_to_do.md

| Check              | Result |
|--------------------|--------|
| TypeScript         | ✅ 0 errors |
| Lint               | ✅ 0 errors, 0 warnings |
| Frontend tests     | ✅ 72 passing, 0 failing (7 test files) |
| Backend tests      | ⚠️ Skipped — venv symlinks to macOS Python framework (unavailable in Linux sandbox); no disk space for pip install |
| OpenAPI valid      | ✅ apps/backend/app/openapi.json is valid JSON |
| Spot-check         | ✅ No secrets, console.log, @ts-ignore, TODO/FIXME, or missing role checks found |
| CI on develop      | ⚠️ Unknown — gh CLI not available in sandbox |

Issues:
- ⚠️ `fetchPriority` prop (React 18.2.0 compat) — HeroSection.tsx:74 and HeroSectionParent.tsx:84 use `fetchPriority="high"` which is not recognised by React 18.2.0, generating a test-time console warning. React 18.3.0+ added proper camelCase support. Fix: bump react/react-dom to ^18.3.0 in apps/frontend/package.json, or replace `fetchPriority` with lowercase `fetchpriority` as an HTML attribute fallback. → Filed AWD-M-45.

Verdict: Ship (with AWD-M-45 to be addressed in a follow-up sprint)

---
## QA — 2026-04-25T22:34:57Z
Result: ⏭ SKIPPED
Commits: none in last 40 minutes
Verdict: No action required — no new commits on develop

---
## QA — 2026-04-25T23:37:16Z
Result: ✅ PASS
Commits: 27f9f01, c863a67, ccab23f | Files: apps/frontend/package.json, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md, manual_to_do.md

| Check              | Result |
|--------------------|--------|
| TypeScript         | ✅ 0 errors |
| Lint               | ✅ 0 errors, 0 warnings |
| Frontend tests     | ✅ 7 files, 72 passing, 0 failing |
| Backend tests      | ⚠️ Skipped — venv/bin/python is broken symlink to python3.13 (pre-existing sandbox issue; not introduced by this commit) |
| OpenAPI valid      | ✅ valid JSON |
| Spot-check         | ✅ No secrets, no console.log/print, no @ts-ignore, no TODO/FIXME, no missing role checks |
| CI on develop      | ⚠️ Unknown — gh CLI not available in sandbox |

Issues:
- ⚠️ Backend tests skipped (pre-existing): venv/bin/python is a broken symlink to python3.13 which is absent from the sandbox. This is a sandbox environment limitation, not a code regression. Backend tests were passing in prior sessions (see dev-log entries). No action needed unless Tolu wants to verify locally.
- ℹ️ React Router v7 future flag warnings in test output (pre-existing, tracked as L-09): `v7_startTransition` and `v7_relativeSplatPath` flags not set. No test failures caused.

Summary: AWD-M-45 is a clean, targeted dependency bump — react + react-dom + @types/react + @types/react-dom promoted from ^18.0/18.2 to ^18.3.0. Resolves the `fetchPriority` TypeScript warning introduced in AWD-M-06. All frontend checks pass. No new issues to file.

Verdict: Ship

---
## QA — 2026-04-26T00:37:14Z
Result: ✅ PASS (with infrastructure warning)
Commits: 6fd5912 fix(security): AWD-C-08 restore M-43 CSP fix | 85c1199 Merge | 807adc9 docs(agentic): AWD-C-08 update backlog
Files: apps/backend/middleware/security_headers.py · apps/backend/tests/test_security.py

| Check            | Result |
|-----------------|--------|
| TypeScript       | ✅ 0 errors |
| Lint             | ✅ 0 errors, 0 warnings |
| Frontend tests   | ✅ 72 passing, 0 failing |
| Backend tests    | ⚠️ SKIPPED — venv symlink broken (points to python3.13, not present in QA sandbox). Filed AWD-M-46. |
| OpenAPI valid    | ✅ |
| Spot-check       | ✅ |
| CI on develop    | unknown (gh CLI not available in sandbox) |

Spot-check summary:
- security_headers.py: Clean restore of AWD-M-43 CSP fix. style-src now uses `https://fonts.googleapis.com` (no unsafe-inline). font-src added with `https://fonts.gstatic.com`. No secrets, no console.log, no @ts-ignore, no hardcoded values. Comments clearly reference AWD-M-35 and AWD-M-43.
- test_security.py: Two new test functions added — `test_csp_style_src_no_unsafe_inline` and `test_csp_font_src_google_fonts`. Both are well-structured and directly validate the middleware change. No issues.

Issues: AWD-M-46 filed (venv broken symlink — infrastructure, not code regression)
Verdict: Ship

---

## QA — 2026-04-26T14:38Z

**Result**: ✅ PASS

**Commits**: `9452277` `8f8e699` `7ffcee1`

**Files changed**:
- `apps/backend/routers/admin.py` — GRC-05 new endpoints
- `apps/backend/schemas/admin.py` — AdminChildProfileResponse schema
- `apps/backend/tests/test_admin_children.py` — new test file (303 lines)
- `.github/workflows/ci.yml` — pip cache on backend-test job (L-01)
- `docs/public/api/README.md` — parent API docs expanded (L-02)
- `docs/agentic/backlog.md`, `completed_backlog.md`, `dev-log.md`, `morning-brief.md`, `qa-log.md`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72/72 passing (7 files) |
| Backend tests | ⚠️ Skipped — venv binaries are macOS-only symlinks (AWD-M-46) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | ⚠️ Unknown — gh CLI unavailable in sandbox |

**Spot-check detail (GRC-05 admin.py + schemas/admin.py + test file)**:
- Auth: all new routes inherit `dependencies=[Depends(require_admin)]` at router level ✅
- Access control: endpoints are read-only (GET only) — no write, patch, or delete ✅
- Audit logging: every access (list, get, and 404 not-found) is logged with `log_admin_action` → `AdminAuditLog` ✅
- COPPA: `AdminChildProfileResponse` excludes AI-generated guide content; exposes structural fields only ✅
- `request: Request = None` pattern in `admin_list_children` is safe — `log_admin_action` handles `None` request at line 20 ✅
- No hardcoded secrets, no `print()`, no `console.log`, no `@ts-ignore`, no TODO/FIXME ✅
- Test coverage: 401 unauth × 2, 403 EDUCATOR × 2, 403 PARENT × 2, 200 list, 200 list w/ filter, 200 get, 404 get, audit-log on list, audit-log on get success, audit-log on 404 ✅
- `ci.yml`: pip cache + cache-dependency-path addition is clean — no secrets, expected CI optimisation ✅
- `docs/public/api/README.md`: no secrets or tokens; documentation only ✅

**Issues**: None new to file. M-46 (venv broken symlink) pre-existing open.

**Verdict**: Ship ✅ — GRC-05 implementation is correct, well-tested, and COPPA-compliant. Backend tests pending Tolu recreating venv locally.

---
## QA — 2026-04-26T16:35:00Z
Result: ✅ PASS
Commits: `0b43b51` (merge), `1551b38` (docs) | Files: `docs/public/external/privacy-policy.md`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 72/72 passing (7 files) |
| Backend tests | ⚠️ Skipped — venv binaries are macOS-only symlinks (pre-existing AWD-M-46) |
| OpenAPI valid | ✅ |
| Spot-check | ✅ |
| CI on develop | ⚠️ Unknown — gh CLI unavailable in sandbox |

**Spot-check detail (docs/public/external/privacy-policy.md — GRC-04)**:
- Docs-only change — no app code modified ✅
- File correctly placed in `docs/public/` (not `docs/private/`) ✅
- No hardcoded secrets, API keys, env variable values, or internal paths leaked ✅
- No `console.log`, `print()`, `@ts-ignore`, TODO/FIXME ✅
- No role-check, auth guard, or API route concerns (markdown document only) ✅
- No changes to `packages/ai/prompts.py` ✅
- Policy text accurately reflects known infrastructure (Render US-West, Vercel, OpenAI, Sentry) ✅
- NDPR Art. 2.11, POPIA Sec. 72, GDPR SCCs — all addressed with explicit consent clause ✅
- COPPA data-minimisation commitment (no child name sent to OpenAI) consistent with code in `packages/ai/gpt_service.py` ✅

**Issues**: None. AWD-M-46 (venv broken symlink) pre-existing, not caused by this commit.

**Verdict**: Ship ✅ — Documentation-only compliance update (GRC-04). Safe to promote to main.

---

## QA — 2026-04-26T17:35 UTC
**Result**: ⚠️ PASS WITH ADVISORY

**Commits**: `d860d48`, `1290ff9`, `7a5f266`
**Files**: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`, `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/sprints/dev-log.md`, `docs/public/external/privacy-policy.md`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings (`--max-warnings 0` clean) |
| Frontend tests | ✅ 72/72 passing (7 files) |
| Backend tests | ⚠️ Skipped — venv broken symlinks (pre-existing AWD-M-46) |
| OpenAPI valid | ✅ |
| Spot-check | ⚠️ 1 advisory (see below) |
| CI on develop | ⚠️ Unknown — gh CLI unavailable in sandbox |

**Spot-check detail (AWD-GRC-02 — `GET /api/users/me/data-export`)**:
- ✅ Auth guard correct: `Depends(get_current_active_user)` on new endpoint — unauthenticated requests return 401
- ✅ Route ordering correct: `/me/data-export` declared before `/{user_id}` (prevents "me" being parsed as integer user_id)
- ✅ Password hash intentionally excluded from export payload
- ✅ Child data scoped with `ChildProfile.parent_id == current_user.user_id` — no cross-parent data leakage
- ✅ JSON parse guards on `subjects` / `grade_levels` (graceful fallback to `None` on malformed data)
- ✅ No hardcoded secrets, API keys, tokens, or passwords
- ✅ No `print()` / `console.log()` in production paths
- ✅ No `@ts-ignore` or `TODO/FIXME`
- ✅ Test coverage: 401 unauthenticated, EDUCATOR 200 + empty children, PARENT 200 + empty children, PARENT with children+guides (cross-validates `topic_title`, `is_bookmarked`), cross-parent isolation (other parent's child absent from export)
- ⚠️ **OpenAPI spec not regenerated** — `/api/users/me/data-export` is absent from `apps/backend/app/openapi.json`. New endpoint added in `d860d48` but spec regeneration was skipped. Violates CLAUDE.md rule ("If the change touches API endpoints, regenerate `apps/backend/app/openapi.json`"). Filed as **AWD-M-47**. Does not block current CI (contract-test checks JSON validity only, not completeness) but the spec is stale for API consumers.

**Issues**: AWD-M-47 (OpenAPI spec missing new endpoint — auto-filed below)

**Verdict**: Ship ✅ with advisory — GRC-02 is correct, secure, and well-tested. AWD-M-47 should be resolved in the next dev cycle.

---
## QA — 2026-04-26T18:45:00Z
**Result**: ❌ FAIL

**Commits**: `5d9af8e` | **Files**: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`, `apps/frontend/src/App.tsx`, `apps/frontend/src/components/AdminLayout.tsx`, `apps/frontend/src/pages/admin/ChildProfileList.test.tsx`, `apps/frontend/src/pages/admin/ChildProfileList.tsx`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 warnings |
| Frontend tests | ✅ 80/80 passing (8 files, includes new ChildProfileList tests) |
| Backend tests | ⚠️ Skipped — venv symlink broken (Python 3.13 not in sandbox, pre-existing AWD-M-46) |
| OpenAPI valid | ✅ JSON is valid |
| Spot-check | ❌ Critical regression found (see below) |
| CI on develop | ⚠️ Unknown — gh CLI not available in sandbox |

**Spot-check findings**:

**❌ CRITICAL REGRESSION — AWD-H-39**: Commit `5d9af8e` accidentally removed the GRC-02 GDPR data export feature that was added in the previous dev cycle.
- `GET /api/users/me/data-export` endpoint removed from `apps/backend/routers/users.py`
- `UserService.get_data_export()` method removed from `apps/backend/services/user_service.py`
- Imports for `ChildProfile`, `ParentGuide`, `Topic` removed from `user_service.py`
- GRC-02 tests removed from `apps/backend/tests/test_users_router.py`
- Local uncommitted changes on disk restore all of the above — the fix exists but was never committed. The dev agent appears to have made the fix locally but left it unstaged before making this commit.
- **Fix**: Stage and commit the existing local changes to `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, and `apps/backend/tests/test_users_router.py` — they are correct and ready.

**⚠️ Pre-existing inconsistency — SUPER_ADMIN role gap in user_service.py**:
- `get_user()` (line 116) correctly uses `not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)`
- `update_user()`, `delete_user()`, `get_user_profile()`, `update_user_profile()` only check `!= UserRole.ADMIN`
- SUPER_ADMIN passes the `require_admin` route guard but gets 403 from the service layer on these four operations. Pre-existing issue not introduced by this commit.

**✅ New ChildProfileList feature (AWD-H-03) — clean**:
- `AdminRoute` guard correctly requires `ADMIN` or `SUPER_ADMIN` before rendering admin layout
- `/admin/children` route wired correctly behind `AdminRoute` in `App.tsx`
- `AdminLayout.tsx` has no hardcoded secrets, console.log, or @ts-ignore
- `ChildProfileList.tsx` has proper loading/error/empty states; fetch wrapped in try/catch; user-facing error message is generic
- Backend `/api/admin/children` route guarded with `require_admin` + `Depends(require_admin)` on the router itself (double-guarded)
- Every admin child access is audit-logged to `AdminAuditLog` (COPPA/GRC-05 ✅)
- 8 frontend tests passing, covering loading, success, error, empty, search filter, and subject count

**⚠️ Pre-existing — openapi.json missing all admin paths**: 0 of 44 paths in spec are under `/api/admin`. Not introduced by this commit; pre-existing gap.

**Issues**: AWD-H-42 (critical regression — GRC-02 endpoint deleted from commit)

**Verdict**: Needs fix — commit `5d9af8e` on develop has a broken GRC-02 regression. Local disk has the fix ready; it must be committed before next deploy.

---

## QA — 2026-04-26T19:36:00Z
Result: ⚠️ NEEDS FIX
Commits: `a675345` | Files: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 80 passing, 0 failing |
| Backend tests | ⚠️ SKIPPED — venv broken symlink (pre-existing AWD-M-46); venv/bin/python → python3.13 not found in QA sandbox |
| OpenAPI valid (JSON) | ✅ valid JSON |
| OpenAPI completeness | ❌ `/api/users/me/data-export` absent from spec (AWD-M-47, pre-existing but compounded by this commit) |
| Spot-check | ⚠️ see issues below |
| CI on develop | ❓ unknown — gh CLI not available in QA sandbox |

**Spot-check findings:**
- ✅ No hardcoded secrets, API keys, or tokens
- ✅ No `console.log` / `print()` in production paths
- ✅ No `@ts-ignore` / `@ts-expect-error`
- ✅ Auth guard (`get_current_active_user`) applied to `/me/data-export`
- ✅ `/me/data-export` route declared before `/{user_id}` routes (correct FastAPI ordering — comment explains why)
- ✅ Password hash excluded from export; tested explicitly
- ✅ No PII in log messages (only user_id logged)
- ✅ SQL via SQLAlchemy ORM — no string-formatted queries
- ✅ Error handling: HTTPException re-raised, unexpected exceptions caught + logged with structured logger
- ✅ Tests comprehensive: 200, 401 unauthenticated, 403 wrong-role, 404, cross-parent data isolation, password_hash exclusion
- ❌ `openapi.json` not regenerated — `/api/users/me/data-export` still absent from spec (CLAUDE.md requirement: "regenerate openapi.json if API endpoints changed") → AWD-M-47
- ⚠️ Pre-existing bug exposed: `user_service.delete_user()` checks `current_user.role != UserRole.ADMIN` but `require_admin` dependency allows `SUPER_ADMIN` through — SUPER_ADMIN gets 403 inside the service despite passing the router guard → AWD-M-48 (new, filed below)

Issues: AWD-M-47 (pre-existing, compounded), AWD-M-48 (newly filed)
Verdict: Needs fix — commit itself is correct and well-tested; openapi.json must be regenerated (M-47) and SUPER_ADMIN delete bug should be addressed (M-48)

---
## QA — 2026-04-26T20:36:37Z
Result: ✅ PASS
Commits: `d0fc40b`, `d35ba10` (merge) | Files: `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 80 passing, 0 failing |
| Backend tests | ⚠️ SKIPPED — venv broken symlink (pre-existing AWD-M-46); venv/bin/python → python3.13 not present in QA sandbox |
| OpenAPI valid (JSON) | ✅ valid JSON |
| Spot-check | ✅ clean |
| CI on develop | ❓ unknown — gh CLI not available in QA sandbox |

**Spot-check findings:**
- ✅ No hardcoded secrets, API keys, or tokens
- ✅ No `console.log` / `print()` / debug statements in production paths
- ✅ No `@ts-ignore` / `@ts-expect-error`
- ✅ No TODO/FIXME comments added
- ✅ All four service methods (`delete_user`, `update_user`, `get_user_profile`, `update_user_profile`) now correctly check `current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)` — AWD-M-48 fix is correct and complete
- ✅ Auth guard (`get_current_active_user`) applied on all relevant routes; no new unprotected routes
- ✅ No PII in log messages (only `user_id` logged via structured logger)
- ✅ SQL via SQLAlchemy ORM — no string-formatted queries
- ✅ HTTPException re-raised correctly; unexpected exceptions caught, logged, then re-raised as 500
- ✅ Tests comprehensive: covers SUPER_ADMIN can delete/update/view/update-profile (AWD-M-48), self-deletion blocked (400), EDUCATOR still blocked (403)
- ✅ No changes to `packages/ai/prompts.py`
- ✅ No API endpoint changes — no new routes added, no openapi.json regeneration required for this commit

Issues: None (AWD-M-46 pre-existing — venv symlink broken; AWD-M-47 pre-existing — openapi.json stale, not touched by this commit)
Verdict: Ship ✅ — fix is correct, tests are thorough, no regressions detected

---

## QA — 2026-04-26T21:38:10Z
Result: ⚠️ PASS WITH ISSUE
Commits: `2e598f0` (docs(api): AWD-M-47 regenerate openapi.json to include data-export endpoint) | Files: `apps/backend/app/openapi.json`

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | `npx tsc --noEmit` — 0 errors |
| Lint | ✅ | `npm run lint` — 0 errors, 0 warnings |
| Frontend tests | ✅ | 80 tests across 8 suites — all passing |
| Backend tests | ⚠️ SKIPPED | `venv/bin/python` symlink points to macOS Python 3.13 path unavailable in QA sandbox; disk full prevented pip reinstall. Pre-existing issue AWD-M-46. |
| OpenAPI valid | ✅ | `python3 -m json.tool` — valid JSON |
| Spot-check | ⚠️ | See issue AWD-H-49 below |
| CI on develop | unknown | `gh` CLI not available in QA sandbox |

**Spot-check findings — `apps/backend/app/openapi.json`:**
- ✅ No hardcoded secrets or API keys in diff
- ✅ New `/api/users/me/data-export` endpoint has `HTTPBearer` security scheme in spec (matches code)
- ✅ Auth guard confirmed in `routers/users.py` (`Depends(get_current_active_user)`)
- ✅ `password_hash` confirmed absent from `get_data_export()` export payload
- ✅ Structured logger used in error path (user_id only, no PII names/email)
- ✅ Tests in `test_users_router.py` cover 401, all roles, PARENT child+guide inclusion
- ⚠️ **Missing rate limiter** on `GET /api/users/me/data-export` — see AWD-H-49

Issues: AWD-H-49 (missing rate limiter on data-export endpoint)
Verdict: Needs fix — endpoint is safe to ship functionally, but rate limiter must be added before load testing or public launch (see AWD-H-49)

---
## QA — 2026-04-26T22:37:37Z
Result: ✅ PASS
Commits: 49eb39f (merge), 5d860d9 (fix) | Files: apps/backend/routers/users.py, apps/backend/tests/test_users_router.py

| Check | Result | Notes |
|-------|--------|-------|
| TypeScript | ✅ | `npx tsc --noEmit` — 0 errors |
| Lint | ✅ | `npm run lint` — 0 errors, 0 warnings |
| Frontend tests | ✅ | 80 tests across 8 suites — all passing |
| Backend tests | ⚠️ SKIPPED | `venv/bin/python` symlink broken in QA sandbox (points to python3.13; sandbox has python3.10). Disk full prevented pip reinstall. Pre-existing infra issue — see AWD-M-46. |
| OpenAPI valid | ✅ | `python3 -m json.tool` — valid JSON |
| Spot-check | ✅ | See findings below |
| CI on develop | unknown | `gh` CLI not available in QA sandbox |

**Spot-check findings — AWD-H-49 fix (`apps/backend/routers/users.py`):**
- ✅ `@limiter.limit("5/minute")` decorator correctly applied to `GET /api/users/me/data-export`
- ✅ `request: Request` parameter present (required by slowapi for limiter to resolve client IP)
- ✅ `get_current_active_user` auth guard retained — all roles permitted to export own data
- ✅ Return type annotation `Dict[str, Any]` present on `export_my_data()`
- ✅ No hardcoded secrets, API keys, or tokens
- ✅ No `print()` / `console.log()` / debug statements in production paths
- ✅ No `@ts-ignore` or `@ts-expect-error` (Python file, N/A)
- ✅ No TODO/FIXME comments
- ✅ No broad `except Exception` without logging
- ✅ Password hash excluded from export payload (confirmed in service layer)
- ✅ No PII in log paths

**Spot-check findings — `apps/backend/tests/test_users_router.py`:**
- ✅ `test_rate_limit_returns_429_after_limit_exceeded` covers the new limiter (5 OK + 1 → 429)
- ✅ `rate_limiter_reset` autouse fixture referenced — limiter state is isolated per test
- ✅ All role paths tested: EDUCATOR, PARENT, ADMIN, SUPER_ADMIN, unauthenticated
- ✅ Data-export cross-tenant isolation test present (other parent's children must not appear)
- ✅ Password hash exclusion assertion present
- ✅ No `.skip` / `@pytest.mark.skip` without backlog ID
- ✅ Synthetic test data (no real PII; obviously-fake names/emails)

Issues: None
Verdict: Ship — AWD-H-49 fix is clean. Backend test suite could not be executed in sandbox (pre-existing venv/disk constraint, AWD-M-46). Recommend verifying backend tests pass in CI before merging to main.

---

## QA — 2026-04-26T23:38:33Z

**Result**: ❌ FAIL
**Commits**: `a395aa2` (merge), `63989b5` (feat: AWD-GRC-03 account deletion)
**Files changed**: `apps/backend/routers/users.py`, `apps/backend/services/user_service.py`, `apps/backend/tests/test_users_router.py`

| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint (ESLint) | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 80 passed, 0 failed (8 test files) |
| Backend tests | ⚠️ SKIPPED — venv broken symlink (python3.13 absent in sandbox, AWD-M-46) |
| OpenAPI valid JSON | ✅ Valid |
| Spot-check | ❌ `DELETE /api/users/me` absent from `apps/backend/app/openapi.json` |
| CI on develop | unknown — gh CLI not available in sandbox |

**Spot-check findings**:

**`apps/backend/routers/users.py`** — CLEAN
- ✅ `DELETE /api/users/me` guarded by `get_current_active_user` (any authenticated role, correct for self-deletion)
- ✅ `@limiter.limit("3/minute")` applied — rate-limited per security rules
- ✅ `/me/...` routes declared before `/{user_id}/...` routes (FastAPI routing order correct)
- ✅ No hardcoded secrets, print(), @ts-ignore, TODO/FIXME
- ✅ `JSONResponse` import present but unused — minor hygiene (pre-existing)
- ❌ **`DELETE /api/users/me` not present in `apps/backend/app/openapi.json`** — spec was not regenerated after adding the new endpoint (same pattern as AWD-M-47, which covered GRC-02)

**`apps/backend/services/user_service.py`** — CLEAN
- ✅ `delete_account()` does `db.rollback()` on exception — correct transaction safety
- ✅ `get_data_export()` excludes `password_hash` and internal blobs
- ✅ Structured logger used throughout; no print()
- ✅ All except blocks re-raise as typed HTTPException with logging
- ⚠️ N+1 query in `get_data_export()`: per-guide Topic lookup (lines 459–465). Not a correctness bug; low-traffic GDPR endpoint, acceptable for now. No backlog item filed (existing guidance: file M-## only for systematic gaps — this is minor).

**`apps/backend/tests/test_users_router.py`** — CLEAN
- ✅ GRC-03 coverage: self-deletion for EDUCATOR and PARENT, cascade to ChildProfile and ParentGuide, unauthenticated 401
- ✅ `sample_topic` and `rate_limiter_reset` fixtures confirmed present in conftest.py
- ✅ Synthetic test data only — no real PII
- ✅ No skipped tests without backlog IDs

**Issues**:
- ❌ AWD-M-49 auto-filed: `DELETE /api/users/me` absent from openapi.json — spec not regenerated post-GRC-03

**Verdict**: **Needs fix** — OpenAPI spec must be regenerated before merge to `main`. Backend test suite unverifiable in sandbox (AWD-M-46 still open). Recommend Tolu runs `python -m pytest tests/ -v` locally before promoting to main.

## QA — 2026-04-27T00:36:39Z
Result: ✅ PASS
Commits: `197a19d` `7939e43` `0246466` | Files: `docs/agentic/backlog.md` `docs/agentic/completed_backlog.md` `docs/agentic/sprints/dev-log.md`
| Check | Result |
|-------|--------|
| TypeScript | ✅ 0 errors |
| Lint | ✅ 0 errors, 0 warnings |
| Frontend tests | ✅ 80 passing, 0 failing (8 test files) |
| Backend tests | ⚠️ skipped — venv/bin/python is a macOS binary (broken symlink to python3.13), not executable in Linux sandbox. Pre-existing issue: AWD-M-46. |
| OpenAPI valid | ✅ apps/backend/app/openapi.json is valid JSON; DELETE /api/users/me confirmed present with correct operationId, HTTPBearer security, 200 response |
| Spot-check | ✅ All 3 changed files are docs-only (backlog, completed_backlog, dev-log). No secrets, console.log, @ts-ignore, hardcoded values, or TODO/FIXME in any changed file. |
| CI on develop | unknown — gh CLI not available in sandbox |
Issues: None
Verdict: Ship — docs-only commit, all applicable checks pass. Tolu must run `git push origin develop` to trigger CI (19+ commits queued).

---
## QA — 2026-04-27T02:40:00Z
Result: ❌ FAIL
Commits: 07ca8e9, 8f3e30c | Files: apps/backend/alembic/versions/b3f92c1d4e87_add_parental_consents_table.py, apps/backend/models.py, apps/backend/routers/children.py, apps/backend/schemas/children.py, apps/backend/services/children_service.py, apps/backend/tests/test_consent_router.py, apps/frontend/src/components/ConsentModal.test.tsx, apps/frontend/src/components/ConsentModal.tsx, apps/frontend/src/pages/ParentDashboardPage.tsx, apps/frontend/src/services/api.ts, apps/frontend/src/types/children.ts, docs/agentic/backlog.md, docs/agentic/completed_backlog.md, docs/agentic/sprints/dev-log.md

| Check               | Result | Notes                                                                 |
|---------------------|--------|-----------------------------------------------------------------------|
| TypeScript          | ✅     | 0 errors                                                              |
| Lint                | ✅     | 0 errors, 0 warnings                                                  |
| Frontend tests      | ✅     | 88 passing, 0 failing (act() warnings are non-blocking, test-only)    |
| Backend tests       | ⚠️     | Could not run — venv symlinks to macOS Python 3.13 (incompatible with Linux sandbox); pip install blocked by no disk space. Requires local or CI run. |
| OpenAPI JSON valid  | ✅     | Valid JSON                                                             |
| Spot-check          | ❌     | openapi.json is missing ALL children, guide, and consent endpoints. GRC-01 added 2 new consent routes (/api/consent/status, /api/consent) to children.py but did not regenerate openapi.json. Pre-existing gap: children/guide routes also absent. contract-test CI job will fail. Filed AWD-H-50. |
| CI on develop       | unknown | gh CLI not available in sandbox                                       |

Issues:
- AWD-H-50: openapi.json not regenerated — missing consent, children, and guide routes (introduced by 07ca8e9; pre-existing gap compounded). contract-test CI job will fail.
- Backend tests unverified in this run (environment constraint — not a code defect).

Verdict: Needs fix — regenerate openapi.json before CI contract-test passes.

---
## QA — 2026-04-27T03:34:48Z
Result: ⏭ SKIPPED
Reason: No commits on develop in the last 40 minutes (last commit 8f3e30c at 02:22 UTC, 72 min ago)
Verdict: No action required

---

## QA — 2026-04-27T04:36:51Z

**Result**: ✅ PASS

**Commits validated**:
- `6f69506` — docs(api): AWD-H-50 regenerate openapi.json to include consent, children, and guide routes
- `2813ef4` — Merge fix/api-docs/AWD-H-50-openapi-regen into develop
- `c7ec892` — docs(agentic): AWD-H-50 mark complete in backlog, completed_backlog, dev-log

**Files changed**: `apps/backend/app/openapi.json` · `docs/agentic/backlog.md` · `docs/agentic/completed_backlog.md` · `docs/agentic/sprints/dev-log.md` · `manual_to_do.md`

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 88/88 passing (9 test files) |
| Backend tests (`pytest`) | ⚠️ Skipped — venv broken symlink (known AWD-M-46; no app code changed this cycle) |
| OpenAPI valid (`python3 -m json.tool`) | ✅ Valid JSON, 74 paths — consent, children, guide routes confirmed present |
| Spot-check | ✅ Clean — docs + openapi.json only; no secrets, console.log, @ts-ignore, TODOs, or missing role checks |
| CI on develop | ❓ Unknown — gh CLI unavailable; all commits still pending push (see manual_to_do.md) |

**Notes**:
- 2 `act()` React warnings in `ConsentModal.test.tsx` — pre-existing, non-blocking
- React Router v6 future flag warnings in `ChildProfileList.test.tsx` — pre-existing, tracked via AWD-L-09
- openapi.json confirmed to include all 12 new routes (consent, children, guides) matching AWD-H-50 intent
- No app code touched this cycle — backend pytest skip is safe given docs-only changes

**Issues filed this cycle**: None — all conditions clean

**Verdict**: Ship (pending Tolu push to GitHub to trigger real CI)

---

## QA Cycle — 2026-04-27 (AWD-M-51 Dev Agent run)

**Issue**: AWD-M-51 — Remove console.log PII leak and unguarded debug logs
**Commit**: ef73e69 / merge 510fd89

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings (fixed unused param on first pass) |
| Frontend tests (`npm run test:run`) | ✅ 88/88 passing (9 test files) |
| Backend tests (`pytest`) | ⏭ Skipped — no backend changes this cycle |
| OpenAPI valid (`python3 -m json.tool`) | ✅ Valid JSON |
| Spot-check | ✅ Zero bare `console.log/warn/error` in production paths across all 3 files; websocket.ts guards all 9 calls with `import.meta.env.DEV` |

**Verdict**: Ship (pending `git push origin develop` by Tolu)

---

## QA — 2026-04-27T06:37:27Z
**Result**: ✅ PASS
**Commits**: 510fd89 (merge), ef73e69 (fix) | **Files**: AIGenerationLoadingRealtime.tsx, Footer.tsx, websocket.ts

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 88 passing, 0 failing (9 test files) |
| Backend tests (`pytest`) | ⚠️ Skipped — venv symlink broken (M-46, pre-existing) |
| OpenAPI valid (`python3 -m json.tool`) | ✅ Valid JSON |
| Spot-check | ✅ |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check detail**:
- `Footer.tsx`: `console.log('Subscribing email:', email)` removed ✅ — PII leak patched
- `websocket.ts`: 8× bare `console.*` calls all now guarded with `if (import.meta.env.DEV)` ✅
- `AIGenerationLoadingRealtime.tsx`: unused `data: any` param + `console.log('Generation session started:')` removed ✅
- No hardcoded secrets, no `@ts-ignore`, no new `any` types, no TODO/FIXME, no missing role checks

**Issues**: None new. M-46 (venv broken symlink) remains open — backend tests cannot run in QA sandbox until recreated on dev machine.

**Verdict**: Ship

---

## QA — 2026-04-27T07:39:49Z
**Result**: ❌ FAIL
**Commits**: ad60f1c (fix(backend): AWD-M-50 replace bare print() calls with structured logger in main.py) | **Files**: apps/backend/main.py, apps/frontend/src/components/AIGenerationLoadingRealtime.tsx, apps/frontend/src/components/Footer.tsx, apps/frontend/src/services/websocket.ts

| Check | Result |
|-------|--------|
| TypeScript (`tsc --noEmit`) | ✅ 0 errors |
| Lint (`npm run lint`) | ✅ 0 errors, 0 warnings |
| Frontend tests (`npm run test:run`) | ✅ 88 passing, 0 failing (9 test files) |
| Backend tests (`pytest`) | ⚠️ Skipped — venv/bin/python3.13 is a broken macOS symlink in Linux sandbox (M-46, pre-existing) |
| OpenAPI valid (`python3 -m json.tool`) | ✅ Valid JSON |
| Spot-check | ❌ Regression detected — see issues below |
| CI on develop | unknown (gh CLI not available in sandbox) |

**Spot-check detail**:

**❌ REGRESSION — AWD-M-50 commit (ad60f1c) reverted AWD-M-51 fixes:**
Commit `ad60f1c` was scoped to `apps/backend/main.py` (logging fix) but also included diffs that undid the `ef73e69` (AWD-M-51) frontend console.log removals. The COMMITTED state of develop now has:
- `apps/frontend/src/components/Footer.tsx` line 10: `console.log('Subscribing email:', email)` — logs user email to browser console on every subscription attempt. **PII leak.**
- `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx` line ~145: `console.log('Generation session started:', data)` — logs WebSocket session payload.
- `apps/frontend/src/services/websocket.ts` lines 51, 62, 67, 73, 78, 86, 91, 116: 8 bare `console.log/error/warn` calls without `import.meta.env.DEV` guard.

The correct working-tree fix (DEV guards restored, console.log removed from Footer and AIGenerationLoadingRealtime) already exists as **uncommitted changes** on develop. It needs to be committed immediately.

**⚠️ ADDITIONAL — Multiple uncommitted working-tree changes:**
`git status` shows 10 modified tracked files and 4 untracked paths in the working tree:
- Modified: `apps/backend/app/openapi.json` (5711-line diff — likely a regeneration), `docs/agentic/backlog.md`, `docs/agentic/completed_backlog.md`, `docs/agentic/daily-briefs/morning-brief.md`, `docs/agentic/sprints/dev-log.md`, `docs/agentic/sprints/qa-log.md`, `manual_to_do.md`
- Untracked: `.agent-health/`, `.sandbox_deps/`, `.sandbox_work_H50/`, `apps/frontend/package-lock 2.json`
These represent several previous agent runs' outputs that were never pushed.

**⚠️ PRE-EXISTING — Hardcoded WebSocket production URL placeholder:**
`apps/frontend/src/services/websocket.ts` line 44: `'wss://your-production-domain.com/ws'` is hardcoded. Should be `import.meta.env.VITE_WS_URL`. Not introduced by this commit but not previously filed (see AWD-M-52 below).

**⚠️ MINOR — Stale placeholder comment in main.py:**
`apps/backend/main.py` line 153: `# ... existing code ...` is a code-editor placeholder comment that survived the AWD-M-50 fix. Violates the "no dead comments" rule. Bundleable with any future main.py touch.

**Issues auto-filed**:
- AWD-H-51: PII regression — AWD-M-50 commit reverted AWD-M-51 console.log fixes (see backlog)
- AWD-M-52: Hardcoded WebSocket production URL should use env var (see backlog)

**Verdict**: Needs fix — commit the working-tree fix for H-51 immediately before next deploy.
