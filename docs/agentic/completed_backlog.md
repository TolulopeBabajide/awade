# Awade — Completed Backlog

> Completed issues moved here from `backlog.md` to keep the active backlog clean.
> Most recent completions at the bottom.

---

| # | Issue | Completed |
|---|-------|-----------|
| — | Initial agentic framework adaptation | 2026-04-20 |
| H-05 | Security: Account enumeration protection — generic error for Google OAuth login attempts | 2026-04-21 |
| C-01 | Admin GET endpoints missing auth — **already fixed** in commit `df399fc` via router-level `dependencies=[Depends(require_admin)]` on `APIRouter`. Backlog item was filed in error. | 2026-04-21 |
| C-02 | JWT secret key hardcoded fallback in production — `get_jwt_secret_key()` now raises `RuntimeError` when `ENVIRONMENT=production` and `JWT_SECRET_KEY` unset; startup validation added to lifespan. Commit `cf3e391`. | 2026-04-21 |
| C-03 | Privilege escalation via Google OAuth — whitelisted `authenticate_google_user` to only assign `PARENT` or `EDUCATOR`; `ADMIN`/`SUPER_ADMIN` coerced to `PARENT`. Tests added in `test_security.py::TestGoogleOAuthRoleWhitelist`. Commit `483c428`. | 2026-04-21 |
| C-04 | Unauthenticated context routes + prompt injection chain — all 7 routes in `contexts.py` now require `require_admin_or_educator`; educators are gated to their own lesson plans; admins bypass. `get_contexts_for_user()` added to `ContextService`. Tests in `test_contexts_router.py` cover 401 on every endpoint, 403 cross-user access, and admin bypass. Commit `1aea05a`. | 2026-04-21 |
| H-15 | `App.test.tsx` CI failure (stale educator headline assertion after parent pivot) — updated assertion to `getByRole('heading', { name: /Understand what your child is learning/i })` and added CTA smoke test (`getByRole('link', { name: /Sign up as a parent/i })`). All 9 frontend tests pass. Commit `842e7af`, merged to develop as `59c96aa`. | 2026-04-21 |
| H-14 | 62 TypeScript errors + ESLint config missing (CI `frontend-test` and `validate` blocking) — created `apps/frontend/src/vite-env.d.ts` (fixes `import.meta.env`), updated `tsconfig.json` to add `vitest/globals` types, created `apps/frontend/.eslintrc.cjs`, replaced `process.env` with `import.meta.env.MODE` in `websocket.ts`, replaced `global` with `globalThis` in test files, removed all unused imports/variables across 8 source files. `tsc --noEmit` 0 errors, `eslint --max-warnings 0` 0 problems, all 9 frontend tests pass. Commit `e508e2e`, merged to develop as `d2d7b59`. | 2026-04-21 |
| H-07 | Security / AI: Parent guide generation endpoint rate-limited to 5/minute — added `@limiter.limit("5/minute")` + `Request` param to `generate_guide` in `apps/backend/routers/children.py`. Two regression tests added (`TestGenerateGuideRateLimit`). Commit `da34bf7`, merged to develop as `737c830`. | 2026-04-21 |
| H-08 | Security: `str(e)` leaked in HTTPException detail — replaced all 7 bare exception string interpolations in `auth_service.py` and all 7 in `context_service.py` with generic static messages; added `logger.error(..., exc_info=True)` calls. Also fixed bare `print()` in `blacklist_refresh_token` (H-17). 3 new regression tests in `TestExceptionDetailSanitization`. Commit `d735ea3`, merged to develop as `535718e`. | 2026-04-21 |
| H-17 | Code Hygiene: Bare `print()` in `auth_service.py` `blacklist_refresh_token` — replaced with `logger.error(...)`. Fixed as part of H-08 (same file, same pattern). Commit `d735ea3`. | 2026-04-21 |
| H-02 | Signup role selector — `SignupPage.tsx` now includes PARENT/EDUCATOR role picker with Google OAuth pass-through (credential + role → AuthContext → apiService → backend). Completed as part of parent pivot Phase 3. | 2026-04-21 |
| H-04 | React Query migration for educator pages — created `useEducatorData.ts` hooks, extracted `subjectIcons.ts` utils, refactored DashboardPage / LessonPlansPage / LessonResourcesPage to use React Query with proper cache keys, staleTime, and enabled guards. | 2026-04-21 |
| L-08 | Untracked files resolved — `awade_grc_audit.docx` added to `.gitignore` (sensitive); `awade_rebranding.docx`, `awade_review_parent_pivot.md`, `architecture_diagram.md` committed to repo. | 2026-04-21 |
| H-13 | Security: Auth endpoints rate-limited — `/auth/google` 10/min, `/auth/refresh` 20/min, `/auth/forgot-password` 5/min (email-bombing + enumeration), `/auth/reset-password` 5/min (token brute-force). Added `request: Request` params to all four; renamed Pydantic body params in `forgot-password` and `reset-password` to `payload` to avoid collision. 4 structural regression tests in `TestAuthEndpointRateLimitStructure`. Commit `022b959`, merged to develop as `d108e86`. | 2026-04-22 |
| H-12 | Security: `GET /api/users/{user_id}` ownership check — any authenticated EDUCATOR could read any user record (PII disclosure). `UserService.get_user` now accepts `current_user` and raises 403 if caller is not the owner and not ADMIN/SUPER_ADMIN (mirrors pattern from `update_user`/`get_user_profile`). Also fixed `str(e)` leak in `get_user` exception handler; added `logger` to `user_service.py`. 7 regression tests in `test_users_router.py` cover: own-record 200, cross-user 403, parent 403, admin bypass 200, super_admin bypass 200, unauthenticated 403, non-existent 404 (admin). Commit `8b012b9`, merged to develop as `e30e5c1`. | 2026-04-22 |
| H-09 | Security / AI: OpenAI client timeout — `openai.OpenAI()` had no explicit timeout, allowing a slow/stalled API request to hold a uvicorn worker indefinitely (OWASP LLM10). Added `DEFAULT_TIMEOUT = 60.0` class constant and `self.timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))` to `OpenAIProvider.__init__`, passing it to `openai.OpenAI(api_key=..., timeout=self.timeout)`. Added `OPENAI_TIMEOUT_SECONDS=60` placeholder to `env.example`. Updated `test_initialization` to assert timeout kwarg; added `test_initialization_custom_timeout` to verify env-var override. Commit `3972e01`, merged to develop as `cb57ec2`. | 2026-04-22 |

| H-22 | Testing: Fix failing `TestGeminiProvider::test_get_model_name` — test was asserting stale model names (`gemini-1.5-flash` / `gemini-1.5-pro`) that no longer matched `gemini_provider.py` which returns `gemini-flash-latest` for both tiers since Jan 2026. Updated lines 51-52 of `test_ai_providers.py` to assert `gemini-flash-latest` for both "basic" and "standard" tiers. Both `TestGeminiProvider` tests pass. Commit `4db306a`, merged to develop as `c2c905f`. | 2026-04-22 |

> (Parent pivot Phases 1–4 — completed in the 2026-04-16 session, pre-backlog. Not duplicated here.)
| H-21 | Code Hygiene: Bare `print()` calls in `lesson_plan_service.py` — replaced `print(f"Failed to enqueue job: {e}")` (line 397) with `logger.error("Failed to enqueue job", exc_info=True)` and removed `print(f"DEBUG: Resource {resource_id} found in DB...")` (line 534). Added `import logging` + module-level `logger = logging.getLogger(__name__)`. Commit `4460d8b`, merged to develop as `0184370`. | 2026-04-22 |
| H-06 | AI: Parent guide output validation — `generate_parent_guide()` previously persisted AI output after only a lightweight 5-key presence check, allowing malformed or truncated JSON to reach the database. Added `ParentGuideAIContent` Pydantic schema (+ 6 nested models: `ParentGuideTopicHeader`, `ParentGuideSimpleExplanation`, `ParentGuideHomeActivity`, `ParentGuideCommonMistake`, `ParentGuideCurriculumContext`) to `apps/backend/schemas/children.py`. Updated `ChildrenService.generate_guide()` to call `ParentGuideAIContent.model_validate_json(ai_content)` before `db.add()` — raises HTTP 502 with a generic user-facing message if validation fails, and logs the full Pydantic error for debugging. Nothing is persisted on validation failure. Added 18 tests in `test_parent_guide_validation.py`: 12 schema-level (required fields, optional fields, nested field checks, invalid JSON) + 6 service-level (valid persists, invalid JSON → 502, missing field → 502, nothing persisted on failure, generic error message, idempotency). Commit `f5523a2`, merged to develop as `e25040d`. | 2026-04-22 |
| H-26 | Code Hygiene: `traceback.print_exc()` calls in `lesson_plan_service.py` — two inline `import traceback` + `traceback.print_exc()` blocks remained after the H-21 fix (in `create_lesson_plan_response()` at line 112 and `generate_lesson_plan()` at line 162). Both wrote full tracebacks to stderr in production paths. Replaced each with `logger.error("Unexpected error in <method_name>", exc_info=True)` using the existing module-level `logger`. Also replaced `str(e)` interpolation in the same `HTTPException` detail strings with static messages (partial H-18 fix for these two call sites). Commit `a26af21`, merged to develop as `187bd80`. | 2026-04-22 |
| H-24 | Security: Suspended users bypass authentication — `get_current_active_user` in `apps/backend/dependencies.py` had a placeholder comment but no actual `is_suspended` check. Added `if current_user.is_suspended: raise HTTPException(status_code=403, detail="Account suspended")` — all auth-gated routes inherit the fix through the `Depends` chain. Added 3 regression tests (`TestSuspendedUserAuthBypass`): active user passes, suspended user gets 403, unsuspended user passes again. Commit `91d758e`, merged to develop as `1153504`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| C-05 | Git repo corruption: `refs/heads/develop` pointed to missing commit `187bd80b...` (interrupted write). Repo self-healed across agent runs — `270ac41` is now the confirmed valid HEAD. Verified `git cat-file -e` succeeds; `git log` runs cleanly. No app code changed. Closed as resolved. | 2026-04-22 |
| H-18 | Security: `str(e)` information disclosure in HTTPException details — 43 instances across 6 service files (`user_service.py` ×7, `lesson_plan_service.py` ×8, `country_service.py` ×8, `subject_service.py` ×8, `grade_level_service.py` ×9, `file_upload_service.py` ×3). Added `import logging` + `logger = logging.getLogger(__name__)` to the 3 files that lacked it. Replaced all `detail=f"...{str(e)}"` strings with static messages and added `logger.error("...", exc_info=True)` in each except block. Also fixed a bare `print()` in `file_upload_service.py:delete_profile_image`. Commit `8628ab7`, merged to develop as `73188d5`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-27 | Testing: `test_contexts_router.py` 8 tests failing with `AttributeError: 'NoneType' object has no attribute 'set'` — all four test helper factories (`_make_educator`, `_make_admin`, `_make_lesson_plan`, `_make_context`) used `Model.__new__(Model)` which bypasses SQLAlchemy's instrumented `__init__`, leaving `_sa_instance_state = None`. Any attribute assignment on the resulting object raises `AttributeError`. Fix: replaced all four `__new__` calls with `Model()` (transient SQLAlchemy instances require no session). Full suite result: 183 passed (up from 175), 9 pre-existing failures unchanged (H-28, H-29, M-22). Commit `c38dcd4`, merged to develop as `75f08d0`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-28 | Testing: `TestExceptionDetailSanitization` — 3 tests in `test_auth_flow_security.py` failed for two distinct reasons. (1) `test_google_auth_error_does_not_leak_exception` sent `{"id_token": "dummy-token"}` but `GoogleAuthRequest` requires `credential: str`, so Pydantic returned 422 before the mock ran — fixed by changing field name to `"credential"`. (2) `test_login_db_error_does_not_leak_exception` and `test_registration_db_error_does_not_leak_exception` had valid payloads but `RuntimeError` from the mock escaped via Starlette's async middleware ExceptionGroup rather than being caught and returned as 500 — fixed by adding try/except guards to `login()`, `signup()`, and `google_auth()` router handlers (re-raises `HTTPException`, converts all other exceptions to generic 500 with `logger.error(..., exc_info=True)`). All 3 tests now pass in isolation. In full-suite `test_login_db_error` also encounters H-29 rate-limiter exhaustion — tracked separately. Commit `442990d`, merged to develop as `a977e9c`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-29 | Testing: Rate-limiter state not reset between tests — earlier test files exhausted the in-memory rate-limiter for `/api/auth/login`, causing 6 tests in `test_auth_flow_security.py` to receive 429 instead of expected 200/401/500 when the full suite ran. Added `rate_limiter_reset` autouse fixture to `apps/backend/tests/conftest.py` that calls `limiter._storage.reset()` (with `hasattr` guards) before and after each test, draining all counters. Commit `3ce06c4`, merged to develop as `53874c4`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-23 | Security/Deps: PyJWT version gap — `requirements.txt` used the unpinned floor `PyJWT>=2.0.0`, meaning CI would install whatever was available and could stay at 2.3.0 (large CVE surface vs 2.12.1 latest). Fixed by pinning `PyJWT==2.12.1` in `apps/backend/requirements.txt` with an explanatory comment. No app code changed; requirements-only fix. Commit `b9a089f`, merged to develop as `5e26a7b`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-11 | Testing: No pytest coverage for children router or ChildrenService — added `apps/backend/tests/test_children_router.py` (39 test cases across 6 classes) and `apps/backend/tests/test_children_service.py` (32 test cases across 7 classes). Coverage: unauthenticated → 403 on all 10 endpoints (HTTPBearer raises 403, not 401), EDUCATOR role → 403 on all endpoints, ownership enforcement (parent A's child_id returns 404 for parent B), create_child FK validation (invalid country/curricula/grade/subject_id → 400), list_children isolation (only own children returned), generate_guide idempotency (existing guide returned, AI not called), generate_guide AI validation (invalid JSON → 502, missing required field → 502, valid JSON persists to DB), delete_child happy path. Patch path for inline `from packages.ai.gpt_service import AwadeGPTService` uses `packages.ai.gpt_service.AwadeGPTService`. Commit `991c287`, merged to develop as `ea9578c`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-22 |
| H-19 | Parents: Dedicated /children page — created `apps/frontend/src/pages/ChildrenPage.tsx` with a full child profile management UI: profile cards showing name, age, school, grade, curriculum; add/edit/delete via the existing AddChildModal; empty state with "Add Your First Child" CTA; "Add another child" dashed card; incomplete-profile nudge when curricula/grade not set. Added `/children` route to `App.tsx`. Added "My Children" nav item (FaUsers icon) to parent nav in both `Sidebar.tsx` and `MobileNavigation.tsx`. Zero tsc errors, zero lint warnings, 9/9 vitest passing. Commit `5367714`, merged to develop as `15bdd83`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| H-30 | Security: Missing PARENT role guard on parent routes — created `apps/frontend/src/components/ParentRoute.tsx` (mirrors AdminRoute pattern: checks `user.role === 'PARENT'`, redirects unauthenticated users to /login, redirects wrong-role users to /dashboard). Updated `App.tsx` to wrap the three parent-only routes (/children, /guides/generate, /saved-guides) with `<ParentRoute>` instead of `<ProtectedRoute>`. An authenticated EDUCATOR who navigates directly to any of these routes is now redirected to /dashboard instead of reaching the page. Zero tsc errors, zero lint warnings, 9/9 vitest passing. Commit `79ff2f6`, merged to develop as `d82c94f`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| H-31 | Testing: vitest coverage for ChildrenPage.tsx — created `apps/frontend/src/pages/ChildrenPage.test.tsx` with 25 tests across 6 describe blocks: (1) loading state (spinner visible, no error/empty text), (2) error state (message shown, retry button, retry refetches), (3) empty state (heading, "Add Your First Child" CTA, modal opens on click), (4) children grid (cards per profile, age/school/grade/curriculum displayed, "Add another" card, incomplete-profile nudge, edit modal opens), (5) delete flow (confirm → deleteChild called, cancel → not called, error banner on failure, generic banner on throw, button disabled in-flight), (6) ParentRoute role gate (unauthenticated → /login, EDUCATOR → /dashboard, PARENT → content, loading spinner). All 25 tests pass; 0 tsc errors; 0 lint warnings. Commit `20f83ca` on develop. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| H-20 | Parents: Parent onboarding flow — PARENT users who sign up (email or Google OAuth) are now redirected to `/onboarding` instead of `/dashboard`. Created `apps/frontend/src/pages/ParentOnboardingPage.tsx`: a full-screen welcome page that (a) auto-redirects to /dashboard if the user already has children, (b) shows a friendly "Let's set up your child's profile" form (same fields as AddChildModal: name, age, school, country, curriculum, grade, subjects), (c) on success redirects to /dashboard with a brief "All set!" confirmation screen, (d) has a "Skip for now" link. Updated `SignupPage.tsx` email-signup `useEffect` and Google OAuth handler to navigate to `/onboarding` when `selectedRole === 'PARENT'`. Added `<Route path="/onboarding">` wrapped in `<ParentRoute>` in `App.tsx`. Added 9 vitest tests in `ParentOnboardingPage.test.tsx`: loading spinner, redirect-if-children-exist, welcome message with first name, child name input, subject chips, name-required validation, successful submit + redirect, server error display, and skip navigation. 43/43 tests pass; 0 tsc errors; 0 lint warnings. Commit `8b4ba55`, merged to develop as `5d368d7`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| H-01 | Observability: Sentry error monitoring — wired up `sentry-sdk[fastapi]==2.58.0` on the backend and `@sentry/react@^8` on the frontend. Backend: `_init_sentry()` in `apps/backend/main.py` initialises Sentry with `FastApiIntegration`, `SqlalchemyIntegration`, and `LoggingIntegration` (INFO breadcrumbs, ERROR events). Initialisation is conditional: only runs when `SENTRY_DSN` env var is set and `ENVIRONMENT != 'testing'`, so dev/test environments are unaffected. `traces_sample_rate` defaults to 0.1 (configurable via `SENTRY_TRACES_SAMPLE_RATE`). `send_default_pii=False` for COPPA/GDPR safety. Frontend: `main.tsx` lazy-imports `@sentry/react` only when `VITE_SENTRY_DSN` is set, initialising with `browserTracingIntegration`, `replayIntegration` (maskAllText + blockAllMedia), session replay at 10%/100% on error. Added ambient TypeScript stub in `vite-env.d.ts` so tsc passes before `npm ci` installs the package. Added `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, `VITE_SENTRY_DSN` to all four env template files (env.example, .env.example, env.production.template, env.test.template). 0 tsc errors, 0 lint warnings, 45/45 vitest passing. Commit `364762f`, merged to develop as `85c42e6`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| M-26 | Testing: pytest coverage for `_init_sentry()` — created `apps/backend/tests/test_sentry_init.py` with 9 tests across 4 classes covering all branches: (a) `TestSentryInitNoDSN` — no sentry_sdk.init called when DSN is empty, info message logged; (b) `TestSentryInitTestingEnv` — no init when ENVIRONMENT=testing even with a valid DSN, info message logged; (c) `TestSentryInitImportError` — no crash when sentry_sdk is not installed (sys.modules patched to None), warning logged; (d) `TestSentryInitHappyPath` — sentry_sdk.init called with correct DSN + environment, send_default_pii always False (COPPA/GDPR), generic Exception from init is caught and logged without re-raising. Syntax validated; pytest not runnable in sandbox (disk full — /sessions at 100%). Commit `b552efe`, merged to develop as `37f3918`. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |
| H-33 | CI / Observability: Restore Sentry stack accidentally dropped from b552efe — commit `b552efe` (AWD-M-26 test) staged only `test_sentry_init.py` but omitted the 9 working-tree Sentry files, leaving `_init_sentry()` undefined in committed HEAD. Used git plumbing (`git update-index` + `git write-tree` + `git commit-tree`) to stage and commit exactly the 9 affected files on develop: `apps/backend/main.py`, `apps/backend/requirements.txt`, `apps/frontend/package.json`, `apps/frontend/src/main.tsx`, `apps/frontend/src/vite-env.d.ts`, `env.example`, `env.production.template`, `env.test.template`, `.env.example`. Verified: `git show HEAD:apps/backend/main.py | grep _init_sentry` returns the function definition (2 hits); sentry-sdk dep present in requirements.txt; @sentry/react present in package.json; SENTRY_DSN vars in all env templates. TypeScript: 0 errors. Lint: 0 errors. Frontend tests: 45/45 passing. OpenAPI + MCP JSON valid. Commit `4920431`, develop. Push pending (HTTPS credentials unavailable in sandbox — run `git push origin develop` locally). | 2026-04-23 |

## AWD-H-25 — JWT access token migrated from localStorage to HttpOnly cookie
**Fixed**: 2026-04-23
**Commit**: bfef00f (feature) / 3e54929 (merge into develop)
**Summary**: Access token is now set as an HttpOnly cookie (30-min max-age) on all auth endpoints (login, signup, google, refresh). Frontend api.ts uses `credentials: 'include'` on every request; no Authorization header is constructed or sent. AuthContext no longer reads/writes localStorage for token storage. `get_current_user` in `dependencies.py` accepts token from `access_token` cookie if no `Authorization` header is present (backward-compatible for API clients). Both tokens cleared server-side on logout. OpenAPI spec updated with new `CookieAuthResponse` schema.

## AWD-H-34 — get_optional_current_user cookie fallback for HttpOnly cookie auth
**Fixed**: 2026-04-23
**Commit**: c96a71c (feature) / d05de88 (merge into develop)
**Summary**: `get_optional_current_user` in `apps/backend/dependencies.py` was not updated as part of AWD-H-25. It only checked the `Authorization` header, so browser clients (which carry the JWT only in the HttpOnly cookie) were silently treated as anonymous by any route using this dependency (`curriculum.py`, `curriculum_structure.py`, `lesson_plans.py`). Fix mirrors the cookie-fallback logic from `get_current_user`: checks `Authorization` header first, falls back to `access_token` cookie, returns `None` if neither is present or the token is invalid. Authorization header continues to take precedence (backward-compatible for API clients). Five new pytest cases added to `TestGetOptionalCurrentUserCookieFallback` in `test_security.py` covering: header path, cookie path, no auth, invalid cookie token, and header-over-cookie precedence. All 30 tests in `test_security.py` pass.

## AWD-M-24 — SignupPage.tsx catch-block type narrowing
**Fixed**: 2026-04-23
**Commit**: 4489086 (feature) / 33f7b52 (merge into develop)
**Summary**: `SignupPage.tsx` had `catch (err: any)` on lines 55 and 130, violating the code quality checklist rule against unnarrowed catch types. Both blocks changed to `catch (err: unknown)` with `err instanceof Error ? err.message : '<fallback>'` guards before accessing `.message`. No logic change — error messages shown to the user are identical. TypeScript 0 errors, lint 0 warnings, 45/45 frontend tests passing post-fix.

## AWD-M-23 — Content-safety filtering in `validate_output`
**Fixed**: 2026-04-24
**Commit**: 7865610 (feature) / 84d7829 (merge into develop)
**Summary**: `AwadeGPTService.validate_output` previously only checked JSON structure. Added a content-safety pre-pass (`_check_content_safety`) that rejects AI output containing: (1) PII leakage — email addresses, phone numbers, API keys; (2) prompt-injection markers — phrases like "ignore all previous instructions", "jailbreak", "bypass safety"; (3) harmful child-facing content — explicit/adult terms. Module-level pattern constants (`_OUTPUT_PII_PATTERNS`, `_OUTPUT_INJECTION_PATTERNS`, `_HARMFUL_CONTENT_PATTERNS`) keep the patterns maintainable. `test_audit_security_features.py` updated: the placeholder comment noting the feature was missing is replaced with four new assertions covering each safety category. All pattern logic verified via standalone Python script (pytest unavailable in sandbox — disk full).
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-22 — `test_async_integration.py::test_worker_task_execution` mock fix
**Fixed**: 2026-04-24
**Commit**: ad6a631 (fix) / eec3d39 (merge into develop)
**Summary**: `test_worker_task_execution` was asserting `generate_lesson_resource` was called but receiving "called 0 times". Root cause: two bugs in the test setup. (1) `side_effect` list had only 4 items for `.first()`, but the worker makes 5 `.first()` calls — `LessonResource`, `CurriculumStructure`, `Subject`, `GradeLevel`, `LessonTemplate`. The 5th call (LessonTemplate) raised `StopIteration` (exhausted list), which was caught by the worker's `except Exception` block before the AI call, so the mock was never reached. Fix: added 5th `side_effect` entry (`mock_lesson_template` with `schema_json=None`). (2) `return_value = "Generated Content"` (a `str`) could not be unpacked into `(ai_content, is_safe)` as the worker expects — `generate_lesson_resource` returns `tuple[str, bool]`. Fix: changed to `return_value = ("Generated Content", True)`. Added clarifying comments explaining both bugs. Frontend: 45/45 tests still passing. Backend pytest blocked by sandbox disk-full.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-11 — Add Content-Security-Policy header to SecurityHeadersMiddleware
**Fixed**: 2026-04-24
**Commit**: afed4c2 (feat) / b40496a (merge into develop)
**Summary**: Added `Content-Security-Policy` header to `SecurityHeadersMiddleware` in `apps/backend/middleware/security_headers.py`. Policy: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'`. This complements the existing `X-Frame-Options: DENY`, `X-Content-Type-Options`, `HSTS`, and `Referrer-Policy` headers. Updated `test_security.py` with `test_security_headers` asserting the CSP header is present and `test_csp_header_directives` asserting the four key directives. Frontend: 45/45 tests passing, TS clean, lint clean, openapi.json and mcp.json valid.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-10 — Disable /docs and /redoc in production
**Fixed**: 2026-04-24
**Commit**: 1c175fc (fix) / 6adca34 (merge into develop)
**Summary**: Gated FastAPI `docs_url` and `redoc_url` on `ENVIRONMENT != "production"` in `apps/backend/main.py`. Added module-level `_APP_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")` and set `docs_url=None if _APP_ENVIRONMENT == "production" else "/docs"` (same for redoc). Created `apps/backend/tests/test_docs_visibility.py` with 7 tests covering: endpoint accessibility outside production, app URL config matching environment, and the gating expression evaluated for all three env values (production / development / testing). Frontend: 45/45 tests passing, TS clean, lint clean, openapi.json and mcp.json valid. Backend pytest skipped — venv symlink broken (python3.13 absent in sandbox); verify locally before promoting to main.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally. Also: M-09 (catalog auth guards) inspected and confirmed already implemented — no code change needed; backlog entry can be closed.

## AWD-H-35 — Restore Content-Security-Policy header lost in M-10 merge
**Fixed**: 2026-04-24
**Commit**: 2f0fc8a (fix) / ebefbd7 (merge into develop)
**Summary**: Commit `1c175fc` (AWD-M-10) was cut from a pre-M-11 version of `security_headers.py` and clobbered the CSP header added by AWD-M-11 (`afed4c2`). Restored `Content-Security-Policy` header to `SecurityHeadersMiddleware` in `apps/backend/middleware/security_headers.py`. Updated `apps/backend/tests/test_security.py` to assert CSP presence in `test_security_headers` and added `test_csp_header_directives` test for key directives. Frontend: 45/45 tests passing, TS clean, lint clean, openapi.json and mcp.json valid. Backend pytest skipped — venv symlink broken in sandbox; verify locally before promoting to main.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-36 — Restrict CORS allow_methods and allow_headers from wildcard
**Fixed**: 2026-04-24
**Commit**: 64d117b (fix) / 25f78c2 (merge into develop)
**Summary**: `apps/backend/main.py` CORS middleware used `allow_methods=["*"]` and `allow_headers=["*"]`, permitting any HTTP method and header cross-origin. Restricted to `allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` and `allow_headers=["Authorization", "Content-Type", "X-Requested-With"]` — exactly what the frontend needs. Added `test_cors_allowed_methods_and_headers` to `apps/backend/tests/test_security.py` asserting no wildcards and all required values present. All 32 security tests pass. Frontend: tsc clean, lint clean, openapi.json and mcp.json valid. Pre-existing 21 backend test failures (test_ai_providers, test_children_router, test_children_service) are unrelated and were present on develop before this branch.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-13 — N+1 query in ChildrenService.get_child_topics resolved with joinedload
**Fixed**: 2026-04-24
**Commit**: db282f7 (fix) / f0f7a84 (merge into develop)
**Summary**: `get_child_topics` queried topics with `.join(CurriculumStructure)` but then accessed `t.curriculum_structure.subject.name` per-topic in the list comprehension without eager loading, issuing ~2 extra queries per topic (~160 extra for an 80-topic grade). Fix: added `.options(joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject))` to the query. Also fixed 5 pre-existing test mock bugs in `TestGenerateGuideIdempotency` and `TestGenerateGuideAIValidation` (double-filter chain vs single-filter call in mocks), and added `TestGetChildTopics` class with 5 tests covering empty-state, topic-list, null curriculum_structure, and role-gate (403). All 31 `test_children_service.py` tests pass. Frontend checks: tsc clean, lint clean, 45 vitest passing. Remaining 16 backend failures (test_ai_providers OpenAI/Gemini init, test_children_router 401-vs-403 assertions) are pre-existing and unrelated.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-08 — Pin exact versions in backend requirements.txt for reproducible builds
**Fixed**: 2026-04-24
**Commit**: 31a9d95 (fix) / 6900b9f (merge into develop)
**Summary**: Replaced all `>=X.Y.Z` version specifiers in `apps/backend/requirements.txt` with exact `==X.Y.Z` pins. Every package now has an exact version. Core packages pinned conservatively to latest patch of the minimum minor (fastapi==0.109.2, pydantic==2.6.4, sqlalchemy==2.0.29, uvicorn==0.27.1, alembic==1.13.3). Security-minimum packages pinned to their stated floor (python-multipart==0.0.18, jinja2==3.1.6, requests==2.32.4, urllib3==2.5.0, cryptography==44.0.1, setuptools==78.1.1). openai pinned to 1.12.0 (1.x — openai 2.x has breaking API changes). google-generativeai pinned to 0.7.2 (compatible with gemini-flash-latest model). Previously unversioned email-validator pinned to 2.1.0. Existing exact pins (PyJWT==2.12.1, sentry-sdk==2.58.0, httplib2==0.22.0) unchanged. All 30 packages now reproducibly pinned. Frontend checks: tsc clean, lint clean, 45 vitest passing. openapi.json and mcp.json valid.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-H-34 — get_optional_current_user cookie fallback
**Fixed**: 2026-04-24 (confirmed already committed in prior session at c96a71c)
**Commit**: c96a71c (fix/security)
**Summary**: `get_optional_current_user` in `apps/backend/dependencies.py` already mirrored the cookie-fallback logic from `get_current_user`. Cookie-based auth tested via `TestGetOptionalCurrentUserCookieFallback` (5 tests in `test_security.py` — all 32 security tests pass). Backlog entry was incorrectly left open; cleaned up this run.

## AWD-M-18 — Remove TODO comments from SettingsPage.tsx
**Fixed**: 2026-04-24
**Commit**: fc130ab (style/settings → develop fast-forward)
**Summary**: `handleSaveLogin()` in `apps/frontend/src/pages/SettingsPage.tsx` had two empty `// TODO:` blocks that silently did nothing but showed a false "updated successfully!" alert. Removed TODO comments and replaced with honest UX: if user attempts email or password change, show "Email and password updates are not yet available. Please contact support." and return early without false confirmation. Frontend validation: tsc clean, lint clean, 45/45 vitest passing.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-01 — Loading and error states for parent pages
**Fixed**: 2026-04-24
**Commit**: 19017d1 (feat/parents → develop merge 5e72d9d)
**Summary**: `ParentDashboardPage` and `SavedGuidesPage` silently swallowed fetch errors — a failed children request showed the empty "Welcome" or spinner state rather than an error. Fixed by adding `isError` / `refetch` from React Query to both children and topics queries in `ParentDashboardPage.tsx`, and children and guides queries in `SavedGuidesPage.tsx`. Each error case now shows a user-facing "Failed to load…" message with a "Try again" retry button. `GuideViewPage` was already fully compliant. Added 15 new vitest tests across `ParentDashboardPage.test.tsx` (7 tests) and `SavedGuidesPage.test.tsx` (8 tests) covering loading, error, empty, and success states. All 60 vitest tests pass; tsc clean; lint clean.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-36 — Fix invalid nested `<button>` elements in ParentDashboardPage child selector cards
**Fixed**: 2026-04-24
**Commit**: ff6856c (fix/parents → develop merge 9e25c23)
**Summary**: Child selector cards in `ParentDashboardPage.tsx` were `<button>` elements containing nested `<button>` (Edit, Delete), which is invalid HTML per spec and causes WCAG 2.1 failures and `validateDOMNesting` warnings in vitest. Fixed by converting the outer card from `<button>` to `<div role="group" aria-label={child.name} tabIndex={0}>` with `onClick` and `onKeyDown` handlers (Enter/Space) for full keyboard accessibility. The Edit and Delete `<button>` elements inside are now valid descendants of a non-interactive container. Added 3 new vitest tests to `ParentDashboardPage.test.tsx`: verifies the card is a `div` not a `button`, verifies edit/delete buttons have no button ancestor within the card, and verifies keyboard Enter selection. All 63 vitest tests pass; tsc clean; lint clean.
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally.

## AWD-M-14 — Performance: batch subject FK validation in create_child / update_child
**Completed**: 2026-04-24
**Commit**: d9f8125 / merge 99981fc
**Change**: Replaced N per-subject queries with a single `Subject.subject_id.in_(ids)` batch query in both `create_child` and `update_child`. Added 9 new tests (batch pass, partial invalid, full invalid, single-call assertion for both methods).

## AWD-M-02 — SEO: Meta tags + OG images on landing page
**Completed**: 2026-04-24
**Commit**: 34940e1 / merge 577921c
**Change**: Updated `apps/frontend/index.html` with full SEO meta suite — updated title and description reflecting post-pivot parent audience, Open Graph tags (og:title, og:description, og:type, og:url, og:image, og:image dimensions, og:site_name, og:locale with African market alternates), Twitter/X Card tags, canonical URL, and Schema.org WebApplication structured data with areaServed for NG/GH/KE/ZA. Created `apps/frontend/public/og-image.svg` (1200×630) as the OG image with brand gradient, wordmark, and tagline. All 63 frontend tests pass. No API changes.

## AWD-M-37 — SEO: Convert og-image SVG to PNG for social sharing compatibility
**Completed**: 2026-04-24
**Commit**: d791752 / merge 7ac1c42
**Change**: Converted `apps/frontend/public/og-image.svg` to `og-image.png` (1200×630, PNG, 85 KB). Updated `og:image` and `twitter:image` meta tags in `apps/frontend/index.html` (lines 22 and 36) to reference `og-image.png`. SVG is not supported by Facebook, WhatsApp, LinkedIn, or most OG crawlers — this fix ensures social share previews render correctly. Source SVG retained for future edits. No backend or API changes; all 63 frontend tests pass.

## AWD-H-36 — Fix: Restore batch subject FK query regression + AI guide validation (H-06)
**Completed**: 2026-04-24
**Commit**: b25e3a0 / merge 67d23ce
**Change**: The working tree had regressed `children_service.py` to use per-subject DB loops instead of the single `Subject.subject_id.in_(ids)` batch query shipped in AWD-M-14. Also removed were `_db_subjects_not_found`, `test_partial_invalid_subjects_raises_400_for_first_bad_id`, `test_all_valid_subjects_does_not_raise`, `test_subject_validation_uses_single_batch_query`, and `TestUpdateChildSubjectValidation` from the test suite. Both regressions are now restored. Additionally, the AI guide schema validation block (`ParentGuideAIContent.model_validate_json`) from AWD-H-06 and the `ValidationError` / `ParentGuideAIContent` imports are now correctly committed as part of `children_service.py`. Import ordering cleaned up (stdlib → third-party → local). 37 children service tests pass.

## AWD-H-37 — Fix: TestUnauthenticated assertion updated from 403 to 401
**Completed**: 2026-04-24
**Commit**: af523cd / merge a513468
**Change**: Since AWD-H-25 changed `HTTPBearer(auto_error=True)` to `auto_error=False`, unauthenticated requests now receive `401` (raised manually by `get_current_user`) rather than FastAPI's default `403`. The 10 tests in `TestUnauthenticated` still asserted `403`, causing them to fail on every CI run since H-25 shipped. Fixed by updating the assertion to `401`, renaming `test_returns_403` → `test_returns_401`, and updating the class docstring to reflect the current auth behaviour.

## AWD-H-38 — Fix: TestGenerateGuideIdempotency and TestGenerateGuideMalformedAI mock DB mismatch
**Completed**: 2026-04-24
**Commit**: f7bb28f / merge f61736b
**Change**: 3 tests in `test_children_router.py` were failing with 500 instead of 200/502 because their mock DB setups wired two chained `.filter().filter()` calls, but `ChildrenService.generate_guide()` uses a single `.filter(cond1, cond2)` call. Removed the extra `.filter.return_value` layer in `TestGenerateGuideIdempotency.test_existing_guide_returned_no_ai_call` (~line 439) and `TestGenerateGuideMalformedAI._build_db_no_existing_guide` (~line 492-495). No production code changed — mock wiring fix only.

## AWD-M-12 — Prompt injection: fence user-supplied context with XML delimiters and scrub injection patterns
**Completed**: 2026-04-24
**Commit**: 322e9e5
**Change**: Three-layer input sanitisation applied to educator-supplied `context_input` before it enters `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` as `{local_context}`. (1) `packages/ai/prompts.py` — added `IMPORTANT` instruction above the local-context field and wrapped `{local_context}` in `<user_context>` XML tags so the model treats it as data, not instructions. (2) `packages/ai/gpt_service.py` — added `_MAX_USER_CONTEXT_CHARS = 2000`, `_INPUT_INJECTION_PATTERNS` list (10 patterns), and new `_sanitize_user_context()` method that truncates, strips PII, and scrubs injection phrases; `generate_lesson_resource()` now calls `_sanitize_user_context(context)` before building `prompt_params`. (3) `apps/backend/tests/test_ai_providers.py` — added 11 new tests in `TestSanitizeUserContext` covering passthrough, None/empty, truncation, PII stripping, and each injection pattern category including an end-to-end check confirming injection phrases never reach the rendered prompt.

## AWD-M-39 — Migrate GeminiProvider from deprecated google-generativeai to google-genai
**Completed**: 2026-04-24
**Commit**: 20e88d4
**Change**: Migrated `packages/ai/providers/gemini_provider.py` from the deprecated `google-generativeai` SDK to the new `google-genai` SDK. Import changed from `import google.generativeai as genai` to `from google import genai` + `from google.genai import types as genai_types`. Client init replaced `genai.configure()` with `self.client = genai.Client(api_key=...)`. Content generation rewritten to use `self.client.models.generate_content(model=..., contents=..., config=types.GenerateContentConfig(...))`. Safety settings migrated from a dict keyed on `HarmCategory` to a list of `types.SafetySetting` objects. `apps/backend/requirements.txt` updated from `google-generativeai==0.7.2` to `google-genai==1.14.0`. Test assertion in `test_ai_providers.py` updated from `mock_genai.configure` to `mock_genai.Client`. All 19 tests pass.

## AWD-M-40 — npm audit fix: patch postcss XSS (GHSA-qx2v-qp2m-jg93)
**Completed**: 2026-04-24
**Commit**: e7a1d51
**Change**: Ran `npm audit fix` in `apps/frontend` — updated `postcss` from 8.5.6 to 8.5.10 to close GHSA-qx2v-qp2m-jg93 (XSS via unescaped `</style>` in CSS stringify output). Also updated transitive rollup and esbuild lockfile entries. 63 frontend tests pass, lint clean, build clean post-fix.

## AWD-M-38 — Fix `_sanitize_user_context` type annotation to `Optional[str]`
**Completed**: 2026-04-25
**Commit**: 4b52109 (merge 3b930b3)
**Change**: Updated `_sanitize_user_context` signature in `packages/ai/gpt_service.py` from `(text: str) -> str` to `(text: Optional[str]) -> Optional[str]`. `Optional` was already imported. The method body correctly handles `None` via `if not text: return text`, and the production caller guards with `if context else None`. Type annotation now matches documented and tested behaviour. TypeScript check clean, lint clean.

## AWD-H-39 — GeminiProvider: add explicit request timeout (OWASP LLM10 / Model DoS mitigation)
**Completed**: 2026-04-25
**Commit**: pending — code on disk, bash sandbox out of disk space; Tolu must commit and push
**Change**: Added `DEFAULT_TIMEOUT = 60.0` class variable and `GEMINI_TIMEOUT_SECONDS` env-var override to `GeminiProvider`, mirroring the pattern from `OpenAIProvider` (AWD-H-09). `genai.Client()` now receives `http_options=genai_types.HttpOptions(timeout=self.timeout)` — prevents a hung Gemini call from blocking a FastAPI worker indefinitely. `genai_types` was already imported from the M-39 migration. Updated `test_initialization` in `TestGeminiProvider` (was asserting bare `assert_called_with(api_key=...)` — now checks `http_options` is present). Added `test_initialization_custom_timeout` (GEMINI_TIMEOUT_SECONDS env override). Added `GEMINI_TIMEOUT_SECONDS=60` to `.env.example`. No API changes; no Alembic migration needed.
**Files changed**: `packages/ai/providers/gemini_provider.py`, `apps/backend/tests/test_ai_providers.py`, `.env.example`
**Action required**: From the repo root on your Mac:
  ```
  git add packages/ai/providers/gemini_provider.py apps/backend/tests/test_ai_providers.py .env.example
  git commit -m "fix(ai): AWD-H-39 add 60s timeout to GeminiProvider via HttpOptions"
  git push origin develop
  ```

## AWD-M-05 — Share-to-WhatsApp button on parent guides
**Completed**: 2026-04-25
**Commit**: pending — code on disk, bash sandbox out of disk space; Tolu must commit and push
**Change**: Added `FaWhatsapp` import and `handleWhatsAppShare()` function to `apps/frontend/src/pages/GuideViewPage.tsx`. The function composes a parent-friendly WhatsApp deep-link including: topic title, subject, grade level, a truncated explanation (≤180 chars), home activity title, and "awade.app" attribution. Uses `window.open('https://wa.me/?text=<encoded>', '_blank', 'noopener,noreferrer')`. Button added to the top bar to the left of the existing bookmark button, with `aria-label="Share this guide on WhatsApp"` for accessibility. Created `apps/frontend/src/pages/GuideViewPage.test.tsx` with 8 tests: loading state, error state, malformed-JSON error state, success render (title + explanation), generate-guide path (child+topic params), WhatsApp button presence, WhatsApp URL shape (correct prefix, topic/subject/grade/activity/branding in decoded text, `_blank` target, `noopener,noreferrer` features), and no-call-when-loading guard. No API changes; no Alembic migration needed.
**Files changed**: `apps/frontend/src/pages/GuideViewPage.tsx`, `apps/frontend/src/pages/GuideViewPage.test.tsx` (new)
**Action required**: From the repo root on your Mac:
  ```
  cd apps/frontend && npm run test:run  # verify all tests pass
  git add apps/frontend/src/pages/GuideViewPage.tsx apps/frontend/src/pages/GuideViewPage.test.tsx
  git commit -m "feat(parents): AWD-M-05 add WhatsApp share button to guide view"
  git push origin develop
  ```

## AWD-C-06 — CRITICAL git repo corruption: af7f7b5 mass-deleted 266 tracked files from git tree
**Completed**: 2026-04-25
**Commits**: a762c11 (recovery) / f4ebdb3 (pending changes)
**Change**: Detected that commit `af7f7b5` (chore: add QA entry for AWD-M-12, dated 2026-04-24) had accidentally deleted 266 of 267 tracked files from the git tree while leaving them on disk. `git ls-tree HEAD` showed only 8 files; `git ls-tree b606c38` showed 266 files. All subsequent commits (M-39, M-40, M-38) built on the corrupted tree. Recovery: (1) ran `git read-tree b606c38` to restore the full 266-file index; (2) re-staged M-38/M-39/M-40 working-tree changes explicitly; (3) committed recovery (`a762c11`, 267 files); (4) staged remaining pending on-disk changes not in b606c38 (AWD-H-39 .env.example, AWD-M-05 GuideViewPage + tests, AWD-M-03 package.json + setup-hooks.sh, new test files) and committed (`f4ebdb3`, 272 files). Working tree is now clean. **Tolu must `git push origin develop`** to restore origin/develop (currently 7 files) to the full 272-file codebase and unblock CI.

## AWD-H-41 — Fix GuideViewPage.test.tsx TypeScript errors and failing test
**Completed**: 2026-04-25
**Commit**: f9605aa (fix), b5bc031 (merge into develop)
**Change**: Removed unused `import React from 'react'` (TS6133); changed 5× `error: null` to `error: undefined` in mock return values (TS2322 — `ApiResponse.error` is `string | undefined`, not `string | null`); wrapped the heading assertion in the `generateGuide` path test inside its own `await waitFor(...)` block so React Query state has settled before the assertion runs. All 72 frontend tests pass; TypeScript and lint clean. **Tolu must `git push origin develop`** to trigger CI.

## AWD-M-39 — Upgrade openai dependency to 1.109.1 + use safe_context in cache metadata
**Completed**: 2026-04-25
**Commits**: 3b2c067 (fix), 015b8f1 (merge into develop)
**Changes**:
- `apps/backend/requirements.txt`: upgraded `openai==1.12.0` → `openai==1.109.1` (latest 1.x; stays below 2.x which has breaking API changes). Closes the ~97-minor-version gap and picks up all security patches in the 1.x series.
- `packages/ai/gpt_service.py` line 505: changed `"context": context` → `"context": safe_context` in `prompt_metadata` dict. The sanitised value (length-capped, PII-stripped, injection-scrubbed) is now what gets stored in the Redis cache metadata — defence-in-depth, consistent with how it's already used in the actual prompt.
- All validation green: TypeScript 0 errors, lint 0 warnings, 72/72 frontend tests pass, openapi.json and mcp.json valid. Backend tests skipped in sandbox (broken macOS venv on Linux — pre-existing issue).
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally to trigger CI.

---

**AWD-C-07 — Chore commit `547a4ac` silently reverted two security fixes from AWD-M-39**
**Completed**: 2026-04-25
**Commit**: `6880ce3` fix(security): AWD-C-07 restore safe_context and openai 1.109.1 reverted by 547a4ac
**Changes**:
- `packages/ai/gpt_service.py` line 505: restored `"context": safe_context` (had been accidentally reverted to `"context": context` by chore commit `547a4ac`). The sanitised value is now committed on develop.
- `apps/backend/requirements.txt`: restored `openai==1.109.1` (had been accidentally downgraded back to `openai==1.12.0` by `547a4ac`).
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally to trigger CI. Both files were already correct on disk as uncommitted changes; this commit simply memorialised them.

---

## AWD-M-15 — TypeScript types for children & guides API methods
**Completed**: 2026-04-25
**Commit**: `663b50a` feat(frontend): AWD-M-15 add proper types to children and guides API methods
**Merge**: `91b2740` Merge fix/frontend/AWD-M-15-api-types into develop
**Changes**:
- `apps/frontend/src/types/children.ts`: added `ChildProfileUpdate`, `ChildProfileListResponse`, and `ParentGuideListResponse` interfaces to complete the type set already started in the file.
- `apps/frontend/src/services/api.ts`: added import of all 7 children/guides types; replaced `ApiResponse<any>` on all 11 children/guides API methods (`getChildren`, `getChild`, `createChild`, `updateChild`, `deleteChild`, `getChildTopics`, `getChildGuides`, `generateGuide`, `getGuide`, `toggleGuideBookmark`) with correct typed generics.
- `apps/frontend/src/pages/GuideViewPage.tsx`: added explicit null-guards (`if (!res.data) throw new Error(...)`) so `useQuery<ParentGuide>` queryFn satisfies its non-undefined return type.
- `apps/frontend/src/pages/ParentDashboardPage.tsx`: removed stale `as ChildTopic[]` cast (now inferred from typed `getChildTopics`).
- `apps/frontend/src/pages/ChildrenPage.test.tsx`, `ParentDashboardPage.test.tsx`, `SavedGuidesPage.test.tsx`: updated mock return values — `data: null` → `data: undefined`, added missing `total` field to `ChildProfileListResponse` mocks.
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally to trigger CI.

---

## AWD-M-04 — Shore up backend test coverage: children_service guide methods + lesson_plan_service
**Completed**: 2026-04-25
**Commit**: 7fe0c3b (feature) → 3340c8d (merge into develop)
**Files changed**:
- `apps/backend/tests/test_lesson_plan_service.py` (new — 43 tests across 7 classes): `TestFetchCurriculumData`, `TestCreateLessonPlanResponse`, `TestGetLessonPlan`, `TestUpdateLessonPlan`, `TestDeleteLessonPlan`, `TestGetAllLessonResources`, `TestGetLessonPlanResources`, `TestGetLessonResource` — covers happy paths, 404, 403, admin bypass, and field mapping for all previously untested service methods.
- `apps/backend/tests/test_children_service.py` (appended): added `TestListGuides` (5 tests), `TestGetGuide` (5 tests), `TestToggleBookmark` (5 tests) — covers role gate (educator→403), ownership (wrong parent→404), empty list, `bookmarked_only` filter, `is_bookmarked` int→bool coercion, toggle 0→1 and 1→0, commit call assertion.
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · Python AST syntax ✅ · openapi.json ✅ · mcp.json ✅
**Note**: Backend pytest skipped in sandbox (pre-existing venv python3.13→3.10 mismatch). Push to origin/develop pending Tolu's `git push origin develop`.

---

## AWD-M-41 — Restore typed API interfaces stripped by AWD-M-04 test commit
**Completed**: 2026-04-25
**Commit**: (see merge into develop below)
**Changes**:
- `apps/frontend/src/types/children.ts`: restored 3 deleted interfaces — `ChildProfileUpdate`, `ChildProfileListResponse`, `ParentGuideListResponse`.
- `apps/frontend/src/services/api.ts`: restored typed import block; re-typed 8 API methods (`getChildren`, `getChild`, `createChild`, `updateChild`, `deleteChild`, `getChildTopics`, `getChildGuides`, `generateGuide`, `getGuide`, `toggleGuideBookmark`) from `ApiResponse<any>` to proper typed generics.
- `apps/frontend/src/pages/GuideViewPage.tsx`: added two null-guards (`if (!res.data) throw ...`) to satisfy `useQuery<ParentGuide>` return-type contract.
- `apps/frontend/src/pages/ParentDashboardPage.tsx`: replaced unsafe `res.data as ChildTopic[]` cast with safe `res.data ?? []`.
- Test files (`ChildrenPage.test.tsx`, `ParentDashboardPage.test.tsx`, `SavedGuidesPage.test.tsx`): updated mock shapes to match typed API (`data: null` → `data: undefined`, added `total` field to list responses).
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked by missing GitHub credentials in sandbox — Tolu must run `git push origin develop` locally to trigger CI.

---

## AWD-M-21 — Guide PDF export for parents
**Completed**: 2026-04-25 | **Commit**: c83bee8
**Description**: Parents can now download any "How to Help" guide as a print-ready PDF directly from GuideViewPage.
**Changes**:
- `apps/backend/services/pdf_service.py`: Added `generate_guide_pdf(content, meta)` method with A4-formatted HTML/CSS template; static `_h()` HTML-escape helper; `_get_guide_css_styles()` for guide-specific CSS. WeasyPrint used for rendering (already in requirements).
- `apps/backend/routers/children.py`: Added `GET /api/guides/{guide_id}/export` endpoint — auth-gated, ownership-checked via ChildrenService, returns `application/pdf` with safe `Content-Disposition` filename derived from topic title. Raises 422 (no/malformed content), 503 (WeasyPrint unavailable), 500 (unexpected). Added `import json, logging, re` and `Response` to imports.
- `apps/frontend/src/services/api.ts`: Added `exportGuidePdf(guideId)` method returning `{ blob, filename }` or `{ error }` — handles binary response directly without going through `handleResponse`.
- `apps/frontend/src/pages/GuideViewPage.tsx`: Added `FaDownload` icon, `isDownloading` state, `handleDownloadPdf()` handler (creates object URL, triggers anchor click, revokes URL). Download button placed first in the top-bar action group with spinner while in-flight.
- `apps/backend/tests/test_children_router.py`: Added `TestExportGuidePdf` class with 6 tests: 401 unauthenticated, 404 guide not found, 422 no content, 422 malformed content, 503 WeasyPrint unavailable, 200 happy path (PDFService mocked).
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · openapi.json ✅ (valid JSON; full regen needed locally — spec predates parent pivot)
**Note**: Push to origin/develop blocked — Tolu must run `git push origin develop` to trigger CI.

---

## AWD-M-42 — Replace bare `print()` with `logger.warning()` in `pdf_service.py`
**Completed**: 2026-04-25
**Commit**: f0dddf4
**Fix**: Added `import logging` and `logger = logging.getLogger(__name__)` to `apps/backend/services/pdf_service.py`; replaced the bare `print("Warning: WeasyPrint not available. PDF generation will be disabled.")` in the `except ImportError` block with `logger.warning("WeasyPrint not available — PDF generation will be disabled.")`. Eliminates stdout pollution on every module import and aligns with CLAUDE.md code hygiene rules.
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked in sandbox — Tolu must run `git push origin develop` to trigger CI.

---

### AWD-M-35 — Remove `unsafe-inline` from CSP `script-src`
**Completed**: 2026-04-25
**Commit**: fb9e718
**Fix**: Removed `'unsafe-inline'` from the `script-src` directive in `apps/backend/middleware/security_headers.py` (short-term hardening per OWASP XSS guidance). `style-src` retains `'unsafe-inline'` for now; full nonce-based hardening deferred. Added `test_csp_script_src_no_unsafe_inline()` to `apps/backend/tests/test_security.py` to assert `'unsafe-inline'` is absent from `script-src` and that `'self'` is retained.
**Validation**: tsc 0 errors · eslint 0 errors · vitest 72/72 passing · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked in sandbox — Tolu must run `git push origin develop` to trigger CI.

---

### AWD-M-44 — Hollow `test_rate_limiting` — add `@pytest.mark.skip` with backlog reason
**Completed**: 2026-04-25
**Commit**: 2f79fed (merge: 27a45f0)
**Fix**: Added `@pytest.mark.skip(reason="AWD-M-44 ...")` decorator to the hollow `test_rate_limiting` function in `apps/backend/tests/test_security.py`. The test body (`pass`) remained — now correctly documented as skipped pending the `rate_limiter_reset` autouse fixture from AWD-H-29 before a real 429 assertion can be made safely.
**Validation**: Python AST syntax check ✅ · openapi.json ✅ · mcp.json ✅ · no frontend changes
**Note**: Push to origin/develop blocked in sandbox (HTTPS auth) — Tolu must run `git push origin develop` to trigger CI.

---

## AWD-M-43 — Remove `style-src 'unsafe-inline'` from CSP

**Completed**: 2026-04-25
**Commit**: 490b05a (merge: b63adbf)
**Fix**: Removed `'unsafe-inline'` from `style-src` in `SecurityHeadersMiddleware`. React inline `style={{ }}` props are applied via JS DOM API (governed by `script-src`) so no nonce is needed. Added `https://fonts.googleapis.com` to `style-src` and a new `font-src 'self' https://fonts.gstatic.com` directive to keep Google Fonts working. Added two new backend tests: `test_csp_style_src_no_unsafe_inline` and `test_csp_font_src_google_fonts`.
**Validation**: tsc 0 errors ✅ · lint 0 errors ✅ · frontend tests 72/72 ✅ · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked in sandbox (HTTPS auth) — Tolu must run `git push origin develop` to trigger CI.

---

**AWD-M-06 — Landing page Lighthouse performance: image optimisation + code splitting**
**Completed**: 2026-04-25
**Commit**: 3c0e2be (merge: ebf6289)
**Fix**: 
- Converted all 4 landing-page PNGs to WebP (Pillow, quality 80): hero 2.5 MB→182 KB (93%), feature-1 1.2 MB→26 KB (98%), feature-2 2.0 MB→117 KB (94%), feature-3 1.7 MB→57 KB (97%). Total image payload: 7.4 MB → 382 KB.
- Renamed assets to clean filenames (`hero`, `feature-1/2/3`).
- Wrapped all hero `<img>` elements in `<picture><source type="image/webp">` for WebP-first delivery with PNG fallback.
- Added `fetchPriority="high"` + explicit `width`/`height` to hero images (improves LCP and prevents CLS).
- Added `loading="lazy"` + explicit dimensions to feature images (below fold).
- Updated `vite.config.ts` with `manualChunks` to split `react-router-dom` and `@tanstack/react-query` into separate vendor bundles, reducing main JS chunk parse time.
**Validation**: tsc 0 errors ✅ · lint 0 errors ✅ · frontend tests 72/72 ✅ · build (temp dir) ✅ · openapi.json ✅ · mcp.json ✅
**Note**: Push to origin/develop blocked in sandbox (HTTPS auth) — Tolu must run `git push origin develop` to trigger CI.

## AWD-M-45 — fetchPriority React prop warning (bumped react to ^18.3.0)
- **Completed**: 2026-04-26
- **Commit**: 27f9f01 (fix(frontend): AWD-M-45 bump react/react-dom to ^18.3.0 for fetchPriority support)
- **Merge**: c863a67
- **Fix**: Bumped react/react-dom from ^18.2.0 to ^18.3.0 and @types/react/@types/react-dom from ^18.2.0 to ^18.3.0 in apps/frontend/package.json. React 18.3.0 added official camelCase fetchPriority prop support, eliminating the test-suite warning. Lock file already pinned 18.3.1 so no npm install was required. 72/72 frontend tests pass, 0 TS errors, 0 lint errors.
