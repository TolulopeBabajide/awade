# Awade — Backlog

> Last updated: 2026-04-26 (Lead Dev Agent — AWD-M-45 shipped)
> Last groomed: 2026-04-25 (weekend-ops / Ops Agent) — see notes below. Removed stale items, updated priorities for post-security-sprint phase. Parent pivot code is feature-complete; focus shifts to launch prep + compliance.
> Source of truth for active work. Completed items move to [`completed_backlog.md`](completed_backlog.md).
> Issue prefix: `AWD` — e.g., reference as `AWD-H-03` in commits.

---

## Legend
- 🔴 **Critical (C-##)** — broken behaviour, data loss, security risk, CI-blocking
- 🟠 **High (H-##)** — significant functional gap or user-facing failure
- 🟡 **Medium (M-##)** — degraded experience or subtle correctness issue
- 🟢 **Low / Polish (L-##)** — minor, cosmetic, or edge-case
- 🟣 **Compliance (GRC-##)** — GDPR / COPPA / NDPR / POPIA work

---

## 🔴 Critical

~~**AWD-C-07 — Chore commit `547a4ac` silently reverted two security fixes from AWD-M-39**~~ ✅ 2026-04-25

---

## 🟠 High

~~| M-41 | Code Quality / Types | **AWD-M-04 test commit stripped AWD-M-15 type safety work — uncommitted fix is sitting in working tree.** Commit `7fe0c3b` (`test(backend): AWD-M-04 add service-layer tests…`) accidentally included working-tree reversions to `api.ts` and `children.ts` that undo the typed-API work shipped in AWD-M-15 (commit `663b50a`). **Exact regressions in committed HEAD**: (1) `apps/frontend/src/types/children.ts` — 3 interfaces deleted: `ChildProfileUpdate`, `ChildProfileListResponse`, `ParentGuideListResponse`; (2) `apps/frontend/src/services/api.ts` — typed import block removed; 6 children/guide API methods downgraded from specific return types to `ApiResponse<any>` (`getChildren`, `getChild`, `createChild`, `updateChild`, `deleteChild`, `getChildTopics`, `getChildGuides`). **The fix already exists in the working tree (unstaged/uncommitted)** — it restores all 3 interfaces and re-applies proper typed returns. The working tree also contains two bonus improvements not yet committed: `GuideViewPage.tsx` — two `if (!res.data)` null guards added after the error check; `ParentDashboardPage.tsx` — replaces unsafe `res.data as ChildTopic[]` cast with safe `res.data ?? []`. **Fix**: run `git add apps/frontend/src/types/children.ts apps/frontend/src/services/api.ts apps/frontend/src/pages/GuideViewPage.tsx apps/frontend/src/pages/ParentDashboardPage.tsx` then commit: `fix(frontend): AWD-M-41 restore typed API interfaces stripped in AWD-M-04 test commit`. Do NOT push develop until this is committed — the committed HEAD has type regressions and 3 deleted interfaces. Filed: 2026-04-25 QA Agent. | `apps/frontend/src/types/children.ts`, `apps/frontend/src/services/api.ts`, `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/frontend/src/pages/ParentDashboardPage.tsx` | S |~~ ✅ 2026-04-25

---

~~**AWD-C-05 — git repo corruption: `refs/heads/develop` points to missing commit object**~~
**Problem**: `refs/heads/develop` contains SHA `187bd80b8614c9f84ff3a69f0cddb39a2e31e24b`, which does not exist in `.git/objects/`. All git operations on the develop branch fail (`git log`, `git status`, `git commit`, `git push`). Development and CI pushes are fully blocked.
**Root cause**: An interrupted git commit operation (likely disk-full condition in QA sandbox) left `tmp_obj_*` temporaries in `.git/objects/` and never finalized the commit object. Files for H-22 and H-26 fixes are safely on disk but uncommitted.
**Acceptance criteria**:
- [ ] `git update-ref refs/heads/develop da90c8967dd912f38467e2c93c41ab7501114204` restores develop to last valid commit
- [ ] `git log --oneline -3` shows `da90c89 chore(backend): replace datetime.UTC with timezone.utc` as HEAD
- [ ] On-disk changes re-committed: `apps/backend/tests/test_ai_providers.py` (H-22), `apps/backend/services/lesson_plan_service.py` (H-26), `packages/ai/providers/openai_provider.py` (H-09 remnant)
- [ ] `git push origin develop` succeeds
- [ ] CI pipeline green on develop after push
**Files**: `.git/refs/heads/develop` (fix only — no app code change needed)
**Effort**: S (minutes, but requires Tolu to run commands locally on their Mac)
**Note**: QA sandbox cannot write to the user's git repo — Tolu must run the recovery commands locally.

---

## 🟠 High

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| H-41 | Testing / TypeScript | `GuideViewPage.test.tsx` (introduced by AWD-M-05 commit f4ebdb3) has 6 TypeScript errors and 1 failing test. **TS errors**: (1) `React` imported but never used (TS6133, line 1); (2) 5× `null` not assignable to `string \| undefined` (TS2322, lines 116, 125, 134, 146, 155) — `generateGuide` mock args use `null` for optional string params but the function signature expects `string \| undefined`. Fix: remove the `React` import; change the 5× `null` literals to `undefined`. **Test failure**: `renders guide via generateGuide when child+topic params are supplied (no guide ID)` — component renders an empty `<main>` instead of the expected `Fractions` heading, suggesting the `generateGuide` mock is not resolving (missing `await waitFor(...)` wrapper or mock data mismatch). Fix: wrap the assertion in `await waitFor(() => expect(screen.getByRole(...)).toBeInTheDocument())` and verify the mock return value shape matches what the component renders. Blocks CI `frontend-test` and `validate` jobs once Tolu pushes. Filed: 2026-04-25 QA Agent. | `apps/frontend/src/pages/GuideViewPage.test.tsx` (lines 1, 116, 125, 134, 146, 155, ~140) | S |~~ ✅ 2026-04-25
~~| H-40 | Security / Error Handling | `lesson_plans.py` export endpoint leaks internal error details via `str(e)` in HTTPException detail (OWASP A09 information disclosure). `export_lesson_resource` lines 219–223: `detail=f"An error occurred while exporting the resource: {str(e)}"` — can expose WeasyPrint stack traces, file paths, or SQL errors to the client. Same class as AWD-H-18 (fixed service files) but missed this router-level handler. Fix: add `logger = logging.getLogger(__name__)` to imports and replace the except block with a static detail string + `logger.error(..., exc_info=True)`. | `apps/backend/routers/lesson_plans.py` (lines 219–223) | S |~~ ✅ 2026-04-25
~~| H-27 | Testing | `test_contexts_router.py` — 8 tests fail with `AttributeError: 'NoneType' object has no attribute 'set'`. Root cause: `_make_educator` / `_make_admin` call `User.__new__(User)` which bypasses SQLAlchemy's `__init__`, leaving `_sa_instance_state = None` so attribute assignment fails. Fix: replace `User.__new__(User)` with `User()` (transient instances are fine — no session needed) and set fields via constructor kwargs or direct attribute assignment after `__init__` has run. | `apps/backend/tests/test_contexts_router.py` (lines 22-27, 30-35) | S |~~ ✅ 2026-04-22
~~| H-28 | Testing | `test_auth_flow_security.py::TestExceptionDetailSanitization` — 3 tests assert `status_code == 500` after injecting a `RuntimeError` via `side_effect`, but receive `422`. Pydantic rejects the empty `{}` payloads at the validation layer before the route handler (and the mock) is ever reached. Fix: supply valid request bodies (email + password fields for login/register, token field for google-auth) so requests clear validation and hit the mocked service code path. | `apps/backend/tests/test_auth_flow_security.py` (`TestExceptionDetailSanitization` class) | S |~~ ✅ 2026-04-22
~~| H-29 | Testing | Rate-limiter state not reset between test files — 6 tests in `test_auth_flow_security.py` pass in isolation but fail when the full suite runs: `test_login_sets_httponly_cookie`, `test_refresh_token_flow` (fails `assert 429`), `TestAccountEnumerationProtection` (3 tests), and `TestExceptionDetailSanitization::test_login_db_error_does_not_leak_exception` (added after AWD-H-28 fix revealed this). Root cause: earlier test files exhaust the in-memory rate-limiter for the `/api/auth/login` endpoint; subsequent tests receive 429 instead of the expected 200/401/500. Fix: in `apps/backend/tests/conftest.py`, add a `rate_limiter_reset` autouse fixture that clears the rate-limiter storage between each test (e.g. `app.state.limiter.reset()` or equivalent for the limiter implementation in `apps/backend/limiter.py`). Discovered in full-suite run during QA of AWD-H-18. | `apps/backend/tests/conftest.py`, `apps/backend/limiter.py` | S |~~ ✅ 2026-04-22
~~| H-32 | Parents / Error Handling | `ParentOnboardingPage.tsx`: `loadRefData()` (lines 49-59) and `loadCurriculums()` (lines 69-73) have no try/catch. If any of the three parallel reference-data calls (countries, grades, subjects) or the curriculum fetch fails, the error is silently swallowed and the user sees empty dropdowns with no message. Fix: wrap both async bodies in try/catch; on error call `setError('Failed to load options. Please refresh.')`. Regression in AWD-H-20. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (lines 49-59, 69-73) | S |~~ ✅ 2026-04-23
~~| H-01 | Observability | Wire up Sentry (or equivalent) for error monitoring — backend + frontend | `apps/backend/main.py`, `apps/backend/middleware/`, `apps/frontend/src/main.tsx` | M |~~ ✅ 2026-04-23
~~| H-33 | CI / Observability | Commit `b552efe` accidentally reverted AWD-H-01 Sentry stack and broke CI — see detail below | multiple | S |~~ ✅ 2026-04-23
| H-03 | Admin | Admin panel has no parent / child management views yet | `apps/backend/routers/admin.py`, `apps/frontend/src/pages/` (admin) | L |
~~| H-39 | Security / AI | `GeminiProvider.generate_content()` has no explicit request timeout — a hung Gemini call can block a FastAPI worker indefinitely (OWASP LLM10, Model DoS). H-09 added a timeout to `OpenAIProvider` but the Gemini provider was not updated to match. Fix: pass `http_options=genai_types.HttpOptions(timeout=30)` (or similar) to `genai.Client(api_key=..., http_options=...)` during initialisation, or set a per-call timeout via `config.timeout` if the SDK supports it. Verify the correct parameter in `google-genai==1.14.0` docs before applying. Filed: 2026-04-25 QA Agent (spotted during M-39 spot-check). | `packages/ai/providers/gemini_provider.py` (`__init__`, `generate_content`) | S |~~ ✅ 2026-04-25
~~| H-06 | AI | Output validation for `generate_parent_guide()` — validate JSON shape against schema before persisting | `packages/ai/gpt_service.py`, `apps/backend/schemas/children.py` | S |~~ ✅ 2026-04-22
~~| H-18 | Security | `str(e)` leaked in HTTPException detail across remaining service files — same class of information disclosure fixed in H-08 for auth/context, but present in `user_service.py` (6 instances), `lesson_plan_service.py` (10), `country_service.py` (8), `subject_service.py` (8), `grade_level_service.py` (9), `file_upload_service.py` (2). Fix: add `logger = logging.getLogger(__name__)` and replace `detail=f"...{str(e)}"` with static strings + `logger.error(..., exc_info=True)` in each file. Discovered during H-08 validation. | `apps/backend/services/user_service.py`, `lesson_plan_service.py`, `country_service.py`, `subject_service.py`, `grade_level_service.py`, `file_upload_service.py` | M |~~ ✅ 2026-04-22
~~| H-09 | Security / AI | OpenAI client has no explicit timeout — request can hang a worker indefinitely under network degradation (OWASP LLM10) | `packages/ai/providers/openai_provider.py` (line 27) | S |~~ ✅ 2026-04-22
~~| H-10 | Security / Deps | npm audit: 3 high-severity vulnerabilities via `@remix-run/router` / `react-router` / `react-router-dom` (XSS via open redirects — GHSA-2w69-qvjg-hvjx). Fix: `npm audit fix` | `apps/frontend/package.json`, `apps/frontend/package-lock.json` | S |~~ ✅ 2026-04-22
~~| H-11 | Testing | No pytest coverage for the new children router or `ChildrenService`. Must cover: ownership (parent A cannot read parent B's child → 404), role gating (EDUCATOR hitting `/api/children` → 403), idempotent `generate_guide`, validator rejecting malformed AI JSON. Complements M-04 (general coverage shore-up) | `apps/backend/tests/` (new `test_children_router.py`, `test_children_service.py`), `apps/backend/routers/children.py`, `apps/backend/services/children_service.py` | M |~~ ✅ 2026-04-22
~~| H-19 | Parents | Dedicated `/children` page for managing child profiles — currently only AddChildModal inline on the dashboard; rebranding doc §5.4 calls for a standalone "My Children" page with add/edit/delete | `apps/frontend/src/pages/` (new `ChildrenPage.tsx`), `apps/frontend/src/App.tsx`, `apps/frontend/src/components/Sidebar.tsx` | M |~~ ✅ 2026-04-23
~~| H-20 | Parents | Parent onboarding flow — first-time parent signup should guide through adding a child profile before landing on the dashboard (rebranding doc §4.3 step 2) | `apps/frontend/src/pages/ParentDashboardPage.tsx`, new `ParentOnboardingPage.tsx` | M |~~ ✅ 2026-04-23
~~| H-16 | Code Hygiene | 10+ `console.log` / `console.error` left in production paths in `EditLessonResourcePage.tsx` (lines 399, 403, 440–442, 469, 477, 480, 486, 508, 516, 520, 530) and `SettingsPage.tsx` (lines 104, 208, 214, 229) — leaks internal parse details and auto-save payloads to browser console. Replace with structured logger or remove. | `apps/frontend/src/pages/EditLessonResourcePage.tsx`, `apps/frontend/src/pages/SettingsPage.tsx` | S |~~ ✅ 2026-04-22
~~| H-21 | Code Hygiene | 2 bare `print()` calls in `lesson_plan_service.py` left in production paths: line 397 `print(f"Failed to enqueue job: {e}")` (swallows enqueue errors silently after printing) and line 534 `print(f"DEBUG: Resource {resource_id} found in DB...")` (debug statement). Both violate CLAUDE.md hygiene rule and leak internal details to stdout. Fix: replace line 397 with `logger.error("Failed to enqueue job", exc_info=True)` and remove line 534. Discovered during QA of `da90c89`. | `apps/backend/services/lesson_plan_service.py` | S |~~ ✅ 2026-04-22
~~| H-26 | Code Hygiene | 2 `traceback.print_exc()` calls remain in `lesson_plan_service.py` after the AWD-H-21 fix — missed in commit `4460d8b`. **Line 112** (in `create_lesson_plan_response()` except block) and **line 162** (in `generate_lesson_plan()` except block). Both do `import traceback` inline then call `traceback.print_exc()`, which writes the full traceback to stderr in production paths. `logger = logging.getLogger(__name__)` is already defined at the top of the file. Fix: in each of the two except blocks, delete the `import traceback` line and replace `traceback.print_exc()` with `logger.error("Unexpected error in <method_name>", exc_info=True)`. No other changes needed. Discovered during QA of `4460d8b`. | `apps/backend/services/lesson_plan_service.py` (lines 111-112, 161-162) | S |~~ ✅ 2026-04-22
~~| H-22 | Testing | `TestGeminiProvider::test_get_model_name` fails in CI: test asserts `gemini-1.5-flash` / `gemini-1.5-pro` but `gemini_provider.py` now returns `gemini-flash-latest` for both tiers (updated in Jan 2026 per inline comment). Exact error: `AssertionError: assert 'gemini-flash-latest' == 'gemini-1.5-flash'` at `tests/test_ai_providers.py:51`. Fix: update lines 51-52 — `assert provider._get_model_name("basic") == "gemini-flash-latest"` and `assert provider._get_model_name("standard") == "gemini-flash-latest"`. Unmasked by `da90c89` Python 3.10 compat fix which allows `test_ai_providers.py` to execute for the first time in QA sandbox. | `apps/backend/tests/test_ai_providers.py` (lines 51-52), `packages/ai/providers/gemini_provider.py` (lines 37-40) | S |~~ ✅ 2026-04-22
~~| H-23 | Security / Deps | PyJWT 2.3.0 installed vs 2.12.1 latest — large version gap for the JWT signing library. Known CVE surface across this range; `requirements.txt` uses `PyJWT>=2.0.0` (unpinned floor) so CI installs whatever is available. Fix: pin to `PyJWT==2.12.1` in `requirements.txt` and verify locally. Also see M-08 (general requirements pinning). Filed: 2026-04-22 security scan. | `apps/backend/requirements.txt` | S |~~ ✅ 2026-04-22
~~| H-24 | Security | Suspended users bypass authentication — `get_current_active_user` in `apps/backend/dependencies.py` has a comment "Add any additional checks for user status here" but does NOT check `user.is_suspended`. An admin can set `is_suspended=1` in the DB, but the user continues to authenticate and use all endpoints. Fix: add `if user.is_suspended: raise HTTPException(status_code=403, detail="Account suspended")` after the user lookup (line ~135). All auth-gated routes inherit the fix through the Depends chain. Filed: 2026-04-22 security scan. | `apps/backend/dependencies.py` | S |~~ ✅ 2026-04-22
~~| H-25 | Security | JWT access token stored in `localStorage` — `AuthContext.tsx` stores `access_token` and `user_data` in `localStorage`. Any XSS can silently exfiltrate tokens. **Decision (2026-04-23): migrate to httpOnly cookies.** Backend: update `/api/auth/login`, `/api/auth/register`, `/api/auth/google` to issue `Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/` instead of returning the token in the JSON body. Add `/api/auth/logout` endpoint that clears the cookie. Update `/api/auth/refresh` to read from cookie and re-issue. Frontend: remove `localStorage.setItem('access_token', ...)` from `AuthContext.tsx`; update API client (`api.ts`) to use `credentials: 'include'` instead of `Authorization: Bearer` header. Update `get_current_active_user` in `dependencies.py` to read token from cookie if `Authorization` header is absent. | `apps/backend/routers/auth.py`, `apps/backend/dependencies.py`, `apps/frontend/src/contexts/AuthContext.tsx`, `apps/frontend/src/services/api.ts` | M |~~ ✅ 2026-04-23
~~| H-30 | Security | `/children` route missing PARENT role guard — `App.tsx` (lines 48–52) wraps `/children` in `<ProtectedRoute>` (auth only). An authenticated EDUCATOR who navigates directly to `/children` via the address bar reaches `ChildrenPage.tsx` with no role check, violating the security rule "Role-gated routes check user.role against UserRole.EDUCATOR / UserRole.PARENT". Fix: create a `<ParentRoute>` wrapper (similar to `<AdminRoute>`) that checks `user.role === 'PARENT'` and redirects EDUCATORs to `/dashboard` if not, then wrap the `/children`, `/saved-guides`, and `/guides/generate` routes in it. Alternatively, add an early-return role check at the top of `ChildrenPage.tsx`. Discovered during QA of commit `5367714`. | `apps/frontend/src/App.tsx` (lines 48–52), `apps/frontend/src/components/ProtectedRoute.tsx` or new `ParentRoute.tsx` | S |~~ ✅ 2026-04-23
~~| H-31 | Testing | No vitest tests for `ChildrenPage.tsx` — the new page added in AWD-H-19 (commit `5367714`) has no colocated `.test.tsx` file. Code quality checklist and testing standards require: (1) render in loading state, (2) render in error state with retry button, (3) render in empty state with "Add Your First Child" CTA, (4) render children grid with multiple profiles, (5) delete confirmation flow (mock `apiService.deleteChild`), (6) EDUCATOR redirect/gate behavior once H-30 is fixed. Create `apps/frontend/src/pages/ChildrenPage.test.tsx` with vitest + `@testing-library/react`. Mock `apiService` from `apps/frontend/src/services/api.ts`. Discovered during QA of commit `5367714`. | `apps/frontend/src/pages/ChildrenPage.test.tsx` (new file) | S |~~ ✅ 2026-04-23

~~**AWD-H-34 — `get_optional_current_user` not updated for HttpOnly cookie auth — cookie-authenticated browser users silently treated as anonymous**~~ ✅ 2026-04-24
**Problem**: `apps/backend/dependencies.py` — `get_current_user` was correctly updated in AWD-H-25 to read the `access_token` from either the `Authorization` header OR the HttpOnly cookie. However, `get_optional_current_user` was **not** updated: it still reads only the `Authorization` header. If the header is absent it returns `None` immediately, bypassing the cookie. Browser clients (which now carry the token only in the cookie) will appear unauthenticated to any endpoint that uses this dependency.
**Affected routes**: `apps/backend/routers/curriculum.py` (imports `get_optional_current_user`), `apps/backend/routers/curriculum_structure.py` (imports `get_optional_current_user`), `apps/backend/routers/lesson_plans.py` (imports `get_optional_current_user`).
**Fix**: Mirror the cookie-fallback logic from `get_current_user` into `get_optional_current_user`:
```python
async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    try:
        token: Optional[str] = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = request.cookies.get("access_token")
        if not token:
            return None
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.query(User).filter(User.user_id == int(user_id)).first()
    except Exception:
        return None
```
**Acceptance criteria**:
- [x] `get_optional_current_user` returns the `User` object when only the `access_token` cookie is present (no `Authorization` header)
- [x] `get_optional_current_user` still returns `None` for unauthenticated requests
- [x] Existing routes using this dependency continue to work with bearer-token clients
- [x] Backend tests cover the cookie-fallback path
**Files**: `apps/backend/dependencies.py` (~line 195), `apps/backend/tests/` (new test case)
**Effort**: S
**Filed**: 2026-04-23 QA Agent (automated — AWD-H-25 follow-up)

~~**AWD-H-33 — Commit `b552efe` accidentally reverted the entire Sentry observability stack (AWD-H-01) and CI backend tests will fail**~~
**Problem**: The commit `test(backend): AWD-M-26 add pytest coverage for _init_sentry() branches` (b552efe) staged only the new test file `apps/backend/tests/test_sentry_init.py`, but the developer's local working tree still held the committed versions of all other Sentry-related files. The committed HEAD is now missing everything that AWD-H-01 shipped:
- `_init_sentry()` removed from `apps/backend/main.py` (confirmed via `git show HEAD:apps/backend/main.py | grep sentry` → no output)
- `sentry-sdk[fastapi]==2.58.0` removed from `apps/backend/requirements.txt`
- `@sentry/react` removed from `apps/frontend/package.json`
- Frontend Sentry init block removed from `apps/frontend/src/main.tsx`
- Sentry type stubs removed from `apps/frontend/src/vite-env.d.ts`
- All `SENTRY_DSN` / `SENTRY_TRACES_SAMPLE_RATE` / `VITE_SENTRY_DSN` vars removed from `env.example`, `env.production.template`, `env.test.template`, `.env.example`

`test_sentry_init.py` (which IS in the commit) calls `apps.backend.main._init_sentry()` — CI backend-test job will immediately fail with `AttributeError: module 'apps.backend.main' has no attribute '_init_sentry'`.
**Acceptance criteria**:
- [ ] All working-tree files are staged and committed: `apps/backend/main.py`, `apps/backend/requirements.txt`, `apps/frontend/package.json`, `apps/frontend/src/main.tsx`, `apps/frontend/src/vite-env.d.ts`, `env.example`, `env.production.template`, `env.test.template`, `.env.example`
- [ ] `git show HEAD:apps/backend/main.py | grep _init_sentry` returns the function definition
- [ ] `cd apps/backend && python -m pytest tests/test_sentry_init.py -v` — all 9 tests pass
- [ ] `cd apps/frontend && npm run test:run` — still 45/45 green
- [ ] Push develop; CI backend-test job green
**Fix (exact steps)**:
```bash
cd <project root>
git add apps/backend/main.py apps/backend/requirements.txt
git add apps/frontend/package.json apps/frontend/src/main.tsx apps/frontend/src/vite-env.d.ts
git add env.example env.production.template env.test.template .env.example
git commit -m "fix(observability): restore Sentry stack accidentally dropped from b552efe"
git push origin develop
```
**Files**: `apps/backend/main.py`, `apps/backend/requirements.txt`, `apps/frontend/package.json`, `apps/frontend/src/main.tsx`, `apps/frontend/src/vite-env.d.ts`, `env.example`, `env.production.template`, `env.test.template`, `.env.example`
**Effort**: S (minutes — just stage and commit the working-tree files, no code changes needed)
**Audience**: internal / CI
**Filed**: 2026-04-23 QA Agent (automated)

---

~~**AWD-H-35 — AWD-M-10 merge accidentally removed the Content-Security-Policy header, breaking the AWD-M-11 fix and causing CI backend tests to fail**~~

**Problem**: Commit `1c175fc` (AWD-M-10: disable `/docs` and `/redoc` in production) was cut from a version of `apps/backend/middleware/security_headers.py` that pre-dates AWD-M-11 (which added the CSP header in commit `afed4c2`). When AWD-M-10 was merged into `develop` (merge commit `6adca34`), it clobbered the CSP addition. `git show develop:apps/backend/middleware/security_headers.py` confirms no `Content-Security-Policy` line exists in committed HEAD on `develop`. The test `test_csp_header_directives` in `apps/backend/tests/test_security.py` asserts the CSP header is present — it will fail in CI.

**Note**: The working tree already has the CSP restored as an uncommitted local change to `security_headers.py` (plus 16 other modified files not yet staged). The fix is simply committing the working-tree restoration.

**Acceptance criteria**:
- [ ] `git show develop:apps/backend/middleware/security_headers.py | grep Content-Security-Policy` returns the header line
- [ ] `cd apps/backend && python -m pytest tests/test_security.py::test_csp_header_directives -v` — passes
- [ ] `cd apps/backend && python -m pytest tests/ -v` — 0 failures
- [ ] Push `develop`; CI backend-test job green

**Fix (exact steps)**:
```bash
cd <project root>
git add apps/backend/middleware/security_headers.py
git commit -m "fix(security): restore CSP header accidentally dropped in AWD-M-10 merge"
git push origin develop
```
If Tolu also wants to commit the other 16 working-tree modifications, review and stage them selectively — do not use `git add -A`.

**Files**: `apps/backend/middleware/security_headers.py`
**Effort**: S (minutes — file already fixed locally, just needs committing)
**Audience**: internal / CI
**Filed**: 2026-04-24 QA Agent (automated)

~~**AWD-H-36 — AWD-M-14 regression: staged working tree reverts batch subject FK query back to per-subject loops, removing 3 test cases**~~ ✅ 2026-04-24

---

~~**AWD-H-37 — `TestUnauthenticated` asserts 403 but auth layer returns 401 (pre-existing since AWD-H-25)**~~ ✅ 2026-04-24

**Problem**: 10 tests in `TestUnauthenticated` in `apps/backend/tests/test_children_router.py` assert `resp.status_code == 403` for requests made with no auth token. The actual response is `401 Unauthorized`. The test's docstring claims "FastAPI's `HTTPBearer(auto_error=True)` raises HTTP 403" — but AWD-H-25 changed the scheme to `HTTPBearer(auto_error=False)` (see `apps/backend/dependencies.py` line 22), after which `get_current_user` manually raises `HTTP_401_UNAUTHORIZED` (lines 114–118). The test was never updated to match. These 10 tests have been failing on every CI run since AWD-H-25 shipped.

**Acceptance criteria**:
- [ ] Change the assertion in `TestUnauthenticated.test_returns_403` (line ~150) from `resp.status_code == 403` to `resp.status_code == 401`
- [ ] Rename the test method and class docstring to reflect 401 (e.g. `test_returns_401`, class docstring updated)
- [ ] `cd apps/backend && python -m pytest tests/test_children_router.py::TestUnauthenticated -v` — 10/10 pass
- [ ] `cd apps/backend && python -m pytest tests/ -v` — 0 failures (net of other pre-existing issues)

**Fix (exact steps)**:
In `apps/backend/tests/test_children_router.py` around line 148–151:
```python
# Before:
assert resp.status_code == 403, (
    f"{method} {path} returned {resp.status_code}, expected 403 (no auth)"
)
# After:
assert resp.status_code == 401, (
    f"{method} {path} returned {resp.status_code}, expected 401 (no auth)"
)
```
Also update the class name and docstring to say 401 instead of 403.

**Files**: `apps/backend/tests/test_children_router.py` (lines ~139–155)
**Effort**: S (minutes — test assertion change only, no prod code)
**Audience**: internal / CI
**Filed**: 2026-04-24 QA Agent (automated)

---

~~**AWD-H-38 — `TestGenerateGuideIdempotency` and `TestGenerateGuideMalformedAI` mock DB mismatch causes 3 test failures**~~ ✅ 2026-04-24

**Problem**: 3 tests introduced in `991c287` fail because their mock DB setup expects TWO chained `.filter()` calls on the `ParentGuide` query — i.e. `.options().filter().filter().first()` — but the service (`generate_guide`, line ~347) uses a single `.filter(ParentGuide.child_id == child_id, ParentGuide.topic_id == topic_id)` call, producing the chain `.options().filter().first()`. As a result:

1. `test_existing_guide_returned_no_ai_call` — mock returns a default `MagicMock()` (not `existing_guide`) for the existence check; it is truthy so `_guide_to_response(MagicMock)` is called, Pydantic rejects the fields, unhandled exception → 500 (expected 200).
2. `test_malformed_ai_json_returns_502` — same issue: mock `MagicMock` is truthy so service short-circuits to `_guide_to_response()` before reaching the AI call or the `model_validate_json` validation block → 500 (expected 502).
3. `test_missing_required_ai_fields_returns_502` — same root cause → 500 (expected 502).

The two `TestGenerateGuideMalformedAI` tests were specifically written to verify the AWD-H-36 (502 validation) feature, but the mock bug prevents the new code from ever being exercised.

**Acceptance criteria**:
- [ ] In `TestGenerateGuideIdempotency` (line ~412), update the `ParentGuide` mock branch: `q.options.return_value.filter.return_value.first.return_value = existing_guide` (remove the extra `.filter.return_value` layer)
- [ ] In `TestGenerateGuideMalformedAI._build_db_no_existing_guide` (line ~467), update the `ParentGuide` mock branch: `q.options.return_value.filter.return_value.first.return_value = None` (remove the extra `.filter.return_value` layer)
- [ ] `cd apps/backend && python -m pytest tests/test_children_router.py::TestGenerateGuideIdempotency tests/test_children_router.py::TestGenerateGuideMalformedAI -v` — all 3 pass
- [ ] `cd apps/backend && python -m pytest tests/ -v` — net failures reduced by 3

**Fix (exact steps)**:

In `TestGenerateGuideIdempotency.test_existing_guide_returned_no_ai_call` (around line 432):
```python
# Before:
q.options.return_value.filter.return_value.filter.return_value.first.return_value = existing_guide
q.filter.return_value.filter.return_value.first.return_value = existing_guide
# After:
q.options.return_value.filter.return_value.first.return_value = existing_guide
q.filter.return_value.first.return_value = existing_guide
```

In `TestGenerateGuideMalformedAI._build_db_no_existing_guide` (around line 488):
```python
# Before:
inner = MagicMock()
inner.first.return_value = None
q.options.return_value.filter.return_value.filter.return_value = inner
q.filter.return_value.filter.return_value.first.return_value = None
# After:
q.options.return_value.filter.return_value.first.return_value = None
q.filter.return_value.first.return_value = None
```

**Files**: `apps/backend/tests/test_children_router.py` (lines ~412–560)
**Effort**: S (minutes — mock wiring fix only, no prod code)
**Audience**: internal / CI
**Filed**: 2026-04-24 QA Agent (automated)

**Problem**: The `develop` HEAD (commit `99981fc`) correctly contains the AWD-M-14 batch IN query for subject FK validation in `create_child` and `update_child`. However, the current **staged index** (i.e. `git diff --cached`) reverses this — replacing the single `Subject.subject_id.in_(ids)` query with the original per-subject loop in both methods. The staged changes to `test_children_service.py` also remove the three tests that specifically exercised the batch query: `test_partial_invalid_subjects_raises_400_for_first_bad_id`, `test_all_valid_subjects_does_not_raise`, and the `_db_subjects_not_found` mock helper. If the next commit is made with these files in their current staged state, AWD-M-14 will silently regress.

**Root cause**: The staged `children_service.py` changes appear to be from an earlier working tree snapshot that pre-dates AWD-M-14, mixed in alongside new AI-validation additions (the `ParentGuideAIContent.model_validate_json(ai_content)` block in `generate_guide()` that references the new `ParentGuideAIContent` and `ValidationError` imports). The AI validation additions are correct and should be preserved — only the subject FK loop reversion is wrong.

**Acceptance criteria**:
- [ ] `git diff --cached -- apps/backend/services/children_service.py` no longer shows the per-subject loop replacing the batch query
- [ ] Both `create_child` and `update_child` retain the `Subject.subject_id.in_(ids)` / `found_ids` / `invalid` pattern from commit `d9f8125`
- [ ] `test_children_service.py` retains `_db_subjects_not_found`, `test_partial_invalid_subjects_raises_400_for_first_bad_id`, and `test_all_valid_subjects_does_not_raise`
- [ ] The AI-validation additions (`ParentGuideAIContent.model_validate_json`, `ValidationError` import, `ParentGuideAIContent` schema import) are preserved in the committed file
- [ ] `python -m pytest tests/test_children_service.py -v` passes (all tests including the batch-query tests)

**Fix**: Unstage `children_service.py` and `test_children_service.py`, then re-stage only the correct lines:
```bash
git restore --staged apps/backend/services/children_service.py
git restore --staged apps/backend/tests/test_children_service.py
# Then manually re-add only the AI-validation block additions using `git add -p`
```
Or: accept the full working-tree version of `children_service.py` (which has both the correct batch query AND the AI validation additions) and re-stage cleanly.

**Files**: `apps/backend/services/children_service.py` (staged index), `apps/backend/tests/test_children_service.py` (staged index)
**Effort**: S — git staging surgery, no logic changes needed
**Filed**: 2026-04-24 QA Agent (automated — detected via `git diff --cached`)

---

## 🟡 Medium

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| M-45 | Frontend / Compat | `fetchPriority` React prop warning in tests — `HeroSection.tsx` (line 74) and `HeroSectionParent.tsx` (line 84) use `fetchPriority="high"` on `<img>` elements. React 18.2.0 does not recognise the camelCase prop, generating `Warning: React does not recognize the 'fetchPriority' prop` in the test suite (visible in App.test.tsx output). React 18.3.0+ added official camelCase support. Fix: either (a) bump `react` and `react-dom` to `^18.3.0` in `apps/frontend/package.json` (also resolves L-09 future-flag warnings which were fixed in 18.3) or (b) as a backward-compatible short-term fix, replace `fetchPriority` with lowercase `fetchpriority` (valid HTML attribute accepted by React for unknown props). Option (a) is preferred. Ensure `@types/react` and `@types/react-dom` are bumped to match. Run `npm run test:run` and `npx tsc --noEmit` after to confirm no regressions. Discovered: 2026-04-25 QA Agent (App.test.tsx stderr). | `apps/frontend/src/components/HeroSection.tsx` (line 74), `apps/frontend/src/components/HeroSectionParent.tsx` (line 84), `apps/frontend/package.json` | S |~~ ✅ 2026-04-26
~~| M-42 | Code Hygiene | `pdf_service.py:19` — bare `print()` at module level (import-time). When WeasyPrint is not installed the line `print("Warning: WeasyPrint not available. PDF generation will be disabled.")` fires on every import, writing directly to stdout in production. Violates CLAUDE.md hygiene rule and code-quality checklist. Fix: (1) add `logger = logging.getLogger(__name__)` near the top of the file (or reuse the existing import if one is added later); (2) replace the `print(...)` with `logger.warning("WeasyPrint not available — PDF generation will be disabled.")`. Discovered during spot-check of AWD-M-21 (2026-04-25 QA Agent). | `apps/backend/services/pdf_service.py` (line 19) | S |~~ ✅ 2026-04-25
~~| M-26 | Testing | No pytest coverage for `_init_sentry()` in `apps/backend/main.py` (added in AWD-H-01, commit 364762f). Three branches are untested: (a) `SENTRY_DSN` blank → returns early; (b) `ENVIRONMENT=testing` → returns early; (c) `ImportError` → logs warning and returns. Risk is low — all branches are safe no-ops — but testing standards require at least a smoke test. Fix: add `tests/test_sentry_init.py` (or a section in `test_api_endpoints.py`) with three parametrised cases, monkeypatching `os.getenv` and `sentry_sdk.init`. Filed: 2026-04-23 QA. | `apps/backend/main.py` (`_init_sentry`), `apps/backend/tests/` | S |~~ ✅ 2026-04-23
~~| M-25 | Testing | `ParentOnboardingPage.test.tsx`: all 9 tests emit `Warning: An update to ParentOnboardingPage inside a test was not wrapped in act(...)`. Tests pass, but the warnings are a flakiness risk in CI and indicate async state settling outside the test boundary. Fix: use `waitFor` or `findBy*` queries (from `@testing-library/react`) in place of immediate `getBy*` assertions where state updates follow user events or query resolution. | `apps/frontend/src/pages/ParentOnboardingPage.test.tsx` | S |~~ ✅ 2026-04-24
~~| M-24 | Code Quality | `SignupPage.tsx` lines 55 and 130: `catch (err: any)` — `any` in catch blocks violates the code quality checklist ("Error types in catch blocks are narrowed, not `catch (e: any)`"). Fix: change to `catch (err: unknown)` and narrow with `err instanceof Error ? err.message : 'Unexpected error'` before accessing `.message`. | `apps/frontend/src/pages/SignupPage.tsx` (lines 55, 130) | S |~~ ✅ 2026-04-23
~~| M-23 | Security / AI | `AwadeGPTService.validate_output` only checks for required JSON fields — no harmful-word / content-safety pass implemented. `test_audit_security_features.py` was written against an assumed harmful-pattern check that was never built. Add content-safety filtering (harmful words, PII patterns, instruction-injection markers) to `validate_output` before the `return True, None`. The `sanitize_input` util in `apps/backend/utils/sanitizer.py` has a prompt-injection list that can seed the pattern set. | `packages/ai/gpt_service.py` (`validate_output`), `apps/backend/utils/sanitizer.py` | S |~~ ✅ 2026-04-24
~~| M-22 | Testing | `test_async_integration.py::test_worker_task_execution` fails: `generate_lesson_resource` called 0 times. The mock target path is likely wrong or the arq worker task dispatch is not wired to the mock. Investigate whether the patch path matches the symbol actually used at call time, and whether the async task is being enqueued vs called directly. | `apps/backend/tests/test_async_integration.py` | S |~~ ✅ 2026-04-24
~~| M-01 | UX | Handle loading + error states consistently across ParentDashboardPage, GuideViewPage, SavedGuidesPage | `apps/frontend/src/pages/ParentDashboardPage.tsx`, `GuideViewPage.tsx`, `SavedGuidesPage.tsx` | M |~~ ✅ 2026-04-24
~~| M-02 | SEO | Meta tags + OG images on landing page (parent + educator versions) | `apps/frontend/src/pages/LandingPage.tsx`, `apps/frontend/index.html` | S |~~ ✅ 2026-04-24
~~| M-03 | DX | Pre-commit hooks for lint + type check (husky + lint-staged) | `.husky/`, `apps/frontend/package.json` | S |~~ ✅ 2026-04-25
~~| M-04 | Testing | Backend coverage below 70% threshold in some modules — shore up children_service + lesson_plan_service | `apps/backend/tests/` | M |~~ ✅ 2026-04-25
~~| M-05 | Parents | Share-to-WhatsApp button on parent guides (high-engagement channel in target markets) | `apps/frontend/src/pages/GuideViewPage.tsx` | S |~~ ✅ 2026-04-25
~~| M-06 | Performance | Landing page Lighthouse performance score warning — audit and fix heaviest assets | `apps/frontend/src/pages/LandingPage.tsx`, `apps/frontend/src/assets/` | M |~~ ✅ 2026-04-25
| M-07 | Content | "How it works" section for parents needs real screenshots, not placeholders | `apps/frontend/src/pages/LandingPage.tsx` (HowItWorksSection) | S |
~~| M-08 | Security / Deps | Backend `requirements.txt` uses `>=` minimums — pin exact versions for reproducible builds | `apps/backend/requirements.txt` | S |~~ ✅ 2026-04-24
~~| M-09 | Security | Catalog GET endpoints (country / subject / curriculum / grade_level) currently have no auth guard. **Decision (2026-04-23): require authentication.** Add `Depends(get_current_active_user)` to all list/detail endpoints in `apps/backend/routers/country.py`, `curriculum.py`, `curriculum_structure.py`, `grade_level.py`, `subject.py`. Note: the signup form fetches countries/curricula before the user is logged in — either (a) fetch after login during onboarding, or (b) keep a single unauthenticated `/api/catalog/countries` stub for the signup dropdown only. Agent should implement option (a) since onboarding already runs post-login. | `apps/backend/routers/country.py`, `curriculum.py`, `curriculum_structure.py`, `grade_level.py`, `subject.py` | S |~~ ✅ 2026-04-24 (already implemented — all catalog GET endpoints confirmed using `Depends(get_current_user)`; tests in test_api_endpoints.py assert 401 for unauthenticated requests)
~~| M-10 | Security | Disable `/docs` and `/redoc` in production (gate on `ENVIRONMENT == "production"`) | `apps/backend/main.py` (lines 107-108) | S |~~ ✅ 2026-04-24
~~| M-11 | Security | Add `Content-Security-Policy` header to `SecurityHeadersMiddleware` | `apps/backend/middleware/security_headers.py` | S |~~ ✅ 2026-04-24
~~| M-12 | Security / AI | Wrap user-supplied prompt fields in delimiters + sanitisation. **Scope update (2026-04-22):** `context_input` in `LessonResourceCreate` IS a live injection surface — educator-supplied free text flows directly into `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` as `{local_context}` with only email/phone stripping, not instruction fencing. Add XML-style delimiters around user-supplied fields and reject/truncate strings containing instruction-like patterns. Parent guide flow is lower risk (topic data from DB). | `packages/ai/prompts.py`, `packages/ai/gpt_service.py`, `apps/backend/services/lesson_plan_service.py` | S |~~ ✅ 2026-04-24
~~| M-13 | Performance | N+1 in `ChildrenService.get_child_topics` — `t.curriculum_structure.subject.name` is accessed per topic without eager loading. A grade with ~80 topics issues ~160 extra queries. Fix with `joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject)` | `apps/backend/services/children_service.py` (lines 223-244) | S |~~ ✅ 2026-04-24
~~| M-14 | Performance | FK validation loops in `create_child` / `update_child` issue one query per subject / FK. Replace with a single `Subject.subject_id.in_(ids)` + count comparison | `apps/backend/services/children_service.py` (lines 118-133, 170-190) | S |~~ ✅ 2026-04-24
~~| M-15 | Frontend / Types | New children & guides methods in `api.ts` all return `ApiResponse<any>` — leaks untyped data to callers. Define `ChildProfile`, `ParentGuide`, `ChildTopic`, `ChildProfileListResponse`, `ParentGuideListResponse` in `apps/frontend/src/types/` and thread through the API client + pages | `apps/frontend/src/services/api.ts` (lines 648-760), `apps/frontend/src/types/`, `apps/frontend/src/pages/ParentDashboardPage.tsx`, `GuideViewPage.tsx`, `SavedGuidesPage.tsx` | M |~~ ✅ 2026-04-25
| M-16 | Data model | `child_profiles.subjects` stored as JSON-in-`Text` forecloses subject-level analytics (e.g. "which subjects do parents request most?") and makes filtering/joining impossible. Migrate to a proper `child_subjects` join table | `apps/backend/models.py` (`ChildProfile.subjects`), `apps/backend/alembic/versions/` (new migration), `apps/backend/services/children_service.py` | M |
| M-17 | DX / Migrations | **⚠️ Grooming note (2026-04-25): requires Tolu decision — pick one migration system before M-16 (join table) can land. Recommend scheduling this as the first M-effort item in the June prep sprint.** Three overlapping migration systems, none coherent: (a) `codebase-map.md` claims `apps/backend/alembic/versions/` "latest head includes ChildProfile + ParentGuide tables" — false; Alembic head is `a8a7efde9d3c_add_user_suspension` and the chain doesn't touch the parent tables. (b) `apps/backend/migrations/008_add_parent_role_and_child_profiles.py` is written as an Alembic migration (`revision='008'`, `down_revision='007'`) but lives outside `alembic/versions/` and its down_revision references a non-existent revision — unreachable via `alembic upgrade head`. (c) `migrate_database.py` actually provisions schema by calling `Base.metadata.create_all()`, which reflects `models.py` directly and silently ignores both migration folders — meaning schema drift (ALTER/DROP) is invisible and rollbacks are impossible. Fix: pick one system (recommend Alembic), port `001–008` into `alembic/versions/` chained from the current head, delete the sequential `migrations/` dir, update `migrate_database.py` to run `alembic upgrade head`, and correct `codebase-map.md` to match. Unblocks M-16 (which assumes Alembic is the active system) | `.claude/rules/codebase-map.md` (line 62), `apps/backend/migrations/*.py`, `apps/backend/alembic/versions/`, `apps/backend/migrate_database.py`, `run_migrations.py` | M |
| M-19 | UX / Mobile | Mobile responsiveness audit on mid-range Android devices — rebranding doc §7 Phase 5 calls for testing on actual hardware, not just browser dev tools. Covers parent flow pages + landing page | `apps/frontend/src/pages/ParentDashboardPage.tsx`, `GuideViewPage.tsx`, `SavedGuidesPage.tsx`, `LandingPage.tsx` | M |
| M-20 | AI / Quality | Prompt quality review — test "How to Help" guides across multiple topics, grade levels, and subjects. Verify tone is parent-friendly, not teacher-handbook. Rebranding doc §5.2 defines acceptance bar | `packages/ai/prompts.py`, `packages/ai/gpt_service.py` | M |
~~| M-21 | Parents | Guide export — add PDF/DOCX export button to GuideViewPage so parents can print guides for offline use (rebranding doc §5.1 confirms export service carries over) | `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/backend/routers/children.py` (new export endpoint) | M |~~ ✅ 2026-04-25
~~| M-18 | Code Hygiene | `SettingsPage.tsx` lines 207 and 213 contain `// TODO: Implement email update API call` and `// TODO: Implement password update API call` — violates CLAUDE.md rule (no TODO/FIXME in code; add backlog items instead). Remove the TODO comments and implement or defer via this backlog item. | `apps/frontend/src/pages/SettingsPage.tsx` (lines 207, 213) | S |~~ ✅ 2026-04-24
~~| M-36 | Security / Config | CORS middleware uses `allow_methods=["*"]` and `allow_headers=["*"]` in `apps/backend/main.py`. `allow_methods=["*"]` permits all HTTP methods (including `DELETE`, `PUT`, `PATCH`) cross-origin, which is broader than necessary. Fix: restrict to the methods and headers actually used by the frontend — e.g. `allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` (or fewer) and `allow_headers=["Authorization", "Content-Type", "X-Requested-With"]`. Low exploitation risk given the origin allowlist and auth guards, but defence-in-depth best practice. Filed: 2026-04-24 Security Agent. | `apps/backend/main.py` (CORS middleware block) | S |~~ ✅ 2026-04-24
~~| M-43 | Security | `style-src 'unsafe-inline'` remains in the CSP after the AWD-M-35 short-term fix. The in-code comment (`security_headers.py` line 24-25) acknowledges this as deferred, but M-35 was marked fully done in the backlog with no separate open ticket tracking the remaining work. Fix: implement a nonce-based or hash-based `style-src` policy — generate a per-request nonce in `SecurityHeadersMiddleware.dispatch`, inject it into `style-src 'nonce-{value}'`, and expose it via `request.state.csp_nonce` for any inline styles the frontend needs. Alternatively, migrate all inline styles to external stylesheets (already loaded via `'self'`) and set `style-src 'self'` with no nonce. See OWASP CSP Cheat Sheet. Risk: `'unsafe-inline'` in `style-src` allows CSS injection (data exfiltration via `background-image: url(...)`, history sniffing, UI redressing). Lower severity than script-src but still a real attack surface. Filed: 2026-04-25 QA Agent (spot-check of AWD-M-35 commit fb9e718). | `apps/backend/middleware/security_headers.py` (line 30), `apps/backend/tests/test_security.py` (add test asserting `style-src` lacks `unsafe-inline` once fixed) | M |~~ ✅ 2026-04-25
~~| M-44 | Testing | `test_rate_limiting` in `apps/backend/tests/test_security.py` (line 171) is a hollow test — body is `pass` with no assertions. It is marked `@pytest.mark.asyncio` but does nothing. Per testing standards (`.claude/rules/testing.md`), a test without assertions that should be skipped must use `@pytest.mark.skip(reason="AWD-<id> <reason>")`. Fix: either (a) implement the test using `respx` or a mock to simulate rate-limit state and assert a 429 after N requests, or (b) add `@pytest.mark.skip(reason="AWD-M-44 TestClient shares limiter state — needs rate_limiter_reset fixture from AWD-H-29 approach")` until a real implementation is feasible. Pre-existed commit fb9e718; discovered during spot-check. | `apps/backend/tests/test_security.py` (line 171) | S |~~ ✅ 2026-04-25
~~| M-35 | Security | `Content-Security-Policy` uses `'unsafe-inline'` for both `script-src` and `style-src`, significantly weakening XSS protection. The CSP added in AWD-M-11 (`apps/backend/middleware/security_headers.py` lines 25-26) allows all inline scripts and styles, which is the primary attack surface CSP is designed to block. Fix: replace `'unsafe-inline'` with a nonce-based or hash-based approach. For `style-src`, consider allowing only specific hashes for known inline styles, or migrate styles to external stylesheets. For `script-src`, implement nonce injection via middleware (generate a UUID nonce per request, inject as `request.state.csp_nonce`, template into responses). Alternatively, as a short-term measure, remove `'unsafe-inline'` from `script-src` (more critical — scripts are higher risk than styles) and test that the frontend still functions correctly. See OWASP CSP cheat sheet for nonce implementation guidance. | `apps/backend/middleware/security_headers.py` (lines 25-26) | M |~~ ✅ 2026-04-25 (short-term fix shipped: unsafe-inline removed from script-src; style-src nonce hardening deferred)
~~| M-36 | Accessibility / HTML | `ParentDashboardPage.tsx` lines 168–203: child selector cards are `<button>` elements that contain nested `<button>` elements (Edit, Delete). This is invalid HTML per spec — `<button>` cannot be a descendant of `<button>`. Browsers handle it inconsistently; keyboard navigation and screen readers may break (WCAG 2.1 failure). Fix: convert the outer card to `<div role="group">` (with `tabIndex`, `onClick`, `onKeyDown` handlers) so the edit/delete buttons are descendants of a non-interactive container, not a button. Or restructure layout so action buttons are siblings to the selector, not children. Reproduces as `validateDOMNesting` warning in vitest output. Filed by QA Agent 2026-04-24. | `apps/frontend/src/pages/ParentDashboardPage.tsx` (lines 168–203) | S |~~ ✅ 2026-04-24
~~| M-37 | SEO / OG | AWD-M-02 shipped OG and Twitter Card meta tags pointing to `og-image.svg`. SVG is not a supported format for Open Graph images — Facebook, WhatsApp, LinkedIn, and most crawlers require JPEG or PNG (1200×630). As a result, no preview image will render when awade.app is shared on these platforms, defeating the purpose of the feature. Fix: (1) convert `apps/frontend/public/og-image.svg` to `og-image.png` (use `cairosvg`, ImageMagick, or Inkscape CLI: `inkscape og-image.svg --export-type=png --export-filename=og-image.png`); (2) update both `og:image` and `twitter:image` in `apps/frontend/index.html` to reference `og-image.png`; (3) keep the `.svg` source file for easy future edits. Filed: 2026-04-24 QA Agent. | `apps/frontend/index.html` (lines 22, 36), `apps/frontend/public/og-image.svg` → `og-image.png` | S |~~ ✅ 2026-04-24

---

## 🟢 Low / Polish

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
| L-01 | DX | CI cache key for pip dependencies (backend-test is slow on every run) | `.github/workflows/ci.yml` | S |
| L-02 | Docs | Update `docs/public/api/README.md` with parent/children endpoints | `docs/public/api/` | S |
| L-03 | A11y | Run WCAG 2.1 AA audit on parent flow, file specific items | `apps/frontend/src/pages/Parent*.tsx`, `GuideViewPage.tsx` | M |
| L-04 | Security | Re-enable `TrustedHostMiddleware` with `ALLOWED_HOSTS` env var in production | `apps/backend/main.py` (lines 133-135) | S |
| L-05 | Code hygiene | `require_parent` and `require_any_role` added to `dependencies.py` but never imported. Either wire `require_parent` into `children.py` router `dependencies=[...]` (fails earlier with 403) or delete the helpers | `apps/backend/dependencies.py` (lines 168, 170), `apps/backend/routers/children.py` | S |
| L-06 | Data model | `ParentGuide.is_bookmarked` uses `Integer` (0/1) instead of `Boolean` — response schema already coerces with `bool(...)`, so the column type should match. Small alembic migration + model tweak | `apps/backend/models.py` (ParentGuide), `apps/backend/alembic/versions/` (new migration) | S |
| L-07 | Compatibility | `GoogleAuthRequest.role` now defaults to `"PARENT"` — any existing client that calls `/auth/google` without passing a role will create parents instead of educators (a behaviour change from the prior EDUCATOR default). Confirm no older mobile/web clients are still in the wild; otherwise make `role` required | `apps/backend/routers/auth.py` (line 44) | S | **⚠️ Grooming note (2026-04-25): requires Tolu decision — are any pre-pivot educator clients still active? Block on Tolu confirmation before closing.**
| L-10 | Docs / Config | `project-config.md` §5 `ERROR_MONITORING` still reads "not yet connected (Sentry recommended — flagged as H-01)". AWD-H-01 shipped in commit 364762f — update the line to reflect Sentry is now wired for both backend (`sentry-sdk[fastapi]==2.58.0`) and frontend (`@sentry/react ^8.0.0`). Filed: 2026-04-23 QA. **Grooming note (2026-04-25): trivially bundleable with any doc/config commit. S = minutes.** | `project-config.md` (§5, line ~28) | S |
| L-09 | DX / Frontend | React Router v7 future flag warnings in frontend test output — `v7_startTransition` and `v7_relativeSplatPath` flags not set on `<BrowserRouter>`. Will become breaking changes in v7. Fix: add `future={{ v7_startTransition: true, v7_relativeSplatPath: true }}` to the `<BrowserRouter>` or `<RouterProvider>` in `apps/frontend/src/App.tsx`. Filed: 2026-04-22 QA. | `apps/frontend/src/App.tsx` | S |
| L-11 | Security / Deps | `Pillow==10.0.0` pinned in `requirements.txt` (AWD-M-08). Multiple CVEs affect Pillow versions below 10.3.0, including CVE-2024-28219 (heap buffer overflow in `ImagingResampleHorizontal`). Current pin may be intentional for compatibility but should be reviewed and upgraded to `Pillow>=10.3.0` (or latest stable) if no breaking change. Check release notes for Pillow 10.x before bumping. Filed: 2026-04-24 QA Agent. | `apps/backend/requirements.txt` | S |
~~| L-12 | Code Hygiene | `GeminiProvider` class docstring (line 20) is stale after AWD-M-39 migration: still says "Uses 'gemini-1.5-pro' for standard tier and 'gemini-1.5-flash' for basic tier" but the code returns `gemini-flash-latest` for both tiers. Also: `import re` is done inline inside `generate_content()` (line 98) rather than at module top — minor convention violation. Fix: (1) update docstring to reflect `gemini-flash-latest`; (2) move `import re` to module-level imports. Effort: S. Filed: 2026-04-25 QA Agent. | `packages/ai/providers/gemini_provider.py` (lines 20-21, 98) | S |~~ ✅ 2026-04-25

---

## 🟡 Medium (continued)

~~| M-39 | Security / Deps + AI | Two related issues: **(A)** `openai==1.12.0` is ~70 minor versions behind latest 1.x (1.82+). Pinned at 1.12.0 for API compatibility (AWD-M-08 comment) but no breaking changes occur within 1.x — the gap means missed security patches. Fix: upgrade to `openai>=1.82.0` (latest stable 1.x), run backend tests to confirm no breakage. **(B)** `generate_lesson_resource()` cache metadata (line 505) stores `"context": context` (original unsanitized value) instead of `"context": safe_context`. If ContentCache persists metadata to Redis as JSON, unsanitized educator input is stored in Redis (injection risk is low since the prompt uses `safe_context`, but defence-in-depth gap). Fix: change `"context": context` → `"context": safe_context` at line 505. | `apps/backend/requirements.txt`, `packages/ai/gpt_service.py` (line 505) | S |~~ ✅ 2026-04-25
~~| M-38 | Code Quality / Types | `_sanitize_user_context` in `packages/ai/gpt_service.py` is typed `(text: str) -> str` but the companion test `test_returns_empty_for_none` documents it accepts `None` and returns `None`. The production caller correctly guards with `if context else None` so `None` is never passed at runtime, but the type annotation is incorrect — should be `Optional[str] -> Optional[str]`. Fix: update type hints to `def _sanitize_user_context(self, text: Optional[str]) -> Optional[str]` and add the `Optional` import. Filed: 2026-04-24 QA Agent (spotted during AWD-M-12 review). | `packages/ai/gpt_service.py` (line ~231), `apps/backend/tests/test_ai_providers.py` (`test_returns_empty_for_none`) | S |~~ ✅ 2026-04-25

---

## 🟣 Compliance (GRC)

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
| GRC-01 | COPPA | Parental consent flow before first ChildProfile creation (plain-language disclosure + explicit opt-in, dated record) | `apps/backend/routers/children.py`, `apps/frontend/src/pages/ParentDashboardPage.tsx`, new consent table | M |
| GRC-02 | GDPR | Data export endpoint — allow a parent to download all their data + their children's data as JSON | `apps/backend/routers/users.py` (new endpoint), `apps/backend/services/user_service.py` | M |
| GRC-03 | GDPR | Account deletion endpoint with cascade for ChildProfile + ParentGuide | `apps/backend/routers/users.py`, migrations (cascade rules) | M |
| GRC-04 | NDPR/POPIA | Data-residency note in privacy policy — document where Awade stores African parent/child data | `docs/public/external/`, privacy policy file | S |
| GRC-05 | COPPA | Audit logs for any admin access to a ChildProfile | `apps/backend/models.py` (AdminAuditLog — verify coverage), `apps/backend/routers/admin.py` | S |

---

## ✅ Done

> Completed items live in [`completed_backlog.md`](completed_backlog.md) to keep this file focused on active work.

---

## Issue Template
When adding a new issue, use this format:

```
**AWD-H-XX — [Title]**
**Problem**: [What's broken or missing, from the user's perspective]
**Acceptance criteria**:
- [ ] [Specific, testable condition]
- [ ] [Another]
**Files**: [Relevant file paths from .claude/rules/codebase-map.md]
**Effort**: S (hours) | M (1 day) | L (2 days) | XL (needs breakdown)
**Audience**: parent | educator | admin | all
```
