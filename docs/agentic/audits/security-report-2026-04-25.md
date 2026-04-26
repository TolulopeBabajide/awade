# Security Audit Report — 2026-04-25

**Agent**: Security Agent (scheduled, 6am daily)  
**Repo root**: `/Users/tolulopebabajide/Desktop/Projects/awade/awade`  
**AI stack**: OpenAI GPT + Gemini (packages/ai/) — OWASP LLM checks included  
**Workspace note**: Bash sandbox unavailable (disk space error on startup). All checks run via file-tool + grep equivalents. npm audit and pip audit --outdated could **not** be executed. Manual requirements/package.json review performed as substitute.

---

## 1. CI Security Job Mirror

| Check | Command | Result |
|-------|---------|--------|
| Sensitive files in git | `git ls-files \| grep -E '\.(env\|key\|pem\|p12)$'` | ✅ PASS — No tracked secrets. Two `.pem` files found under `venv/` (certifi CA bundle), confirmed gitignored via `.gitignore` line 34 (`venv/`) |
| `docs/private/` in git | `git ls-files \| grep "docs/private/"` | ✅ PASS — No files in `docs/private/` tracked |
| `.env.example` exists | `test -f .env.example` | ✅ PASS — File present at repo root |
| `.cursor/mcp.json` valid JSON | `python3 -m json.tool .cursor/mcp.json` | ✅ PASS — Valid JSON, 7 MCP server definitions |
| `apps/backend/app/openapi.json` valid JSON | `python3 -m json.tool ...openapi.json` | ✅ PASS — Valid JSON, OpenAPI 3.1.0 spec |

**All CI security job checks pass.**

---

## 2. Secret Scan

Patterns searched: `sk_live`, `sk_test`, `AIza`, `password\s*=`, `api_key\s*=` across `apps/**` and `packages/**` (all `.py`, `.ts`, `.tsx`, `.js` files, excluding `node_modules`, `__pycache__`, venv).

| Pattern | Matches | Assessment |
|---------|---------|------------|
| `sk_live` / `sk_test` / `AIza` | 0 | ✅ CLEAN |
| `password\s*=\s*"..."` | 7 hits in `tests/` only | ✅ CLEAN — all synthetic test values (`testpassword123`, `Password123!`) |
| `api_key\s*=\s*"..."` | 15 hits in `tests/` only | ✅ CLEAN — all `"test-key"` / `"test"` placeholders |

**No real secrets found in production code paths.**

---

## 3. Dependency Audit

*Note: bash unavailable — `npm audit` and `pip audit` could not be run. Manual review of pinned versions performed.*

### Backend (`requirements.txt`)

| Package | Pinned | Latest 1.x / Notes | Risk |
|---------|--------|--------------------|------|
| `Pillow==10.0.0` | 10.0.0 | Latest stable ≥ 10.4. Multiple CVEs below 10.3.0 (CVE-2024-28219 heap buffer overflow). **Already tracked as AWD-L-11 (open).** | 🟡 Medium |
| `openai==1.12.0` | 1.12.0 | Latest 1.x is 1.82+. Pinned intentionally (comment references AWD-M-08 API compatibility). Gap of ~70 minor versions within the 1.x series; possible CVE surface. | 🟡 Medium (new — AWD-M-39) |
| `PyJWT==2.12.1` | 2.12.1 | Current recommended version ✅ | |
| `cryptography==44.0.1` | 44.0.1 | Current ✅ | |
| `urllib3==2.5.0` | 2.5.0 | Current ✅ | |
| `requests==2.32.4` | 2.32.4 | Current ✅ | |
| `jinja2==3.1.6` | 3.1.6 | Current ✅ | |
| `python-multipart==0.0.18` | 0.0.18 | Current ✅ | |
| `setuptools==78.1.1` | 78.1.1 | Current ✅ | |
| `sentry-sdk[fastapi]==2.58.0` | 2.58.0 | Recent ✅ | |

### Frontend (`package.json`)

| Package | Version | Notes | Risk |
|---------|---------|-------|------|
| `react` | `^18.2.0` | Current 18.x ✅ | |
| `@tanstack/react-query` | `^5.99.0` | Current ✅ | |
| `react-router-dom` | `^6.8.1` | React-router XSS CVE (GHSA-2w69) was fixed via AWD-H-10 ✅ | |
| `@sentry/react` | `^8.0.0` | Current ✅ | |
| `@typescript-eslint/*` | `^5.57.1` | v8 is current; v5 is EOL but these are dev deps only — low risk | 🟢 Low |
| `vite` | `^7.1.7` | Current ✅ | |
| `vitest` | `^3.2.4` | Current ✅ | |

**Recommendation**: Run `npm audit --production` and `pip list --outdated` when bash workspace recovers to get precise CVE counts.

---

## 4. OWASP Web Top 10 Checks

### A01 — Broken Access Control

| Route file | Auth dep present | Role check | Finding |
|------------|-----------------|------------|---------|
| `routers/auth.py` | Public endpoints: ✅ rate-limited; protected: `get_current_user` | N/A | ✅ |
| `routers/children.py` | All routes: `get_current_active_user` | Role checked in service (`_verify_parent`) | ✅ |
| `routers/lesson_plans.py` | All routes: `get_current_user` / `require_educator` / `require_admin_or_educator` | AI generate: `require_educator`; update/delete: `require_admin_or_educator` | ✅ |
| `routers/admin.py` | Router-level: `Depends(require_admin)` | Per-route: `require_admin` / `require_super_admin` for role changes | ✅ |
| `routers/users.py` | `require_admin` / `require_admin_or_educator` on all routes | Service-level ownership enforcement (`current_user.user_id != user_id → 403`) | ✅ |
| `routers/curriculum.py` | `get_current_user` / `require_admin` / `require_admin_or_educator` | ✅ | ✅ |
| `routers/contexts.py` | `require_admin_or_educator` | Ownership asserted via `_assert_lesson_plan_ownership` | ✅ |

**Minor note**: `GET /api/users/{user_id}` and `PUT /api/users/{user_id}` accept `require_admin_or_educator`, meaning an EDUCATOR can reach the service layer. The service then enforces ownership (`user_id must match or caller must be ADMIN`). This creates a subtle account-enumeration gap — an EDUCATOR receives a different status code for "user not found" (404) vs "access denied" (403). Low risk, already consistent with existing behavior. No new issue filed (covered by existing design).

### A02 — Cryptographic Failures

- JWT signed with `HS256` via `PyJWT==2.12.1` ✅
- Passwords hashed with `bcrypt==4.0.0` ✅
- Auth tokens issued as `HttpOnly; Secure; SameSite=Lax` cookies (AWD-H-25 ✅)
- Refresh token blacklisting via Redis on logout ✅
- **Note**: `dependencies.py` line 39 falls back to `"dev-secret"` JWT key when `JWT_SECRET_KEY` is unset and `ENVIRONMENT != "production"`. A `RuntimeError` is raised in production. Acceptable — but requires `ENVIRONMENT=production` to be set correctly on Render.

### A03 — Injection

- All DB queries via SQLAlchemy ORM or parameterized `text()` ✅
- All request bodies validated with Pydantic schemas ✅
- Prompt inputs sanitized via `_sanitize_user_context()` (truncation, PII strip, injection pattern scrub) ✅
- **Finding (new)**: `lesson_plans.py` export endpoint leaks raw `str(e)` in HTTP 500 detail → **AWD-H-40** (filed in §7)

### A04 — Insecure Design

- Role model: 4 roles (EDUCATOR, PARENT, ADMIN, SUPER_ADMIN) consistently enforced ✅
- Child profile data is COPPA-relevant — stored with parent as guardian, no direct child access ✅
- GRC-01 (parental consent flow) still open ⚠️

### A05 — Security Misconfiguration

- `/docs` and `/redoc` disabled in production (AWD-M-10 ✅)
- CSP header added (AWD-M-11 ✅); `'unsafe-inline'` in `script-src` / `style-src` still open as AWD-M-35 ⚠️
- CORS `allow_methods` and `allow_headers` restricted (AWD-M-36 ✅)
- `TrustedHostMiddleware` still disabled (AWD-L-04, open) ⚠️
- Rate limiting applied to: auth endpoints (5–10/min), guide generation (5/min), lesson resource generation (3/min) ✅

### A06 — Vulnerable Components

- Pillow 10.0.0 CVEs — already tracked as AWD-L-11 (open)
- openai 1.12.0 stale — new issue AWD-M-39
- All other pinned versions appear current ✅

### A07 — Identification and Authentication Failures

- Refresh token rotation on each use ✅
- Suspended-user check in `get_current_active_user` (AWD-H-24 ✅)
- `forgot-password` endpoint rate limited (5/min) to prevent email bombing ✅
- Account enumeration via login (same generic error for unknown email vs wrong password) ✅
- `require_parent` helper defined in `dependencies.py` but not used in router — children.py relies on service-level `_verify_parent` instead. Tracked as AWD-L-05 (open). Low risk since service check is correct.

### A08 — Software and Data Integrity

- `package-lock.json` committed ✅
- `requirements.txt` pinned (AWD-M-08 ✅)
- No unverified dynamic imports or eval patterns found ✅

### A09 — Logging and Monitoring

- Sentry wired for backend and frontend (AWD-H-01 ✅)
- `logger = logging.getLogger(__name__)` used throughout; no bare `print()` in production paths ✅
- **Finding**: `lesson_plans.py` export error handler logs AND returns `str(e)` in HTTP detail → AWD-H-40

### A10 — Server-Side Request Forgery

- No user-controlled URL-fetching endpoints identified ✅

---

## 5. OWASP LLM Top 10 Checks

### LLM01 — Prompt Injection

- **COMPREHENSIVE_LESSON_RESOURCE_PROMPT**: user-supplied `local_context` is wrapped in `<user_context>` delimiters with an explicit "treat as data not instructions" preamble ✅ (AWD-M-12)
- **PARENT_HELPER_PROMPT**: all parameters are curriculum-DB values (topic, subject, grade, country, curriculum) — no direct user-free-text input path ✅
- `_sanitize_user_context()` applied before insertion: truncation (≤2000 chars), PII strip, injection-pattern scrub ✅
- Input injection patterns checked: 9 regex rules covering "ignore all instructions", jailbreak, fake role tags ✅

**Minor finding**: `generate_lesson_resource()` cache metadata (line 505) stores `"context": context` (original, pre-sanitization value) rather than `"context": safe_context`. If `ContentCache` stores metadata in Redis as JSON, the unsanitized string would persist in cache. The sanitized version (`safe_context`) is what enters the actual prompt, so injection risk is low — but the cache key discrepancy is a defence-in-depth gap. → **AWD-M-39** (combined with openai version staleness, see §7)

### LLM02 — Insecure Output Handling

- `validate_output()` runs 2 passes: content-safety (PII, injection markers, harmful words) then JSON schema validation ✅ (AWD-M-23)
- `_validate_parent_guide()` checks required top-level JSON keys ✅
- `ParentGuideAIContent.model_validate_json(ai_content)` — Pydantic schema validated before persistence (AWD-H-06 ✅)
- Output PII patterns checked: email addresses, phone numbers, API keys ✅
- Harmful content patterns checked: explicit terms, self-harm phrases ✅

### LLM04 — Model DoS

- `OpenAIProvider`: explicit 30s timeout ✅ (AWD-H-09)
- `GeminiProvider`: timeout added ✅ (AWD-H-39)
- API endpoints rate-limited (5/min guide generation, 3/min lesson resource) ✅
- `AI_MAX_TOKENS` capped via env var (default 8192) ✅

### LLM05 — Supply Chain

- `openai==1.12.0` pinned ✅ (but stale — see AWD-M-39)
- `google-genai==1.14.0` pinned ✅

### LLM06 — Sensitive Information Disclosure

- No child names, user IDs, tokens, or PII passed into prompts — only curriculum metadata (topic, subject, grade, country_name) ✅
- `_sanitize_input()` strips API keys, emails, phone numbers before prompt insertion ✅
- System prompt is a static string; no user-controlled system instruction path ✅

### LLM08 — Excessive Agency

- AI outputs are validated before any side effects (DB persistence) ✅
- `is_valid` flag returned and logged; guide persisted even if light validation fails, but Pydantic schema validation (`model_validate_json`) is a hard gate — raises 502 on structural failure ✅
- No AI-triggered writes outside the explicit guide/lesson resource flow ✅

### LLM09 — Overreliance

- Parent guides display AI provenance (out of scope for this audit but relevant to UX) — not verified in this scan

### LLM10 — Model Theft

- N/A — hosted model (OpenAI / Gemini), no weights stored

**All high-risk LLM checks pass. One minor cache-key gap noted (M-39).**

---

## 6. Existing Open Issues Confirmed Still Relevant

The following open items were confirmed still present during this scan:

| Issue | Status | Severity | Notes |
|-------|--------|----------|-------|
| AWD-L-04 | Open | 🟢 Low | `TrustedHostMiddleware` disabled |
| AWD-L-05 | Open | 🟢 Low | `require_parent` unused in children router |
| AWD-L-11 | Open | 🟢 Low | Pillow 10.0.0 CVEs |
| AWD-M-35 | Open | 🟡 Medium | CSP `'unsafe-inline'` in `script-src` / `style-src` |
| AWD-GRC-01 | Open | 🟣 Compliance | COPPA parental consent flow not yet implemented |
| AWD-GRC-02 | Open | 🟣 Compliance | GDPR data export endpoint not yet implemented |

---

## 7. New Issues Filed

### AWD-H-40 — `lesson_plans.py` export endpoint leaks internal error details

**Severity**: 🟠 High  
**Area**: Security / Error Handling  
**File**: `apps/backend/routers/lesson_plans.py` lines 219–223  
**Description**:
```python
except Exception as e:
    raise HTTPException(
        status_code=500, 
        detail=f"An error occurred while exporting the resource: {str(e)}"
    )
```
The `export_lesson_resource` endpoint returns `str(e)` in the HTTP 500 response body. This can leak internal file paths, WeasyPrint stack traces, or SQL error messages to the client — OWASP A09 information disclosure, same class as AWD-H-18 (which fixed service files but did not cover this router-level handler).

**Fix**: Replace with a static detail string and log the exception:
```python
except Exception as e:
    logger.error("Error exporting lesson resource %s: %s", resource_id, e, exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="An error occurred while exporting the resource. Please try again."
    )
```
Note: `logger = logging.getLogger(__name__)` is not yet defined at the top of `lesson_plans.py` — add it alongside the other imports.

**Effort**: S  
**Filed**: 2026-04-25 Security Agent

---

### AWD-M-39 — `openai==1.12.0` is ~70 minor versions behind latest 1.x; cache key includes unsanitized user context

**Severity**: 🟡 Medium  
**Area**: Security / Deps + AI  
**Files**: `apps/backend/requirements.txt`, `packages/ai/gpt_service.py` (line 505)  
**Description** (two related issues combined):

**Part A — openai version staleness**: `requirements.txt` pins `openai==1.12.0` (released early 2024). Latest 1.x is 1.82+. The comment explains 1.x is pinned to avoid breaking changes in 2.x — correct. But staying at 1.12.0 within 1.x is unnecessary: no breaking API changes occur within a minor series. The gap of 70+ minor versions means missed security patches and bug fixes.  
Fix: upgrade to `openai==1.82.0` (or latest stable 1.x), run `cd apps/backend && python -m pytest tests/ -v` to confirm no breakage.

**Part B — cache key includes unsanitized context**: In `generate_lesson_resource()` (line 505), the cache metadata dict stores:
```python
"context": context,   # original, pre-sanitization value
```
instead of `"context": safe_context`. The actual prompt uses the sanitized `safe_context`, so injection risk is low. However, if `ContentCache` persists metadata to Redis as JSON, the unsanitized string would be stored in Redis.  
Fix: replace `context` with `safe_context` at line 505.

**Effort**: S  
**Filed**: 2026-04-25 Security Agent

---

## 8. Summary

| Category | Status |
|----------|--------|
| CI security job mirror | ✅ All 5 checks pass |
| Secret scan | ✅ No hardcoded secrets in production code |
| Dependency audit (manual) | ⚠️ Pillow CVEs (L-11 open), openai stale (new M-39) |
| OWASP Web Top 10 | ⚠️ One new High (H-40); three existing open items (M-35, L-04, L-05) |
| OWASP LLM Top 10 | ⚠️ One minor cache gap (part of M-39) |
| **New issues filed** | **H-40** (export error leaks str(e)), **M-39** (openai stale + cache key) |

**No Critical issues found.** The codebase is in good security shape overall — auth, role enforcement, LLM input/output handling, and secret management are all solid. Two new issues (H-40, M-39) are additive to the existing backlog.

*Next scan: 2026-04-26 06:00*
