# Security Audit Report — 2026-04-22

**Agent:** Security Agent (automated daily scan, 6am)  
**Repo root:** `apps/backend/`, `apps/frontend/`, `packages/ai/`  
**AI stack:** OpenAI GPT (OWASP LLM checks included)  
**Status:** 4 High findings, 2 Medium findings, all CI checks pass

---

## 1. CI Security Job Mirror

| Check | Result | Notes |
|-------|--------|-------|
| Sensitive files in git (`*.env`, `*.key`, `*.pem`, `*.p12`) | ✅ PASS | No sensitive files committed |
| `docs/private/` in git | ✅ PASS | Clean |
| `.env.example` exists | ✅ PASS | Present at repo root |
| `.cursor/mcp.json` valid JSON | ✅ PASS | |
| `apps/backend/app/openapi.json` valid JSON | ✅ PASS | |

---

## 2. Secret Scan

All matches in `apps/` and `packages/` are **legitimate**: all secrets are read from `os.getenv()`, not hardcoded. No actual secret values present. ✅

Notable entries reviewed:
- `redis_client.py` — `password=REDIS_PASSWORD` (env var)
- `init_db.py` — `ADMIN_PASSWORD`, `EDUCATOR_PASSWORD` (env vars with getpass fallback)
- `packages/ai/providers/openai_provider.py` — `os.getenv("OPENAI_API_KEY")` ✅
- `packages/ai/providers/gemini_provider.py` — `os.getenv("GEMINI_API_KEY")` ✅

---

## 3. Dependency Audit

### 3a. Frontend (npm audit --production)

**3 HIGH severity vulnerabilities found → AWD-H-23**

| Package | Installed | Severity | Advisory |
|---------|-----------|----------|---------|
| `@remix-run/router` | ≤1.23.1 | HIGH | XSS via Open Redirects — [GHSA-2w69-qvjg-hvjx](https://github.com/advisories/GHSA-2w69-qvjg-hvjx) |
| `react-router` | 6.0.0–6.30.2 | HIGH | Depends on vulnerable `@remix-run/router` |
| `react-router-dom` | 6.0.0–6.30.2 | HIGH | Depends on vulnerable `@remix-run/router` |

Fix: `npm audit fix` in `apps/frontend/`.

### 3b. Backend (pip — security-relevant packages)

| Package | Installed | Latest | Risk |
|---------|-----------|--------|------|
| `PyJWT` | 2.3.0 | 2.12.1 | HIGH — JWT library, major version gap (2.3 → 2.12). Covers multiple CVE windows. Requirements.txt uses `>=2.0.0` (unpinned). → AWD-H-24 |
| `cryptography` | 46.0.6 | 46.0.7 | LOW — Minor patch, no known CVEs |

---

## 4. OWASP Web Top 10

### 4a. Broken Access Control
- ✅ All routers use `Depends(get_current_active_user)` or role-specific deps
- ✅ Admin router uses router-level `dependencies=[Depends(require_admin)]`
- ✅ Role deps properly distinguish `EDUCATOR`, `PARENT`, `ADMIN`, `SUPER_ADMIN`
- ❌ **Suspended users bypass auth check → AWD-H-25**
  - `get_current_active_user` in `apps/backend/dependencies.py` (line 122) has a comment saying "Add any additional checks for user status here" but does NOT check `user.is_suspended`. A user suspended by an admin can still authenticate and call all endpoints.

### 4b. Cryptographic Failures
- ✅ `bcrypt` used for password hashing (`init_db.py`)
- ✅ JWT tokens signed with `SECRET_KEY` from env (production guard raises `RuntimeError` if unset)
- ✅ HS256 algorithm hardcoded (consistent; algorithm confusion attacks mitigated by explicit `algorithms=[algorithm]` in `jwt.decode`)
- ⚠️ PyJWT 2.3.0 is far behind latest — see AWD-H-24

### 4c. Injection
- ✅ No raw SQL — all queries via SQLAlchemy ORM
- ✅ Pydantic schemas on all request bodies
- ✅ No f-string SQL construction found
- ✅ No `dangerouslySetInnerHTML` in frontend

### 4d. Security Misconfiguration
- ✅ CORS origins: correctly defaults to explicit localhost list when env var is `*` (no wildcard in prod)
- ⚠️ `allow_methods=["*"]` and `allow_headers=["*"]` in CORS — slightly permissive but low risk given origin allowlist → M-22
- ✅ Rate limiting on all auth endpoints (5–20/min) and AI endpoints (3–5/min)
- ✅ No `print()` statements in production paths

### 4e. Auth Failures
- ❌ JWT stored in `localStorage` → AWD-H-26  
  `apps/frontend/src/contexts/AuthContext.tsx` stores `access_token` and `user_data` in `localStorage`. Any XSS vulnerability (including the react-router one in AWD-H-23) can exfiltrate these tokens.
- ✅ No account enumeration detected in auth responses

### 4f. Logging & Monitoring
- ✅ Structured `logging` module used throughout backend
- ✅ Admin audit log (`AdminAuditLog`) captures role changes, moderation actions, template changes
- ℹ️ Sentry not yet connected (tracked as existing H-01)

---

## 5. OWASP LLM Top 10

### LLM-01: Prompt Injection
- ⚠️ **`context_input` (lesson resource generation) is free-form user text — AWD-M-22**
  - In `apps/backend/routers/lesson_plans.py`, `LessonResourceCreate.context_input` is `Optional[str]` from the request body
  - This flows into `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` as `{local_context}` without injection-specific sanitization
  - `_sanitize_input()` in `gpt_service.py` only strips API keys/emails/phones — it does not defend against injected instructions
  - **Mitigating factor:** Rate-limited to 3/minute; requires EDUCATOR role; AI output is JSON-validated before persistence
- ✅ Parent guide: topic/subject/country data comes from the database (validated `topic_id` integer → DB lookup), not free-form user input. Injection risk is low.

### LLM-02: Insecure Output Handling
- ✅ `validate_output()` checks JSON structure before persisting lesson resources
- ✅ `_validate_parent_guide()` checks required top-level keys before persisting guides
- ✅ `_clean_and_repair()` strips markdown fences, extracts JSON payload
- ✅ Fallback to mock response on parse failure (no raw LLM output stored)

### LLM-04: Model DoS / Unbounded Consumption
- ✅ Rate limiting: 5/min on lesson plan generation, 3/min on resource generation
- ✅ `AI_MAX_TOKENS` configurable via env var (defaults to 8192)
- ✅ Response caching via `ContentCache` to avoid redundant API calls

### LLM-05: Supply Chain
- ⚠️ `openai>=1.12.0` uses `>=` (unpinned floor) — combined with PyJWT concern in H-24, a pin pass is recommended → M-23
- ⚠️ `google-generativeai>=0.3.0` also unpinned — Gemini provider is present in codebase (`packages/ai/providers/gemini_provider.py`) even if not the default

### LLM-06: Sensitive Information Disclosure
- ✅ No user PII (emails, names, IDs) embedded in prompts
- ✅ Child profile IDs are not passed to the AI; only topic title, grade, subject, country from DB
- ✅ `_sanitize_input()` removes incidentally included emails/phones from context fields

### LLM-08: Excessive Agency
- ✅ AI output is validated before any DB write
- ✅ `is_valid` flag returned and logged when validation fails; stored guide is only created on success

### LLM-09: Overreliance
- ℹ️ No UI indicator yet that content is AI-generated (user-facing) — not a security issue but a GRC/trust concern; flagged for product backlog

---

## 6. Summary of Issues

### Already tracked in backlog (confirmed still open)
| ID | Severity | Title | Status |
|----|----------|-------|--------|
| AWD-H-10 | High | react-router-dom XSS via Open Redirects (GHSA-2w69-qvjg-hvjx) — `npm audit fix` ready | Still open |
| AWD-M-08 | Medium | `requirements.txt` uses `>=` minimums — pin exact versions | Still open |
| AWD-M-12 | Medium | AI prompt sanitization — **UPDATE**: `context_input` in lesson resource generation is an active injection surface (educator free text → `{local_context}` in prompt), not merely preventive | Still open; scope expanded |

### New issues filed today
| ID | Severity | Title | File(s) |
|----|----------|-------|---------|
| AWD-H-23 | High | PyJWT 2.3.0 severely outdated (latest 2.12.1) — large CVE window for JWT signing library | `apps/backend/requirements.txt` |
| AWD-H-24 | High | Suspended users not blocked — `get_current_active_user` missing `is_suspended` check | `apps/backend/dependencies.py` |
| AWD-H-25 | High | JWT access token stored in `localStorage` (XSS exfiltration risk) | `apps/frontend/src/contexts/AuthContext.tsx` |

---

## 7. Items Verified Clean (no new issues)

- No secrets hardcoded in source files ✅
- No `docs/private/` in git ✅
- All CI security file checks pass ✅
- Admin routes protected by router-level dependency ✅
- Role-gated routes properly checked ✅
- No SQL injection vectors found ✅
- No `dangerouslySetInnerHTML` in frontend ✅
- CORS origin allowlist correctly applied ✅
- Rate limiting on auth + AI endpoints ✅
- Structured logging used; no bare `print()` in prod paths ✅
- Parent guide prompt injection risk low (data from DB, not free text) ✅
- AI output validated before DB persistence ✅
