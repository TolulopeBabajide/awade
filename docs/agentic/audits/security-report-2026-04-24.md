# Security Audit Report — 2026-04-24

**Agent**: Security Agent (scheduled, 6am daily run)
**Repo root**: `apps/backend/awade` (develop branch)
**Scope**: CI security mirror · Secret scan · Dependency audit · OWASP Web Top 10 · OWASP LLM Top 10
**Previous report**: [2026-04-23](security-report-2026-04-23.md)

---

## 1. CI Security Job Mirror

| Check | Result | Notes |
|-------|--------|-------|
| `git ls-files` — no `.env`/`.key`/`.pem`/`.p12` | ✅ PASS | |
| `git ls-files` — no `docs/private/` | ✅ PASS | |
| `.env.example` exists | ✅ PASS | |
| `.cursor/mcp.json` is valid JSON | ✅ PASS | |
| `apps/backend/app/openapi.json` is valid JSON | ✅ PASS | |

**All CI security checks pass.**

---

## 2. Secret Scan

Scanned `apps/` and `packages/` for hardcoded API keys, passwords, and tokens.

| Finding | File | Verdict |
|---------|------|---------|
| `password=REDIS_PASSWORD` | `apps/backend/redis_client.py:17` | ✅ Safe — variable assigned from `os.getenv("REDIS_PASSWORD", None)` |
| `admin_password = os.getenv(...)` | `apps/backend/init_db.py:64,82,87` | ✅ Safe — read from env; `getpass` fallback for interactive setup |
| `api_key = api_key or os.getenv("OPENAI_API_KEY")` | `packages/ai/providers/openai_provider.py:27` | ✅ Safe — env var lookup only |
| `api_key = api_key or os.getenv("GEMINI_API_KEY")` | `packages/ai/providers/gemini_provider.py:24` | ✅ Safe — env var lookup only |
| `secret = "dev-secret"` (fallback) | `apps/backend/dependencies.py:39` | ⚠️ Dev-only fallback — guarded by `ENVIRONMENT != "production"` check which raises `RuntimeError` in prod; acceptable but documented below |

**No hardcoded production secrets found.** The `"dev-secret"` JWT fallback is guarded: `get_jwt_secret_key()` raises `RuntimeError` in production if `JWT_SECRET_KEY` is not set. Risk is low but worth the note.

---

## 3. Dependency Audit

### Frontend (npm)
```
npm audit --production → 0 vulnerabilities
```
✅ Clean.

### Backend (pip)

`requirements.txt` pins security-critical packages correctly:
- `PyJWT==2.12.1` (exact pin — CVE surface addressed)
- `cryptography>=44.0.1` (CVE-2024-12797 fix)
- `jinja2>=3.1.6` (CVE-2025-27516 fix)
- `bcrypt>=4.0.0`
- `python-multipart>=0.0.18` (CVE-2024-53981 fix)
- `requests>=2.32.4` (CVE-2024-47081 fix)
- `urllib3>=2.5.0` (CVE-2025-50181/50182 fix)
- `setuptools>=78.1.1` (CVE-2025-47273 fix)

⚠️ **Dev environment version drift** (non-blocking for CI/production): Local dev machine has older system packages installed (PyJWT 2.3.0, Jinja2 3.0.3, bcrypt 3.2.0). CI runs `pip install -r requirements.txt` fresh each time, so production and CI use correct pinned versions. This is a developer experience issue, not a production security gap. See **M-08** (pin exact versions for reproducible local installs).

---

## 4. OWASP Web Top 10

### Web-1: Broken Access Control

**Auth coverage across all routers:**

| Router | Auth Dependency | Role Check |
|--------|----------------|------------|
| `auth.py` | Public (login/register endpoints + token refresh) | N/A |
| `children.py` | `get_current_active_user` on all endpoints | `_verify_parent()` in service layer enforces PARENT role |
| `lesson_plans.py` | `get_current_active_user` | EDUCATOR/ADMIN in service |
| `contexts.py` | `require_admin_or_educator` | Ownership check per context |
| `admin.py` | `require_admin` (router-level `dependencies=[]`) | SUPER_ADMIN check for role promotion |
| `users.py` | `require_admin` or `require_admin_or_educator` | ✅ |
| `curriculum.py` | `get_current_user` / `require_admin` | ✅ |
| `country.py` | `get_current_user` / `require_admin` | ✅ |
| `subject.py`, `grade_level.py`, `curriculum_structure.py` | Auth-guarded | ✅ |

✅ No unguarded non-public routes found. AWD-M-09 (catalog endpoints unauthenticated) confirmed resolved.

**Notes:**
- `require_parent` dependency exists in `dependencies.py` but is not wired into `children.py` router (uses `get_current_active_user` + service-layer role check instead). Functional but the router-level guard would fail faster — tracked as **L-05**.
- **AWD-H-34** (open): `get_optional_current_user` not updated for HttpOnly cookie auth — browser clients silently treated as anonymous on affected routes. Not resolved; no new action today.

### Web-2: Cryptographic Failures

- Passwords: bcrypt (requirements.txt enforces `>=4.0.0`) ✅
- JWTs: PyJWT 2.12.1 pinned, HS256 algorithm, `SECRET_KEY` from env ✅
- HTTPS: Render/Vercel enforce TLS ✅
- Auth tokens: stored in HttpOnly cookies (AWD-H-25 resolved) ✅

### Web-3: Injection

- **SQL**: SQLAlchemy ORM throughout — no raw f-string queries found ✅
- The only `op.execute()` calls in migrations use literal DDL (`ALTER TYPE ... ADD VALUE`) with no user input ✅
- **User input → AI prompt**: `_sanitize_input()` strips API key patterns, email, and phone numbers. Direct injection text (e.g., "ignore all previous instructions") is NOT stripped from input before sending to the model — tracked as **M-12** (educator `local_context` field). Parent guide flow uses DB-sourced data only (lower risk). No new action; re-confirmed open.

### Web-4: Insecure Design

- Role model (EDUCATOR / PARENT / ADMIN / SUPER_ADMIN) enforced at both route and service layer ✅
- COPPA: parental consent flow pre-ChildProfile creation still missing — tracked as **GRC-01** ✅

### Web-5: Security Misconfiguration

| Control | Status |
|---------|--------|
| CORS origin allowlist | ✅ Explicit origins (localhost variants); wildcard only triggers localhost fallback |
| `CORS allow_methods=["*"]` | ⚠️ **New finding — see M-36** |
| `CORS allow_headers=["*"]` | ⚠️ **New finding — see M-36** |
| `/docs` and `/redoc` in production | ✅ Disabled (AWD-M-10 resolved) |
| CSP header | ⚠️ **AWD-H-35 open** — CSP removed by merge; `'unsafe-inline'` in M-35 also open |
| HSTS, X-Frame-Options, X-Content-Type-Options | ✅ Present in `SecurityHeadersMiddleware` |
| TrustedHostMiddleware | ⚠️ Disabled — tracked as **L-04** |

### Web-6: Vulnerable Components

- npm: 0 production vulnerabilities ✅
- pip: CI installs from pinned requirements.txt with security versions ✅
- Lockfile: `package-lock.json` committed ✅

### Web-7: Identification & Auth Failures

- Login response: returns generic `"Invalid email or password"` for both wrong-email and wrong-password — no account enumeration ✅
- Token refresh: same opaque error messages ✅
- Session timeout: JWT expiry enforced (`ExpiredSignatureError` caught) ✅

### Web-8: Software & Data Integrity

- `package-lock.json` committed; `requirements.txt` with pinned versions ✅

### Web-9: Logging & Monitoring

- Sentry SDK wired (AWD-H-01 resolved) ✅
- Structured logging via Python `logging` module ✅
- **⚠️ `console.log` statements in production frontend code** — see note below
- No PII found in backend log calls (names/emails not directly interpolated into log messages) ✅

**Frontend console.log findings** (code hygiene, not a new backlog item — covered by code-quality checklist):
- `apps/frontend/src/components/Footer.tsx:10` — `console.log('Subscribing email:', email)` logs user-entered email to browser console. This is PII-adjacent and should be removed.
- `apps/frontend/src/components/AIGenerationLoadingRealtime.tsx:146` — session metadata logged (low risk)
- `apps/frontend/src/services/websocket.ts:51,67,86,91,116` — connection state logs (informational, but should be removed or gated behind a debug flag for production)

The `Footer.tsx` email log is the most sensitive — it logs a value the user types before they submit, potentially capturing email addresses in browser dev tools. This should be removed in the next frontend cleanup pass.

### Web-10: SSRF

- No URL-fetching endpoints found (no proxy routes, no user-supplied URL consumption) ✅

---

## 5. OWASP LLM Top 10

### LLM-1: Prompt Injection

**Input side:**
- `PARENT_HELPER_PROMPT` and `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` use `.format(**prompt_params)`.
- **Parent guide flow**: all prompt parameters (`topic`, `subject`, `grade`, `country`, `curriculum`, `objectives`, `contents`) come from DB-sourced curriculum data (admin-controlled). No direct user free-text enters the prompt. ✅ Low risk.
- **Lesson resource flow**: `local_context` (educator-supplied free text) enters the prompt without instruction-pattern fencing — re-confirmed **M-12** (open).
- `_sanitize_input()` strips email, phone, and API key patterns before the prompt reaches the provider. Instruction-like strings (e.g., "ignore all previous instructions") are not stripped at input.

**Output side (improved since yesterday):**
- `_check_content_safety()` now checks AI output for injection markers, PII patterns, and harmful content before persisting — **AWD-M-23 resolved 2026-04-24** ✅

### LLM-2: Insecure Output Handling

- `generate_parent_guide` validates with `ParentGuideAIContent.model_validate_json()` (Pydantic) before DB write ✅
- `generate_lesson_resource` validates via `validate_output()` (JSON parse + required-field check) ✅
- Content-safety pass now in `validate_output` (M-23 resolved) ✅
- `_clean_and_repair()` strips markdown fences and trailing commas before JSON parsing ✅

### LLM-3: Training Data Poisoning
N/A — no fine-tuning.

### LLM-4: Model Denial of Service
- Guide generation: `@limiter.limit("5/minute")` per IP ✅
- Lesson plan generation: `@limiter.limit("5/minute")` and `@limiter.limit("3/minute")` on streaming ✅
- `AI_MAX_TOKENS` defaults to 8192 (configurable via env) ✅
- No per-user daily/monthly token budget in place — low-priority gap given current pre-revenue stage.

### LLM-5: Supply Chain
- `openai>=1.12.0` pinned in requirements.txt ✅
- `google-generativeai>=0.3.0` pinned ✅

### LLM-6: Sensitive Information Disclosure
- Child profile IDs, child names, parent emails — **not** included in any AI prompt ✅
- Prompt inputs use curriculum metadata only (grade, subject, topic, country, curriculum) ✅
- `_sanitize_input()` provides a second layer for any stray PII ✅

### LLM-7: Insecure Plugin Design
N/A — no tool/function calling or plugins exposed to the model.

### LLM-8: Excessive Agency
- AI output Pydantic-validated before persist (no side-effects on validation failure) ✅
- `validate_output()` and `_validate_parent_guide()` gate JSON structure before DB write ✅
- Content-safety scan gates harmful output (M-23 resolved) ✅

### LLM-9: Overreliance
(UX concern — AI-generated label on guide UI not audited here.)

### LLM-10: Model Theft
N/A — hosted OpenAI/Gemini API.

---

## 6. Summary

### New Issues Filed Today

| ID | Severity | Area | Summary |
|----|----------|------|---------|
| AWD-M-36 | Medium | Security / Config | CORS `allow_methods=["*"]` and `allow_headers=["*"]` — restrict to specific methods |

### Pre-existing Open Issues Re-confirmed

| ID | Severity | Area | Status |
|----|----------|------|--------|
| AWD-H-34 | High | Auth | `get_optional_current_user` not updated for HttpOnly cookie — browser clients treated as anonymous |
| AWD-H-35 | High | Security Headers | CSP header removed by AWD-M-10 merge — re-add and push |
| AWD-M-35 | Medium | Security Headers | CSP uses `'unsafe-inline'` for script-src and style-src |
| AWD-M-12 | Medium | AI / Prompt Injection | Educator `local_context` free-text flows into LLM prompt without instruction fencing |
| AWD-M-08 | Medium | Deps | `requirements.txt` uses `>=` minimums; exact pinning for reproducible local installs |
| AWD-L-04 | Low | Config | TrustedHostMiddleware disabled in production |
| AWD-L-05 | Low | Auth | `require_parent` wired at service layer but not at router level |

### Resolved Since Yesterday

| ID | Resolved | Summary |
|----|----------|---------|
| AWD-M-23 | 2026-04-24 | Content-safety pass (PII, injection markers, harmful words) added to `validate_output()` |
| AWD-M-09 | 2026-04-24 | Catalog GET endpoints confirmed using `Depends(get_current_user)` |
| AWD-M-10 | 2026-04-24 | `/docs` and `/redoc` disabled in production |
| AWD-M-11 | 2026-04-24 | CSP header added to `SecurityHeadersMiddleware` (note: regressed by H-35 merge conflict) |

### Passing Controls (key highlights)

| Control | Status |
|---------|--------|
| CI security job checks | ✅ All pass |
| No committed secrets or private docs | ✅ |
| npm production vulnerabilities | ✅ 0 |
| All backend routes require authentication | ✅ |
| Admin router uses router-level `require_admin` | ✅ |
| PARENT role enforced in children_service | ✅ |
| SQL injection — ORM throughout | ✅ |
| Bcrypt passwords, PyJWT 2.12.1 pinned | ✅ (CI/prod; local dev has older system packages) |
| CORS origin allowlist correct | ✅ |
| Rate limiting on auth + AI endpoints | ✅ |
| Auth tokens in HttpOnly cookies | ✅ |
| AI output Pydantic-validated before DB persist | ✅ |
| Content-safety pass on AI output (M-23) | ✅ Resolved |
| No PII or child data in AI prompts | ✅ |
| Account enumeration guard on login | ✅ |
| Sentry error monitoring wired | ✅ |

---

*Report generated by Security Agent · 2026-04-24 06:00*
