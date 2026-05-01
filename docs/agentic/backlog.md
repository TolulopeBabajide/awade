# Awade — Backlog

> Last updated: 2026-04-30 (code-review-agent — filed AWD-H-61 SUPER_ADMIN bypass gap in M-67 fix, AWD-M-70 router/service duplication)
> Prev updated: 2026-04-30 (Lead Dev Agent — AWD-M-67 resolved: uniform 404 for unauthorized lesson resource IDs; AWD-H-60 resolved: .env.example restored to HEAD)
> Prev updated: 2026-04-30 (code-review-agent — filed AWD-H-60 working tree divergence, AWD-M-69 JWT lifetime callout)
> Prev updated: 2026-04-30 (Lead Dev Agent — AWD-M-66 resolved: duplicate JWT vars and merge artifact removed from .env.example)
> Prev update: 2026-04-30 (Lead Dev Agent — AWD-H-58 resolved: staging area cleared; TestPage.tsx no longer staged; residual untracked file on disk — Tolu to `rm apps/frontend/src/pages/TestPage.tsx` locally)
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

~~**AWD-C-08 — Docs commit `e606029` silently reverted AWD-M-43 CSP security fix**~~ ✅ 2026-04-26

~~**AWD-C-09 — Chore commits `c3ae0c4` and `d235cc5` corrupted develop: `c3ae0c4` reverted AWD-M-52 websocket fix and `d235cc5` mass-deleted 312 files**~~ ✅ 2026-04-27

~~**AWD-C-10 — Chore commit `0a00d4f` silently reverted AWD-M-55 `aria-invalid` / `aria-describedby` fixes**~~ ✅ 2026-04-28

~~**AWD-C-11 — Chore commit `e28dedb` silently reverted AWD-M-61 ConsentModal.test.tsx act()+fireEvent fix**~~ ✅ 2026-04-29

---

## 🟠 High

~~| M-41 | Code Quality / Types | **AWD-M-04 test commit stripped AWD-M-15 type safety work — uncommitted fix is sitting in working tree.** Commit `7fe0c3b` (`test(backend): AWD-M-04 add service-layer tests…`) accidentally included working-tree reversions to `api.ts` and `children.ts` that undo the typed-API work shipped in AWD-M-15 (commit `663b50a`). **Exact regressions in committed HEAD**: (1) `apps/frontend/src/types/children.ts` — 3 interfaces deleted: `ChildProfileUpdate`, `ChildProfileListResponse`, `ParentGuideListResponse`; (2) `apps/frontend/src/services/api.ts` — typed import block removed; 6 children/guide API methods downgraded from specific return types to `ApiResponse<any>` (`getChildren`, `getChild`, `createChild`, `updateChild`, `deleteChild`, `getChildTopics`, `getChildGuides`). **The fix already exists in the working tree (unstaged/uncommitted)** — it restores all 3 interfaces and re-applies proper typed returns. The working tree also contains two bonus improvements not yet committed: `GuideViewPage.tsx` — two `if (!res.data)` null guards added after the error check; `ParentDashboardPage.tsx` — replaces unsafe `res.data as ChildTopic[]` cast with safe `res.data ?? []`. **Fix**: run `git add apps/frontend/src/types/children.ts apps/frontend/src/services/api.ts apps/frontend/src/pages/GuideViewPage.tsx apps/frontend/src/pages/ParentDashboardPage.tsx` then commit: `fix(frontend): AWD-M-41 restore typed API interfaces stripped in AWD-M-04 test commit`. Do NOT push develop until this is committed — the committed HEAD has type regressions and 3 deleted interfaces. Filed: 2026-04-25 QA Agent. | `apps/frontend/src/types/children.ts`, `apps/frontend/src/services/api.ts`, `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/frontend/src/pages/ParentDashboardPage.tsx` | S |~~ ✅ 2026-04-25

---

~~**AWD-C-05 — git repo corruption: `refs/heads/develop` points to missing commit object**~~ ✅ 2026-04-29
**Problem**: `refs/heads/develop` contains SHA `187bd80b8614c9f84ff3a69f0cddb39a2e31e24b`, which does not exist in `.git/objects/`. All git operations on the develop branch fail (`git log`, `git status`, `git commit`, `git push`). Development and CI pushes are fully blocked.
**Root cause**: An interrupted git commit operation (likely disk-full condition in QA sandbox) left `tmp_obj_*` temporaries in `.git/objects/` and never finalized the commit object. Files for H-22 and H-26 fixes are safely on disk but uncommitted.
**Resolution**: Verified 2026-04-29 — `refs/heads/develop` now points to `d9c4b60e968fcad6526ee8667a68e9b3e394a7f9` (valid commit object). Develop has 57+ commits since this was filed; git log, status, and commit all work. The corruption was resolved (likely via the local-clone workaround or Tolu running `git update-ref` directly). All acceptance criteria met.
**Files**: `.git/refs/heads/develop` (fix only — no app code change needed)
**Effort**: S (minutes, but requires Tolu to run commands locally on their Mac)
**Note**: QA sandbox cannot write to the user's git repo — Tolu must run the recovery commands locally.

---

## 🟠 High

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| H-58 | Code Hygiene / Git | **Staged index reverts AWD-M-65 fix — TestPage.tsx persists on disk and is staged for re-commit.** After commit `359b4a5` (AWD-M-65) correctly deleted `TestPage.tsx` and removed the `/test` route, the git staging area (index) has been populated with changes that undo the commit: (1) `import TestPage` re-added to `App.tsx`, (2) the `/test` route block re-added to `App.tsx`, (3) `TestPage.tsx` staged as a new file (120 lines). `TestPage.tsx` also physically exists on disk. If any agent or developer runs `git commit` without reviewing `git diff --cached`, AWD-M-65 will silently regress. **Fix**: `git restore --staged apps/frontend/src/App.tsx apps/frontend/src/pages/TestPage.tsx && rm apps/frontend/src/pages/TestPage.tsx` — confirm with `git status` before next commit. Filed: 2026-04-30 code-review-agent. | `apps/frontend/src/App.tsx` (staged), `apps/frontend/src/pages/TestPage.tsx` (staged + on disk) | S | Stage: ready |~~ ✅ 2026-04-30
~~| H-56 | Performance / Build | **ChatGPT prototype images blocking Vite build and adding 7.4MB to dist.** 4 ChatGPT-exported `.png` files (`ChatGPT Image Aug 12, 2025, 12_14_13 PM.png`, `12_14_16 PM.png`, `12_19_01 PM.png`, `12_54_32 AM.png`) are present in `apps/frontend/src/assets/` and `apps/frontend/public/assets/`. They are not imported or referenced in any component (confirmed via grep). Impact: (1) `npm run build` fails with `EPERM: operation not permitted, unlink` on any machine with a prior dist/ — CI and local rebuilds are broken. (2) ~7.4MB of dead weight in the deployment artifact. Fix: `git rm "apps/frontend/src/assets/ChatGPT Image"* "apps/frontend/public/assets/ChatGPT Image"*`, add `ChatGPT*` to `.gitignore` under those dirs, commit: `chore(frontend): AWD-H-56 remove ChatGPT prototype images blocking build`. Filed: 2026-04-29 performance-agent. | `apps/frontend/src/assets/ChatGPT Image*.png` (×4), `apps/frontend/public/assets/ChatGPT Image*.png` (×4), `.gitignore` | S |~~ ✅ 2026-04-30
~~| H-42 | Compliance / GRC-02 | **Commit `5d9af8e` (AWD-H-03) accidentally deleted the GRC-02 GDPR data-export endpoint.** `GET /api/users/me/data-export`, `UserService.get_data_export()`, its imports (`ChildProfile`, `ParentGuide`, `Topic`), and the GRC-02 tests in `test_users_router.py` were all removed as a side-effect of the admin panel commit. The backend will return 500 for any data-export request. **The fix already exists as uncommitted local changes on disk** — the dev agent wrote the restore but never staged it. **Fix (copy-paste ready)**: `git add apps/backend/routers/users.py apps/backend/services/user_service.py apps/backend/tests/test_users_router.py && git commit -m "fix(users): AWD-H-42 restore GRC-02 data-export endpoint deleted in H-03 commit"`. Verify: `GET /api/users/me/data-export` returns 200 with user + children payload; unauthenticated returns 401. Filed: 2026-04-26 QA Agent. | `apps/backend/routers/users.py` (add `/me/data-export` endpoint), `apps/backend/services/user_service.py` (add `get_data_export()` + imports), `apps/backend/tests/test_users_router.py` (GRC-02 test cases) | S |~~ ✅ 2026-04-26
~~| H-41 | Testing / TypeScript | `GuideViewPage.test.tsx` (introduced by AWD-M-05 commit f4ebdb3) has 6 TypeScript errors and 1 failing test. **TS errors**: (1) `React` imported but never used (TS6133, line 1); (2) 5× `null` not assignable to `string \| undefined` (TS2322, lines 116, 125, 134, 146, 155) — `generateGuide` mock args use `null` for optional string params but the function signature expects `string \| undefined`. Fix: remove the `React` import; change the 5× `null` literals to `undefined`. **Test failure**: `renders guide via generateGuide when child+topic params are supplied (no guide ID)` — component renders an empty `<main>` instead of the expected `Fractions` heading, suggesting the `generateGuide` mock is not resolving (missing `await waitFor(...)` wrapper or mock data mismatch). Fix: wrap the assertion in `await waitFor(() => expect(screen.getByRole(...)).toBeInTheDocument())` and verify the mock return value shape matches what the component renders. Blocks CI `frontend-test` and `validate` jobs once Tolu pushes. Filed: 2026-04-25 QA Agent. | `apps/frontend/src/pages/GuideViewPage.test.tsx` (lines 1, 116, 125, 134, 146, 155, ~140) | S |~~ ✅ 2026-04-25
~~| H-40 | Security / Error Handling | `lesson_plans.py` export endpoint leaks internal error details via `str(e)` in HTTPException detail (OWASP A09 information disclosure). `export_lesson_resource` lines 219–223: `detail=f"An error occurred while exporting the resource: {str(e)}"` — can expose WeasyPrint stack traces, file paths, or SQL errors to the client. Same class as AWD-H-18 (fixed service files) but missed this router-level handler. Fix: add `logger = logging.getLogger(__name__)` to imports and replace the except block with a static detail string + `logger.error(..., exc_info=True)`. | `apps/backend/routers/lesson_plans.py` (lines 219–223) | S |~~ ✅ 2026-04-25
~~| H-27 | Testing | `test_contexts_router.py` — 8 tests fail with `AttributeError: 'NoneType' object has no attribute 'set'`. Root cause: `_make_educator` / `_make_admin` call `User.__new__(User)` which bypasses SQLAlchemy's `__init__`, leaving `_sa_instance_state = None` so attribute assignment fails. Fix: replace `User.__new__(User)` with `User()` (transient instances are fine — no session needed) and set fields via constructor kwargs or direct attribute assignment after `__init__` has run. | `apps/backend/tests/test_contexts_router.py` (lines 22-27, 30-35) | S |~~ ✅ 2026-04-22
~~| H-28 | Testing | `test_auth_flow_security.py::TestExceptionDetailSanitization` — 3 tests assert `status_code == 500` after injecting a `RuntimeError` via `side_effect`, but receive `422`. Pydantic rejects the empty `{}` payloads at the validation layer before the route handler (and the mock) is ever reached. Fix: supply valid request bodies (email + password fields for login/register, token field for google-auth) so requests clear validation and hit the mocked service code path. | `apps/backend/tests/test_auth_flow_security.py` (`TestExceptionDetailSanitization` class) | S |~~ ✅ 2026-04-22
~~| H-29 | Testing | Rate-limiter state not reset between test files — 6 tests in `test_auth_flow_security.py` pass in isolation but fail when the full suite runs: `test_login_sets_httponly_cookie`, `test_refresh_token_flow` (fails `assert 429`), `TestAccountEnumerationProtection` (3 tests), and `TestExceptionDetailSanitization::test_login_db_error_does_not_leak_exception` (added after AWD-H-28 fix revealed this). Root cause: earlier test files exhaust the in-memory rate-limiter for the `/api/auth/login` endpoint; subsequent tests receive 429 instead of the expected 200/401/500. Fix: in `apps/backend/tests/conftest.py`, add a `rate_limiter_reset` autouse fixture that clears the rate-limiter storage between each test (e.g. `app.state.limiter.reset()` or equivalent for the limiter implementation in `apps/backend/limiter.py`). Discovered in full-suite run during QA of AWD-H-18. | `apps/backend/tests/conftest.py`, `apps/backend/limiter.py` | S |~~ ✅ 2026-04-22
~~| H-32 | Parents / Error Handling | `ParentOnboardingPage.tsx`: `loadRefData()` (lines 49-59) and `loadCurriculums()` (lines 69-73) have no try/catch. If any of the three parallel reference-data calls (countries, grades, subjects) or the curriculum fetch fails, the error is silently swallowed and the user sees empty dropdowns with no message. Fix: wrap both async bodies in try/catch; on error call `setError('Failed to load options. Please refresh.')`. Regression in AWD-H-20. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (lines 49-59, 69-73) | S |~~ ✅ 2026-04-23
~~| H-01 | Observability | Wire up Sentry (or equivalent) for error monitoring — backend + frontend | `apps/backend/main.py`, `apps/backend/middleware/`, `apps/frontend/src/main.tsx` | M |~~ ✅ 2026-04-23
~~| H-33 | CI / Observability | Commit `b552efe` accidentally reverted AWD-H-01 Sentry stack and broke CI — see detail below | multiple | S |~~ ✅ 2026-04-23
~~| H-03 | Admin | Admin panel has no parent / child management views yet | `apps/backend/routers/admin.py`, `apps/frontend/src/pages/` (admin) | L |~~ ✅ 2026-04-26
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
| M-62 | Performance / Build | **Expand Vite vendor chunk split to reduce initial JS parse cost.** Current `manualChunks` only splits `react-router-dom` (160.5KB) and `@tanstack/react-query` (35.5KB). The main app chunk (282.5KB) bundles `@react-oauth/google`, `@sentry/react`, `@heroicons/react`, `react-icons`, and `react`+`react-dom` together. These stable vendor deps should be in long-lived cached chunks. Proposed split: `vendor-react` (react+react-dom), `vendor-auth` (@react-oauth/google), `vendor-sentry` (@sentry/react), `vendor-icons` (@heroicons/react + react-icons). This will reduce cache-busting surface area on feature deploys and allow browsers to parallelise chunk fetches. **Prerequisite: resolve AWD-H-56 first so the build is unblocked.** Filed: 2026-04-29 performance-agent. | `apps/frontend/vite.config.ts` (build.rollupOptions.output.manualChunks) | S |
| M-63 | Performance / DB | **`curriculum_structure.py` create/update issue 3 sequential FK queries per request.** `POST /curriculum-structures/` (lines 51–66) and `PUT /curriculum-structures/{id}` (lines 111–126) each fire 3 individual `db.query()` calls to validate the related Curriculum, GradeLevel, and Subject records after the write. These should be replaced with a single `joinedload` query or pre-write bulk validation. Fix: refetch the new/updated structure with `joinedload(CurriculumStructure.curriculum).joinedload(CurriculumStructure.grade_level).joinedload(CurriculumStructure.subject)` in one query, eliminating the 3 post-write lookups. Low traffic route currently; worth fixing before parent-scale launch. Filed: 2026-04-29 performance-agent. | `apps/backend/routers/curriculum_structure.py` (lines 51–66, 111–126) | S |
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
~~| M-07 | Content | "How it works" section for parents needs real screenshots, not placeholders | `apps/frontend/src/pages/LandingPage.tsx` (HowItWorksSection) | S |~~ ✅ 2026-04-29 (commit `2eded61` / merge `e1fef37` — replaced text-only numbered circles with three inline SVG phone-frame mockups depicting the Add Child form, Topics browser, and Guide view; 5 new vitest tests in HowItWorksSection.test.tsx)
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

~~**AWD-H-49 — Missing rate limiter on `GET /api/users/me/data-export`**~~ ✅ 2026-04-26
**Problem**: The GDPR data-export endpoint added in AWD-GRC-02 has no `@limiter.limit()` decorator. The endpoint performs a multi-table DB scan (user → child_profiles → parent_guides → topics) — an authenticated user who hammers it in a loop can cause sustained DB load and degrade performance for all users. Every other data-intensive or sensitive route in the project is rate-limited (see `auth.py`: 5–20 req/min; `children.py` AI endpoint: 5/min).
**Acceptance criteria**:
- [ ] `@limiter.limit("5/minute")` (or similar conservative value) added to `export_my_data` in `apps/backend/routers/users.py`
- [ ] `from apps.backend.limiter import limiter` imported in `users.py`
- [ ] A test in `test_users_router.py` verifies that a 429 is returned after the rate limit is exceeded (or skip with backlog ref if rate-limiter test fixture is not yet available — see AWD-M-44)
**Files**: `apps/backend/routers/users.py` (export_my_data decorator), `apps/backend/tests/test_users_router.py`
**Effort**: S (minutes)
**Audience**: all
**Filed**: 2026-04-26 QA Agent (spot-check of commit 2e598f0)

---

~~**AWD-H-50 — `openapi.json` not regenerated after GRC-01 — consent + all children/guide routes missing from spec**~~ ✅ 2026-04-27

**Problem**: Commit `07ca8e9` (AWD-GRC-01) added 2 new consent endpoints (`GET /api/consent/status`, `POST /api/consent`) to `apps/backend/routers/children.py` but did not regenerate `apps/backend/app/openapi.json`. Additionally, all existing children and guide routes (`/api/children`, `/api/children/{child_id}`, `/api/children/{child_id}/topics`, `/api/children/{child_id}/guides`, `/api/children/{child_id}/guides/generate`, `/api/guides/{guide_id}`, `/api/guides/{guide_id}/bookmark`, `/api/guides/{guide_id}/export`) are absent from the spec — a pre-existing gap, compounded by this commit. `CLAUDE.md` requires: "If the change touches API endpoints, regenerate `apps/backend/app/openapi.json`". The `contract-test` CI job validates the JSON but not completeness, so CI may appear green locally — but the spec is stale and any API consumer check against it will miss these endpoints entirely.

**Acceptance criteria**:
- [ ] Start the FastAPI app and regenerate: `python -c "import json; from apps.backend.main import app; print(json.dumps(app.openapi(), indent=2))" > apps/backend/app/openapi.json`
- [ ] Confirm `/api/consent/status`, `/api/consent`, `/api/children`, `/api/children/{child_id}`, `/api/children/{child_id}/topics`, `/api/children/{child_id}/guides`, `/api/children/{child_id}/guides/generate`, `/api/guides/{guide_id}`, `/api/guides/{guide_id}/bookmark`, `/api/guides/{guide_id}/export` all appear in the regenerated spec
- [ ] `python3 -m json.tool apps/backend/app/openapi.json >/dev/null` passes
- [ ] Commit: `docs(api): AWD-H-50 regenerate openapi.json to include consent, children, and guide routes`

**Files**: `apps/backend/app/openapi.json`
**Effort**: S (minutes — regeneration only, no code changes)
**Audience**: internal / CI
**Filed**: 2026-04-27 QA Agent (spot-check of 07ca8e9)

---

## 🟢 Low / Polish

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| L-01 | DX | CI cache key for pip dependencies (backend-test is slow on every run) | `.github/workflows/ci.yml` | S |~~ ✅ 2026-04-26
~~| L-02 | Docs | Update `docs/public/api/README.md` with parent/children endpoints | `docs/public/api/` | S |~~ ✅ 2026-04-26
~~| L-03 | A11y | Run WCAG 2.1 AA audit on parent flow, file specific items | `apps/frontend/src/pages/Parent*.tsx`, `GuideViewPage.tsx` | M |~~ ✅ 2026-04-27 — see [`docs/agentic/audits/a11y-parent-flow-2026-04-27.md`](audits/a11y-parent-flow-2026-04-27.md). 13 findings filed as AWD-H-52..55, AWD-M-53..57, AWD-L-13..16.
~~| L-04 | Security | Re-enable `TrustedHostMiddleware` with `ALLOWED_HOSTS` env var in production | `apps/backend/main.py` (lines 133-135) | S |~~ ✅ 2026-04-26
~~| L-05 | Code hygiene | `require_parent` and `require_any_role` added to `dependencies.py` but never imported. Either wire `require_parent` into `children.py` router `dependencies=[...]` (fails earlier with 403) or delete the helpers | `apps/backend/dependencies.py` (lines 168, 170), `apps/backend/routers/children.py` | S |~~ ✅ 2026-04-26
~~| L-06 | Data model | `ParentGuide.is_bookmarked` uses `Integer` (0/1) instead of `Boolean` — response schema already coerces with `bool(...)`, so the column type should match. Small alembic migration + model tweak | `apps/backend/models.py` (ParentGuide), `apps/backend/alembic/versions/` (new migration) | S |~~ ✅ 2026-04-27
| L-07 | Compatibility | `GoogleAuthRequest.role` now defaults to `"PARENT"` — any existing client that calls `/auth/google` without passing a role will create parents instead of educators (a behaviour change from the prior EDUCATOR default). Confirm no older mobile/web clients are still in the wild; otherwise make `role` required | `apps/backend/routers/auth.py` (line 44) | S | **⚠️ Grooming note (2026-04-25): requires Tolu decision — are any pre-pivot educator clients still active? Block on Tolu confirmation before closing.**
~~| L-10 | Docs / Config | `project-config.md` §5 `ERROR_MONITORING` still reads "not yet connected (Sentry recommended — flagged as H-01)". AWD-H-01 shipped in commit 364762f — update the line to reflect Sentry is now wired for both backend (`sentry-sdk[fastapi]==2.58.0`) and frontend (`@sentry/react ^8.0.0`). Filed: 2026-04-23 QA. **Grooming note (2026-04-25): trivially bundleable with any doc/config commit. S = minutes.** | `project-config.md` (§5, line ~28) | S |~~ ✅ 2026-04-26
~~| L-09 | DX / Frontend | React Router v7 future flag warnings in frontend test output — `v7_startTransition` and `v7_relativeSplatPath` flags not set on `<BrowserRouter>`. Will become breaking changes in v7. Fix: add `future={{ v7_startTransition: true, v7_relativeSplatPath: true }}` to the `<BrowserRouter>` or `<RouterProvider>` in `apps/frontend/src/App.tsx`. Filed: 2026-04-22 QA. | `apps/frontend/src/App.tsx` | S |~~ ✅ 2026-04-26
~~| L-11 | Security / Deps | `Pillow==10.0.0` pinned in `requirements.txt` (AWD-M-08). Multiple CVEs affect Pillow versions below 10.3.0, including CVE-2024-28219 (heap buffer overflow in `ImagingResampleHorizontal`). Current pin may be intentional for compatibility but should be reviewed and upgraded to `Pillow>=10.3.0` (or latest stable) if no breaking change. Check release notes for Pillow 10.x before bumping. Filed: 2026-04-24 QA Agent. | `apps/backend/requirements.txt` | S |~~ ✅ 2026-04-26
~~| L-12 | Code Hygiene | `GeminiProvider` class docstring (line 20) is stale after AWD-M-39 migration: still says "Uses 'gemini-1.5-pro' for standard tier and 'gemini-1.5-flash' for basic tier" but the code returns `gemini-flash-latest` for both tiers. Also: `import re` is done inline inside `generate_content()` (line 98) rather than at module top — minor convention violation. Fix: (1) update docstring to reflect `gemini-flash-latest`; (2) move `import re` to module-level imports. Effort: S. Filed: 2026-04-25 QA Agent. | `packages/ai/providers/gemini_provider.py` (lines 20-21, 98) | S |~~ ✅ 2026-04-25

---

## 🟡 Medium (continued)

~~| M-39 | Security / Deps + AI | Two related issues: **(A)** `openai==1.12.0` is ~70 minor versions behind latest 1.x (1.82+). Pinned at 1.12.0 for API compatibility (AWD-M-08 comment) but no breaking changes occur within 1.x — the gap means missed security patches. Fix: upgrade to `openai>=1.82.0` (latest stable 1.x), run backend tests to confirm no breakage. **(B)** `generate_lesson_resource()` cache metadata (line 505) stores `"context": context` (original unsanitized value) instead of `"context": safe_context`. If ContentCache persists metadata to Redis as JSON, unsanitized educator input is stored in Redis (injection risk is low since the prompt uses `safe_context`, but defence-in-depth gap). Fix: change `"context": context` → `"context": safe_context` at line 505. | `apps/backend/requirements.txt`, `packages/ai/gpt_service.py` (line 505) | S |~~ ✅ 2026-04-25
~~| M-38 | Code Quality / Types | `_sanitize_user_context` in `packages/ai/gpt_service.py` is typed `(text: str) -> str` but the companion test `test_returns_empty_for_none` documents it accepts `None` and returns `None`. The production caller correctly guards with `if context else None` so `None` is never passed at runtime, but the type annotation is incorrect — should be `Optional[str] -> Optional[str]`. Fix: update type hints to `def _sanitize_user_context(self, text: Optional[str]) -> Optional[str]` and add the `Optional` import. Filed: 2026-04-24 QA Agent (spotted during AWD-M-12 review). | `packages/ai/gpt_service.py` (line ~231), `apps/backend/tests/test_ai_providers.py` (`test_returns_empty_for_none`) | S |~~ ✅ 2026-04-25
~~| M-61 | Testing / Regression | **AWD-L-13 commit `9573817` silently reverted the AWD-M-60 `ConsentModal.test.tsx` fix.** Commit `9573817` (`fix(a11y): AWD-L-13 add button:focus-visible rule for keyboard focus rings`) touched `ConsentModal.test.tsx` and reverted the M-60 changes: restored `waitFor`+`userEvent.click` pattern instead of the `act`+`fireEvent.click` fix, and dropped the detailed root-cause comments. The correct (M-60) version is preserved in the working tree. **Fix**: commit the working-tree version — `git add apps/frontend/src/components/ConsentModal.test.tsx && git commit -m "test(modal): AWD-M-61 re-apply M-60 act() fix reverted by L-13 commit 9573817"`. Confirm zero act() warnings in `npm run test:run` output after. Filed: 2026-04-29 Lead Dev Agent (spotted during M-07 pre-flight). | `apps/frontend/src/components/ConsentModal.test.tsx` | S |~~ ✅ 2026-04-29 (commit `02d5c66` / merge `f916e4a`)
| M-46 | DX / Infrastructure | `venv/bin/python` is a broken symlink — points to `python3.13` which is not present in the QA sandbox (Ubuntu 22 / Python 3.10). `venv/bin/python3` has the same broken symlink. Backend pytest cannot run in the QA sandbox until this is recreated with the correct interpreter. This means security tests (e.g. test_security.py for AWD-C-08 CSP changes) cannot be automatically validated post-merge. **Fix**: delete and recreate the venv with the system Python: `cd <project root> && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r apps/backend/requirements.txt`. Run `cd apps/backend && python -m pytest tests/ -v` after to confirm. Must be done on the dev machine (Tolu's Mac), not the QA sandbox. Filed: 2026-04-26 QA Agent. | `venv/` (infra only — no app code change) | S |
~~| M-48 | Auth / Role Logic | `user_service.delete_user()` checks `current_user.role != UserRole.ADMIN` (line 207) but the router guard `require_admin` allows both `ADMIN` and `SUPER_ADMIN` through (see `dependencies.py` line 206). A `SUPER_ADMIN` passes the router-level check then receives a 403 inside the service — they cannot delete users despite being the highest role. Inconsistency also exists at a lower severity in `update_user` (line 155) and `get_user_profile`/`update_user_profile` (lines 254, 292) which all exclude `SUPER_ADMIN` from their role checks. **Fix**: change `!= UserRole.ADMIN` to `not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)` in the four affected service methods. Add a `test_super_admin_can_delete_user` test alongside the fix. Filed: 2026-04-26 QA Agent (spot-check of AWD-H-42 commit). | `apps/backend/services/user_service.py` (lines 155, 207, 254, 292) | S |~~ ✅ 2026-04-26
~~| M-47 | API Docs / Contract | `GET /api/users/me/data-export` (AWD-GRC-02, commit `d860d48`) was never added to `apps/backend/app/openapi.json`. The endpoint is live and tested but absent from the checked-in spec, violating the CLAUDE.md rule ("If the change touches API endpoints, regenerate `apps/backend/app/openapi.json`"). The contract-test CI job only validates JSON validity (not completeness), so CI is currently green — but the spec is stale for any API consumer or frontend contract check. **Fix**: regenerate the spec by starting the FastAPI app locally and running `python -c "import json; from apps.backend.main import app; print(json.dumps(app.openapi()))" > apps/backend/app/openapi.json`, then commit: `docs(api): AWD-M-47 regenerate openapi.json to include data-export endpoint`. Confirm `/api/users/me/data-export` appears in the output. Filed: 2026-04-26 QA Agent (spot-check of d860d48). | `apps/backend/app/openapi.json` | S |~~ ✅ 2026-04-26
~~| M-49 | API Docs / Contract | `DELETE /api/users/me` (AWD-GRC-03, commit `63989b5`) is absent from `apps/backend/app/openapi.json`. The endpoint is live and tested but the spec was not regenerated after adding the route, violating CLAUDE.md ("If the change touches API endpoints, regenerate `apps/backend/app/openapi.json`"). The contract-test CI job only validates JSON validity (not completeness), so CI may appear green — but the spec is stale and any API consumer or frontend contract check will be missing this endpoint. **Fix**: start the FastAPI app locally and run `python -c "import json; from apps.backend.main import app; print(json.dumps(app.openapi()))" > apps/backend/app/openapi.json`, then commit: `docs(api): AWD-M-49 regenerate openapi.json to include account-deletion endpoint`. Confirm `/api/users/me` with `delete` method appears in the output. Filed: 2026-04-26 QA Agent (spot-check of AWD-GRC-03 merge). | `apps/backend/app/openapi.json` | S |~~ ✅ 2026-04-27
~~| M-50 | Code Hygiene / Logging | `apps/backend/main.py` contains 8 bare `print()` calls in startup paths: `run_database_fix()` (lines 104, 111, 113, 116, 117), the `startup` lifespan handler (lines 134, 136), and Prometheus setup (line 180). These bypass the structured logger in production, and two include exception text (`f"❌ Database fix failed: {e}"`, `f"⚠️ Failed to create Redis pool: {e}"`) that could leak internal details to infrastructure logs. **Fix**: add `logger = logging.getLogger(__name__)` (or reuse `_sentry_logger`) at the top of `main.py` and replace all 8 `print(...)` calls with appropriate `logger.info(...)` / `logger.warning(...)` / `logger.error(..., exc_info=True)` calls. Filed: 2026-04-27 Security Agent. | `apps/backend/main.py` (lines 104, 111, 113, 116, 117, 134, 136, 180) | S |~~ ✅ 2026-04-27
~~| M-51 | Code Hygiene / Privacy | `console.log` calls remain in 3 frontend production paths, including one that logs user email (PII). **(A)** `apps/frontend/src/components/Footer.tsx:10` — `console.log('Subscribing email:', email)` logs user-entered email to browser console on every subscription attempt. **(B)** `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx:146` — `console.log('Generation session started:', data)` logs WebSocket session payload. **(C)** `apps/frontend/src/services/websocket.ts:51,67,86,91,116` — 5 connection-lifecycle debug logs. **Fix**: remove all `console.log` statements; for `websocket.ts`, guard with `if (import.meta.env.DEV)` if lifecycle logging is wanted during development. Filed: 2026-04-27 Security Agent. | `apps/frontend/src/components/Footer.tsx`, `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx`, `apps/frontend/src/services/websocket.ts` | S |~~ ✅ 2026-04-27
~~| M-59 | Testing / A11y | `ConsentModal.test.tsx` — two focus-trap tests emit `Warning: An update to ConsentModal inside a test was not wrapped in act(...)` (tests: `"I Agree" button becomes enabled after ticking the checkbox` and `calls onConsented when "I Agree" is clicked with checkbox ticked`). Root cause: `useFocusTrap` calls `.focus()` inside a `useEffect` immediately on mount, triggering a state flush that `userEvent.click` does not enclose in an act boundary. Tests pass — this is a test quality/flakiness risk, not a correctness issue. **Fix**: in the two affected tests, replace the bare assertion after click with `await waitFor(() => expect(btn).not.toBeDisabled())` to force React to drain async effects before asserting; mirror the fix pattern from AWD-M-25 (`ParentOnboardingPage.test.tsx`). Filed: 2026-04-28 QA Agent. | `apps/frontend/src/components/ConsentModal.test.tsx` | S |~~ ✅ 2026-04-28
~~| M-60 | Testing / Regression | **Regression: AWD-M-59 fix incomplete — act() warnings still emitted in ConsentModal tests.** Root cause: `userEvent.click` on a controlled `<input type="checkbox">` triggers React 18's internal controlled-input synchronisation in a micro-task that escapes the `userEvent` act() boundary. Neither `await act(async()=>{})` before the click nor `userEvent.setup()` prevents this — it is a React 18 + jsdom interaction with controlled inputs. Fix: replaced `await userEvent.click(checkbox)` with `await act(async () => { fireEvent.click(checkbox) })` in both affected tests — `fireEvent` fires the change event synchronously without simulating focus, preventing the micro-task scheduling issue. All 124 frontend tests pass with zero act() warnings. Commit: `e02962a` (merge `0f7c8f6`). Filed: 2026-04-28 QA Agent. | `apps/frontend/src/components/ConsentModal.test.tsx` | S |~~ ✅ 2026-04-28
~~| M-58 | Security / AI (LLM02) | Parent-guide AI output bypasses the content-safety pass that lesson-resource output runs through. `packages/ai/gpt_service.py:_validate_parent_guide` (line 612) only validates JSON shape and required top-level keys (`topic_header`, `simple_explanation`, `home_activity`, `conversation_starters`, `common_mistakes`). It does **not** invoke `_check_content_safety()` (line 273) — so `_OUTPUT_PII_PATTERNS` (email/phone/API-key regex), `_OUTPUT_INJECTION_PATTERNS` (`ignore previous instructions`, `system prompt`, `jailbreak`, …), and `_HARMFUL_CONTENT_PATTERNS` are never applied to parent-guide output. Lesson-resource output runs all three checks via `validate_output()` (line 304-316). Persisted parent guides are exported as PDF via `GET /api/parents/guides/{guide_id}/export` (`apps/backend/routers/children.py:212`) — any unscrubbed model emission will be saved and downloaded by parents. Inputs to the parent prompt are curriculum-derived (no raw free-text user input), so input-side injection risk is low; the gap is purely on the output-handling side. **Fix**: in `_validate_parent_guide`, run `is_safe, safety_reason = self._check_content_safety(content)` before the JSON parse and return `(False, safety_reason)` if the safety pass fails. Mirror the lesson-resource ordering. Add a regression test in `apps/backend/tests/` that fires a parent-guide generation with mocked AI output containing an email pattern and asserts the validator rejects it. Filed: 2026-04-28 Security Agent (OWASP LLM02 daily scan). | `packages/ai/gpt_service.py` (`_validate_parent_guide` ~ line 612), `apps/backend/tests/` (new test) | S |~~ ✅ 2026-04-28 (commit `68d1f73` / merge `b44171a` — `_validate_parent_guide` now runs `_check_content_safety` before JSON parse; 5 new regression tests in `TestParentGuideContentSafety` cover clean / email-PII / injection / harmful / safety-precedence)

---

## 🔐 Dependency Security — 2026-04-29 (dependency-security-agent)

**AWD-M-62 — DepSec: bcrypt@4.0.0 → 4.3.0 (CVE-2024-52400 — DoS via large password)**
**Problem**: `bcrypt==4.0.0` in `apps/backend/requirements.txt` is vulnerable to CVE-2024-52400 (CVSS: moderate). An attacker who can reach any auth endpoint can submit an extremely large password to cause CPU exhaustion. bcrypt is used in the auth path — `apps/backend/services/auth_service.py`.
**Acceptance criteria**:
- [ ] `bcrypt==4.3.0` (or latest stable 4.x) set in `apps/backend/requirements.txt`
- [ ] Backend tests pass: `cd apps/backend && python -m pytest tests/ -v`
- [ ] Commit: `fix(deps): AWD-M-62 upgrade bcrypt 4.0.0→4.3.0 (CVE-2024-52400)`
**Patch command**: `pip install bcrypt==4.3.0 --break-system-packages`
**Files**: `apps/backend/requirements.txt`
**Effort**: S (minutes)
**Audience**: all (auth surface)
**Stage**: ready
**Filed**: 2026-04-29 dependency-security-agent (CVE-2024-52400, CVSS moderate, auth-path dep)

---

**AWD-M-63 — DepSec: weasyprint@60.0 → 62.x (2 major versions behind, SSRF/parsing risk)**
**Problem**: `weasyprint==60.0` is 2 major versions behind the current 62.x release. WeasyPrint handles HTML→PDF rendering for the guide export and lesson-plan export features, parsing untrusted HTML content. The 60→62 jump includes patches for HTML/SVG parsing edge cases and SSRF-adjacent risk from external resource loading (CVE-2023-27043 class). Older versions also pull in older `cairocffi` and `tinycss2` with unfixed bugs.
**Acceptance criteria**:
- [ ] `weasyprint==62.0` (or latest stable) set in `apps/backend/requirements.txt`
- [ ] Review WeasyPrint 61 and 62 changelogs for breaking changes in `HTML()` / `render_to_pdf()` usage in `apps/backend/services/pdf_service.py`
- [ ] PDF export smoke test: generate a parent guide PDF and confirm valid output
- [ ] Backend tests pass: `cd apps/backend && python -m pytest tests/ -v`
- [ ] Commit: `fix(deps): AWD-M-63 upgrade weasyprint 60.0→62.x (SSRF/parsing fixes)`
**Patch command**: `pip install weasyprint==62.0 --break-system-packages` (verify API compat first)
**Files**: `apps/backend/requirements.txt`, `apps/backend/services/pdf_service.py` (review only)
**Effort**: S–M (depends on API compat)
**Audience**: parent (guide PDF), educator (lesson plan PDF)
**Stage**: ready
**Filed**: 2026-04-29 dependency-security-agent (2 major versions behind, HTML/PDF rendering surface)

---

**AWD-M-64 — DepSec: fastapi@0.109.2 + uvicorn@0.27.1 — minor security patches missed**
**Problem**: `fastapi==0.109.2` is 6 minor versions behind 0.115.x (current stable). FastAPI 0.109.1 patched CVE-2024-24762 (DoS via multipart form parsing). `uvicorn==0.27.1` is 7 minor versions behind 0.34.x. Both are core request-handling dependencies; missed minor releases include security hardening for HTTP/1.1 pipelining and multipart boundary handling. Pydantic v2 (already at 2.6.4) is required by FastAPI 0.115 ✅.
**Acceptance criteria**:
- [ ] `fastapi==0.115.12` (latest stable 0.115.x) set in `apps/backend/requirements.txt`
- [ ] `uvicorn[standard]==0.34.0` (latest stable) set in `apps/backend/requirements.txt`
- [ ] Backend tests pass: `cd apps/backend && python -m pytest tests/ -v`
- [ ] Commit: `fix(deps): AWD-M-64 upgrade fastapi 0.109.2→0.115.x, uvicorn 0.27.1→0.34.x`
**Patch command**: `pip install fastapi==0.115.12 "uvicorn[standard]==0.34.0" --break-system-packages`
**Files**: `apps/backend/requirements.txt`
**Effort**: S (minutes)
**Audience**: all (request handling surface)
**Stage**: ready
**Filed**: 2026-04-29 dependency-security-agent (CVE-2024-24762 in fastapi<0.109.1, 6 minor versions behind)

---

## 🟣 Compliance (GRC)

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| GRC-01 | COPPA | Parental consent flow before first ChildProfile creation (plain-language disclosure + explicit opt-in, dated record) | `apps/backend/routers/children.py`, `apps/frontend/src/pages/ParentDashboardPage.tsx`, new consent table | M |~~ ✅ 2026-04-27
~~| GRC-02 | GDPR | Data export endpoint — allow a parent to download all their data + their children's data as JSON | `apps/backend/routers/users.py` (new endpoint), `apps/backend/services/user_service.py` | M |~~ ✅ 2026-04-26
~~| GRC-03 | GDPR | Account deletion endpoint with cascade for ChildProfile + ParentGuide | `apps/backend/routers/users.py`, migrations (cascade rules) | M |~~ ✅ 2026-04-27
~~| GRC-04 | NDPR/POPIA | Data-residency note in privacy policy — document where Awade stores African parent/child data | `docs/public/external/`, privacy policy file | S |~~ ✅ 2026-04-26
~~| GRC-05 | COPPA | Audit logs for any admin access to a ChildProfile | `apps/backend/models.py` (AdminAuditLog — verify coverage), `apps/backend/routers/admin.py` | S |~~ ✅ 2026-04-26
| GRC-06 | GDPR Art. 13/14 · NDPR · POPIA | **Vercel Analytics not disclosed as analytics sub-processor.** `@vercel/analytics` is loaded unconditionally in `apps/frontend/src/main.tsx` and collects page URL, referrer, device type, and IP-derived country — but privacy policy §4c lists Vercel as "None (static assets only; no PII in CDN layer)" (incorrect), and §9 implies no analytics data is collected. Required fixes: (1) update privacy policy §2d to name Vercel Analytics and list collected fields; (2) update §3 to add analytics purpose + legitimate interest basis; (3) update §4c Vercel row to accurately describe analytics data collection; (4) update §9 to note cookieless analytics and DNT signal support. No consent banner required (no cookies used), but the transparency gap violates GDPR Art. 13/14, NDPR Art. 2.5, and POPIA §18. Filed: 2026-04-29 compliance-agent. | `docs/public/external/privacy-policy.md` | S |
| GRC-07 | EU AI Act Art. 52 · GDPR Art. 5(1)(a) | **AI-generated content disclosure absent from parent guide flow; `/disclaimer` page missing.** `GuideViewPage.tsx` shows only an italic footer `'_Guide generated by Awade — awade.app_'` — insufficient as an EU AI Act Art. 52 disclosure. `ParentDashboardPage.tsx` has no pre-generation notice. The educator flow (`EditLessonResourcePage.tsx`) has an adequate inline notice and links to `/disclaimer`, but no DisclaimerPage component or route exists in the codebase. Required fixes: (1) add prominent AI-disclosure banner in `GuideViewPage.tsx` (e.g. "This guide was created by Awade's AI. It may contain inaccuracies — use your own judgement."); (2) add brief pre-generation notice in the guide generation trigger; (3) create `DisclaimerPage.tsx` and register `/disclaimer` in `App.tsx`; (4) link both educator and parent flows to the disclaimer page. **Must be implemented before June 2026 parent pivot launch** (EU AI Act Art. 52 enforcement window). Filed: 2026-04-29 compliance-agent. | `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/frontend/src/pages/ParentDashboardPage.tsx`, new `apps/frontend/src/pages/DisclaimerPage.tsx`, `apps/frontend/src/App.tsx` | M |

---

## A11Y — AWD-L-03 audit findings (2026-04-27)

> Source: [`docs/agentic/audits/a11y-parent-flow-2026-04-27.md`](audits/a11y-parent-flow-2026-04-27.md). Each row links to the audit's finding ID for full context.

### 🟠 High

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| H-52 | A11y / Contrast | A11Y-PF-01 — Primary CTA `bg-accent-600 text-white` contrast is **3.66:1**, fails WCAG 1.4.3 (AA needs 4.5:1 for normal text). Affects every parent-flow CTA: "Add Child" / "Add Your First Child" / "Get Started" / "I Agree — Add a Child" / "Save Changes". Fix: shift default ↔ hover so default uses `accent-700` (5.07:1) and hover uses `accent-800`, OR darken `accent-600` itself in `tailwind.config.js`. Filed: 2026-04-27 audit. | `apps/frontend/tailwind.config.js`, `apps/frontend/src/pages/ParentDashboardPage.tsx` (160-166, 189-196), `ChildrenPage.tsx` (92-98, 139-146), `ParentOnboardingPage.tsx` (286-302), `apps/frontend/src/components/ConsentModal.tsx` (122-130), `AddChildModal.tsx` (255-264) | S |~~ ✅ 2026-04-27 (commit `cf64691` — shifted bg-accent-600/hover-accent-700 → bg-accent-700/hover-accent-800 across the 5 parent-flow components; tailwind palette untouched to avoid changing educator pages)
~~| H-53 | A11y / Non-text Contrast | A11Y-PF-02 — `text-gray-400` icon-only buttons are **2.53:1** on white, fail WCAG 1.4.11 (3:1 for graphical UI components). Edit/Trash on dashboard child cards and Download/WhatsApp/Bookmark in guide top bar. Fix: bump default to `text-gray-500` (4.86:1) or `text-gray-600`. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentDashboardPage.tsx` (251-265), `GuideViewPage.tsx` (179-210) | S |~~ ✅ 2026-04-27
~~| H-54 | A11y / Modals | A11Y-PF-03 — `AddChildModal` lacks `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` — screen-reader users get no signal that a modal opened. Mirror the pattern from `ConsentModal.tsx` (lines 35-40, 47-53). Filed: 2026-04-27 audit. | `apps/frontend/src/components/AddChildModal.tsx` (122-127) | S |~~ ✅ 2026-04-28 (commit `e0ed6ea` / merge `5aaca85` — added `role="dialog"` + `aria-modal="true"` + `aria-labelledby="add-child-modal-title"` on the backdrop and `id="add-child-modal-title"` on the heading; new `AddChildModal.test.tsx` with 4 a11y assertions)
~~| H-55 | A11y / Keyboard | A11Y-PF-04 — Topic action buttons reveal `"Get 'How to Help' guide →"` only on hover (`opacity-0 group-hover:opacity-100`); keyboard-only users never see it. Also no `aria-label` on the button — accessible name is just topic title with no action verb. Fix: add `group-focus-within:opacity-100` and `aria-label={\`Generate "How to Help" guide for ${topic.topic_title}\`}`. Same pattern in SavedGuides cards. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentDashboardPage.tsx` (319-332), `SavedGuidesPage.tsx` (158-176) | S |~~ ✅ 2026-04-28

### 🟡 Medium

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| M-53 | A11y / Forms | A11Y-PF-05 — Required-field indication is `<span class="text-red-500">*</span>` only — colour-blind users miss the cue, screen readers announce "asterisk". Add `required aria-required="true"` to the input and a visually-hidden `(required)` to the label. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (167-169), `apps/frontend/src/components/AddChildModal.tsx` (145) | S |~~ ✅ 2026-04-28
~~| M-54 | A11y / Status Messages | A11Y-PF-06 — Form-level error banners and loading text are not announced to assistive tech. No `role="alert"` / `aria-live="polite"` on the `bg-red-50` containers; no `role="status"` on "Generating your guide…". `ConsentModal.tsx:116` already uses `role="alert"` — propagate the pattern. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (161-163), `apps/frontend/src/components/AddChildModal.tsx` (139-141), `ChildrenPage.tsx` (104-108), `GuideViewPage.tsx` (104-107) | S |~~ ✅ 2026-04-28
~~| M-55 | A11y / Forms | A11Y-PF-07 — Form inputs do not surface `aria-invalid` or `aria-describedby` after server validation. When `setError("Please enter your child's name")` fires, the offending input is not flagged programmatically. Track an `invalidFields` set in component state and bind `aria-invalid={invalidFields.has(...)}` + `aria-describedby` linking to the error message. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (170-191), `apps/frontend/src/components/AddChildModal.tsx` (146-167) | S |~~ ✅ 2026-04-28
~~| M-56 | A11y / Modals | A11Y-PF-08 — Neither `AddChildModal` nor `ConsentModal` traps focus, sets initial focus on the dialog, or closes on Escape. Risk: keyboard users can Tab back into the page behind the modal. Recommend adopting `@headlessui/react`'s `Dialog` (handles trap + Escape + `aria-modal` for free) or building a `useFocusTrap` hook. Filed: 2026-04-27 audit. | `apps/frontend/src/components/AddChildModal.tsx`, `ConsentModal.tsx` | M |~~ ✅ 2026-04-28 (commit `f30487a` / merge `2efa824` — new `useFocusTrap` hook in `src/hooks/useFocusTrap.ts`; both modals trap Tab/Shift+Tab and close on Escape; 12 new vitest cases in AddChildModal.test.tsx + ConsentModal.test.tsx)
~~| M-57 | A11y / Navigation | A11Y-PF-09 — No "Skip to main content" link on any parent-flow page. Keyboard users must Tab through the full Sidebar nav on every page load. Add `<a href="#main-content" className="sr-only focus:not-sr-only ...">` at the top of the layout chrome and `id="main-content" tabIndex={-1}` on each `<main>`. Filed: 2026-04-27 audit. | `apps/frontend/src/components/Sidebar.tsx`, all five parent-flow pages | S |~~ ✅ 2026-04-28 (commit `9dcde3f` / merge `500577c` — skip link added to Sidebar before `<aside>`; `id="main-content" tabIndex={-1} outline-none` added to `<main>` in ParentDashboardPage, ChildrenPage, GuideViewPage, SavedGuidesPage; 3 vitest cases in Sidebar.test.tsx)

### 🟢 Low / Polish

| # | Area | Issue | File(s) | Effort |
|---|------|-------|---------|--------|
~~| L-13 | A11y / Focus | A11Y-PF-10 — Parent-flow buttons use raw Tailwind utilities and never set `focus:` styles (`grep -c "focus:" apps/frontend/src/pages/{Parent,Children,Guide,SavedGuides}*.tsx` → 0 each). Browser default focus rings satisfy AA in most browsers but are weak on coloured CTAs. Either migrate CTAs to the `.btn-primary` / `.btn-accent` classes already defined in `apps/frontend/src/index.css` (lines 77-89) or add a project-level `button:focus-visible { @apply outline-none ring-2 ring-primary-500 ring-offset-2; }` rule. Filed: 2026-04-27 audit. | `apps/frontend/src/index.css`, parent-flow pages | S |~~ ✅ 2026-04-28
~~| L-14 | A11y / Landmarks | A11Y-PF-11 — `<nav>` elements in `Sidebar` and `MobileNavigation` lack `aria-label`. In a screen-reader landmarks list both render as "navigation" with no way to distinguish them. Also missing `aria-current="page"` on the active link. Fix: `<nav aria-label="Primary">` / `<nav aria-label="Mobile primary">`, plus `aria-current="page"` per link. Filed: 2026-04-27 audit. | `apps/frontend/src/components/Sidebar.tsx`, `MobileNavigation.tsx` | S |~~ ✅ 2026-04-28
~~| L-15 | A11y / Touch Targets | A11Y-PF-12 — Edit/Trash buttons in `ParentDashboardPage` (lines 251-265) have no `p-*` padding around 12px icons — effective hit target ~12×12 px, well below the 24×24 minimum (and 44×44 AAA recommendation). `ChildrenPage.tsx:172-188` has the correct `p-2 rounded-lg` pattern; copy it. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentDashboardPage.tsx` (251-265) | S |~~ ✅ 2026-04-28
~~| L-16 | A11y / Forms | A11Y-PF-13 — Form labels are siblings of their inputs, not wrapped or associated via `htmlFor` / `id`. Browser heuristics usually pair them but the association is not guaranteed. Add `id="..."` to each input/select and `htmlFor="..."` to each label. Filed: 2026-04-27 audit. | `apps/frontend/src/pages/ParentOnboardingPage.tsx` (165-254), `apps/frontend/src/components/AddChildModal.tsx` (144-227) | S |~~ ✅ 2026-04-28

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

~~| H-51 | Code Hygiene / Privacy / Regression | Commit `ad60f1c` (AWD-M-50) accidentally reverted AWD-M-51's console.log fixes. The COMMITTED state of `develop` now has: **(A)** `apps/frontend/src/components/Footer.tsx` line 10 — `console.log('Subscribing email:', email)` logs user email to browser console on every newsletter subscription attempt (**PII leak**); **(B)** `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx` line ~145 — `console.log('Generation session started:', data)` logs WebSocket session payload; **(C)** `apps/frontend/src/services/websocket.ts` lines 51,62,67,73,78,86,91,116 — 8 bare `console.log/error/warn` calls without `import.meta.env.DEV` guard. **The correct fix already exists as uncommitted working-tree changes.** Fix: `git add apps/frontend/src/components/Footer.tsx apps/frontend/src/components/AIGenerationLoadingRealtime.tsx apps/frontend/src/services/websocket.ts && git commit -m "fix(frontend): AWD-H-51 re-apply M-51 DEV guards reverted by ad60f1c"`. Verify with `git diff HEAD~1 HEAD -- apps/frontend/src/components/Footer.tsx` that console.log('Subscribing email:') is absent. Filed: 2026-04-27 QA Agent. | `apps/frontend/src/components/Footer.tsx`, `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx`, `apps/frontend/src/services/websocket.ts` | S — fix is already in working tree, just needs commit |~~ ✅ 2026-04-27

~~| M-52 | Config / Security | `apps/frontend/src/services/websocket.ts` line 43–45 hardcodes the production WebSocket URL as the literal placeholder `'wss://your-production-domain.com/ws'`. In production builds (`import.meta.env.MODE === 'production'`), the service will silently attempt to connect to this non-existent host, causing all real-time AI generation progress updates to fail silently for every production user. **Fix**: (1) Add `VITE_WS_URL=wss://<your-actual-domain>/ws` to `.env.example` and `env.production.template`; (2) Replace the hardcoded string with `import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws'` in `websocket.ts`; (3) Document the variable in `.env.example`. This is pre-existing (not introduced by AWD-M-50) but newly filed after spot-check. Filed: 2026-04-27 QA Agent. | `apps/frontend/src/services/websocket.ts` (lines 43–45), `.env.example`, `env.production.template` | M |~~ ✅ 2026-04-27

~~| H-61 | Security / Role Logic | **SUPER_ADMIN excluded from admin bypass in AWD-M-67 scoped queries.** Both `lesson_plan_service.py:542` and `lesson_plans.py:189` gate the unscoped (admin) DB query with `if current_user.role == UserRole.ADMIN:`. The project defines `SUPER_ADMIN` as the highest role and `dependencies.py:206` defines `require_admin = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])`. A SUPER_ADMIN who did not create a resource will receive 404 instead of access — silently demoted to regular-user behaviour. Same class as AWD-M-48 (fixed 2026-04-26 in `user_service.py`). **Fix**: change `if current_user.role == UserRole.ADMIN:` → `if current_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):` in both locations. Add `test_super_admin_can_access_any_resource` (service) and `test_super_admin_can_export_any_resource` (router) mirroring the existing admin fixture tests. Filed: 2026-04-30 code-review-agent. | `apps/backend/services/lesson_plan_service.py` (line 542), `apps/backend/routers/lesson_plans.py` (line 189), `apps/backend/tests/test_lesson_plan_service.py`, `apps/backend/tests/test_lesson_plans_router.py` | S | Stage: ready |~~ ✅ 2026-05-01

| H-57 | Security / Architecture | **Vercel serverless proxy (`apps/frontend/api/[...path].js`) sets `Access-Control-Allow-Origin: *`**. This catch-all proxy forwards all requests to `awade-backend-test.onrender.com` and applies a CORS wildcard. If active in production deployment, it bypasses FastAPI CORS middleware. Fix: (a) Confirm whether this proxy is included in the Vercel production build (check `vercel.json` routing). (b) If dev-only: add a comment and exclude via vercel.json. (c) If production-active: restrict CORS to the frontend domain only. Filed: 2026-04-29 architecture-agent. | `apps/frontend/api/[...path].js`, `apps/frontend/vercel.json` | S | Stage: define |
~~| M-65 | Code Hygiene | **`TestPage.tsx` present in frontend src** — a debug/test page at `apps/frontend/src/pages/TestPage.tsx` is included in the production build. Verify it has an auth guard or is excluded from production routing in `App.tsx`. If neither: remove it. Filed: 2026-04-29 architecture-agent. | `apps/frontend/src/pages/TestPage.tsx`, `apps/frontend/src/App.tsx` | S | Stage: ready |~~ ✅ 2026-04-30
| M-66 | Code / Design | **Consolidate 5 `AIGenerationLoading*` component variants** into one canonical component. Current files: `AIGenerationLoading.tsx`, `AIGenerationLoadingActual.tsx`, `AIGenerationLoadingReal.tsx`, `AIGenerationLoadingRealtime.tsx`, `AIGenerationLoadingSimple.tsx`. Identify which variant is used in production; remove the others. Filed: 2026-04-29 architecture-agent. | `apps/frontend/src/components/AIGenerationLoading*.tsx` | S | Stage: ready |
| M-70 | Code / Design | **`export_lesson_resource` router endpoint duplicates scoped access-control query instead of delegating to service.** `lesson_plans.py` lines 187–197 re-implement the `if ADMIN / else user_id` ownership-scoped query that already exists in `LessonPlanService.get_lesson_resource()` (lines 539–551). Every other endpoint in this router delegates to the service. This duplication is what caused AWD-H-61 (the router was patched independently, missing the SUPER_ADMIN case the service handled). **Fix**: refactor `export_lesson_resource` to call `LessonPlanService(db).get_lesson_resource(resource_id, current_user)` for the access check, then re-query the ORM object for export — or extend the service method to return the raw ORM object. Centralising the logic means future access-control changes touch one place. Filed: 2026-04-30 code-review-agent. | `apps/backend/routers/lesson_plans.py` (lines 173–236), `apps/backend/services/lesson_plan_service.py` | S | Stage: define |

| M-67 | Architecture | **Dual caching layer — determine authoritative cache**. `apps/backend/services/data_structures.py` (728 lines) implements in-process LRU/LFU caches. `packages/ai/cache.py` implements a Redis-backed `ContentCache` for AI generation results. Their responsibilities may overlap. Decision needed: is in-process caching intentional (for DB query results) while Redis is for AI content? If so, document the split. If there is redundancy, remove the in-process cache in favour of Redis. Filed: 2026-04-29 architecture-agent. | `apps/backend/services/data_structures.py`, `packages/ai/cache.py` | M | Stage: define |

---
<!-- access-review-agent 2026-04-29 -->

### AWD-H-57 — Rotate AI API keys (Gemini, OpenAI, Google)
- **Stage:** define
- **Priority:** High
- **Source:** access-review-agent 2026-04-29
- **Detail:** GEMINI_API_KEY, OPENAI_API_KEY, and GOOGLE_API_KEY have no recorded rotation date. Recommend treating as overdue. Rotate in provider dashboards, update Render env vars, log date in `.env.example`.
- **Files:** `.env.example`, Render environment settings

### AWD-M-65 — Create agent-permissions.json manifest
- **Stage:** ready
- **Priority:** Medium
- **Source:** access-review-agent 2026-04-29
- **Detail:** `agent-permissions.json` does not exist. Create at repo root enumerating each scheduled agent's read/write paths. 11 agents confirmed active via `.agent-health/`. Enables systematic scope-creep auditing in future runs.
- **Files:** `agent-permissions.json` (create)

~~### AWD-M-66 — Clean up duplicate/stale JWT secret variables in .env.example~~
- ~~**Stage:** ready~~ ✅ 2026-04-30
- **Source:** access-review-agent 2026-04-29
- **Detail:** Removed duplicate `JWT_SECRET_KEY`/`JWT_ALGORITHM`/`JWT_EXPIRATION_HOURS` block, stray `->` merge artifact, and stale `SECRET_KEY`/`JWT_SECRET` entries. Commit: `779881a`.

~~### AWD-M-67 — Lesson resource routes: uniform 404 for unauthorized IDs (existence leakage)~~ ✅ 2026-04-30
- ~~**Stage:** ready~~ ✅ fixed in commit 21367ab — scoped DB query to user_id for non-admins in both `get_lesson_resource` (service) and `export_lesson_resource` (router); tests updated

~~### AWD-H-59 — Wrong variable name for JWT expiry in .env.example~~ ✅ 2026-04-30
- ~~**Stage:** ready~~ ✅ fixed in commit f054da5

### AWD-M-68 — env.production.template still contains stale SECRET_KEY variable
- **Stage:** define
- **Priority:** Medium
- **Source:** code-review-agent 2026-04-30
- **Detail:** `SECRET_KEY` was removed from `.env.example` (AWD-M-66) because the backend uses `JWT_SECRET_KEY`. However `env.production.template` still has `SECRET_KEY=your-super-secret-key-change-this`. Templates are out of sync. Also audit `env.test.template` for the same stale entry. Fix: remove `SECRET_KEY` from all env templates that don't need it and verify no backend path reads it.
- **Files:** `env.production.template`, `env.test.template`

~~### AWD-H-60 — .env.example working tree diverges from HEAD after H-59 fix — risk of silent reversion~~ ✅ 2026-04-30
- ~~**Stage:** ready~~ ✅ resolved by Lead Dev Agent this run — `.env.example` restored to HEAD content (`JWT_EXPIRES_MINUTES=60`) via Python write; staged reversion also cleared from index

### AWD-M-69 — JWT token lifetime default reduced 24× without explicit callout — verify Render env var
- **Stage:** define
- **Priority:** Medium
- **Source:** code-review-agent 2026-04-30
- **Detail:** The H-59 fix changed the example value from `JWT_EXPIRATION_HOURS=24` (≈1440 min) to `JWT_EXPIRES_MINUTES=60` (1 hour). The service-layer default (when the var is absent) is also 60 minutes. Any deployment that omitted the var or copied the old example will now issue tokens expiring 24× sooner. No changelog or dev-log entry calls this out. **Fix**: (1) Verify Render's `JWT_EXPIRES_MINUTES` env var is explicitly set to the intended lifetime. (2) Add a note to `docs/agentic/sprints/dev-log.md` documenting the lifetime change. (3) If 60 min is intentional for security, add a comment to the H-59 completed_backlog entry.
- **Files:** `.env.example`, Render env vars, `docs/agentic/sprints/dev-log.md`
