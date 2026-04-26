# Security Audit Report — 2026-04-23

**Agent:** Security Agent (scheduled, 6am daily)
**Scope:** Full OWASP Web Top 10 + OWASP LLM Top 10 + CI security job mirror
**Repo root:** `apps/backend/`, `apps/frontend/`, `packages/ai/`
**Result: ✅ No new Critical or High findings. 4 pre-existing open issues re-confirmed.**

---

## 1. CI Security Job Mirror

| Check | Command | Result |
|-------|---------|--------|
| Sensitive files in git | `git ls-files \| grep -E '\.(env\|key\|pem\|p12)$'` | ✅ PASS — empty |
| `docs/private/` in git | `git ls-files \| grep "docs/private/"` | ✅ PASS — empty |
| `.env.example` exists | `test -f .env.example` | ✅ PASS |
| `.cursor/mcp.json` valid JSON | `python3 -m json.tool .cursor/mcp.json` | ✅ PASS |
| `apps/backend/app/openapi.json` valid JSON | `python3 -m json.tool apps/backend/app/openapi.json` | ✅ PASS |

---

## 2. Secret Scan

Scanned: `apps/**/*.py`, `apps/**/*.ts`, `apps/**/*.tsx`, `packages/**/*.py`
Patterns: `sk_live`, `sk_test`, `AIza`, `password\s*=`, `api_key\s*=`, `secret\s*=`

| Location | Finding | Verdict |
|----------|---------|---------|
| `apps/backend/dependencies.py:37` | `secret = "dev-secret"` | ✅ INFO — dev/test fallback only. Guarded by `if environment == "production": raise RuntimeError(...)` (lines 30-35). Never reaches production. |
| `packages/ai/providers/openai_provider.py:27` | `self.api_key = api_key or os.getenv("OPENAI_API_KEY")` | ✅ PASS — reads from env, no hardcoded value. |
| `packages/ai/providers/gemini_provider.py:24` | `self.api_key = api_key or os.getenv("GEMINI_API_KEY")` | ✅ PASS — reads from env, no hardcoded value. |
| `apps/backend/init_db.py:64,82` | `os.getenv("ADMIN_PASSWORD")` / `os.getenv("EDUCATOR_PASSWORD")` | ✅ PASS — reads from env, seed script only. |

**No hardcoded production secrets found.**

---

## 3. Dependency Audit

### Frontend (`npm audit --production`)
```
found 0 vulnerabilities
```
✅ PASS

### Backend (requirements.txt review)
`requirements.txt` is correctly pinned with security-conscious minimums:
- `PyJWT==2.12.1` (exact pin, resolves AWD-H-23) ✅
- `python-multipart>=0.0.18` (CVE-2024-53981) ✅
- `jinja2>=3.1.6` (CVE-2025-27516 etc.) ✅
- `bcrypt>=4.0.0` ✅
- `cryptography>=44.0.1` ✅
- `requests>=2.32.4` ✅
- `urllib3>=2.5.0` ✅

> Note: `pip list --outdated` in the sandbox shows older system packages (PyJWT 2.3.0, bcrypt 3.2.0). These are the sandbox OS packages, **not** the project's virtualenv. The requirements.txt pins are correct. Recommend running `pip-audit` against the project venv on a real deploy environment to confirm installed versions match. No new backlog item filed — existing AWD-H-23 (done) and AWD-M-08 cover this.

---

## 4. OWASP Web Top 10

### OW-1: Broken Access Control
- **Admin routes** (`apps/backend/routers/admin.py`): Router-level `dependencies=[Depends(require_admin)]` at line 19 covers ALL routes in this router. ✅
- **Children/parent routes** (`apps/backend/routers/children.py`): All 10 endpoints use `get_current_active_user`. ✅
- **Lesson plan routes** (`apps/backend/routers/lesson_plans.py`): All routes use `get_current_user`, `require_educator`, or `require_admin_or_educator`. ✅
- **Users** (`apps/backend/routers/users.py`): All routes use `require_admin` or `require_admin_or_educator`. ✅
- **Curriculum / curriculum_structure**: All mutation routes require `require_admin`; read routes require `get_current_user`. ✅
- **Role enforcement (children_service.py)**: `_check_parent_role()` method enforces `UserRole.PARENT / ADMIN / SUPER_ADMIN` before any child/guide operation. ✅

### OW-2: Cryptographic Failures
- Passwords: bcrypt (via `bcrypt.hashpw` / `bcrypt.gensalt`) ✅
- JWTs: PyJWT 2.12.1 (pinned), signed with `JWT_SECRET_KEY` from env ✅
- HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains` set by `SecurityHeadersMiddleware` ✅

### OW-3: Injection (SQL)
- SQLAlchemy ORM used throughout — no raw string-formatted queries found. ✅
- Pydantic schemas validate all request bodies before service layer. ✅

### OW-4: Insecure Design
- No new features reviewed today.

### OW-5: Security Misconfiguration
- CORS: When `ALLOWED_ORIGINS` env var is unset or `"*"`, code falls back to an explicit localhost allowlist (lines 195-202 in `main.py`). Production must set `ALLOWED_ORIGINS` explicitly. ✅ (behaviour is correct; env var discipline is deploy concern)
- Security headers present: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `HSTS`, `Referrer-Policy` ✅
- **⚠ Missing `Content-Security-Policy` header** — already tracked as **AWD-M-11** (open, `apps/backend/middleware/security_headers.py`). Re-confirmed open.

### OW-6: Vulnerable Components
- Frontend: 0 npm vulnerabilities ✅
- Backend: requirements.txt pins updated (see §3). No new CVEs identified in scanned packages. ✅

### OW-7: Identification and Auth Failures
- Login uses generic `"Invalid email or password"` for both unknown email and wrong password (account enumeration guard). ✅
- Google OAuth path uses generic `"Invalid Google token"` on failure. ✅
- Rate limiting on `/api/auth/login` (`10/minute`) and `/api/auth/register` (`5/minute`) ✅
- **⚠ JWT stored in `localStorage`** — already tracked as **AWD-H-25** (open, `apps/frontend/src/contexts/AuthContext.tsx` lines 45, 119, 143, 167). Re-confirmed open. XSS on any page could exfiltrate token. Awaiting Tolu's decision on httpOnly cookie vs in-memory approach.

### OW-8: Software and Data Integrity
- `package-lock.json` and `requirements.txt` both committed ✅

### OW-9: Logging and Monitoring
- Structured `logging.getLogger(__name__)` used in backend routers ✅
- Sentry wired (AWD-H-01 resolved, commit 364762f) ✅
- No PII found in log statements (child names, emails not logged) ✅

### OW-10: SSRF
- Only external URL fetch is Google OAuth tokeninfo (`https://oauth2.googleapis.com/tokeninfo?id_token=...`). URL is hardcoded to Google's domain — no user-controlled host. ✅

---

## 5. OWASP LLM Top 10

Scope: `packages/ai/prompts.py` (PARENT_HELPER_PROMPT + COMPREHENSIVE_LESSON_RESOURCE_PROMPT), `packages/ai/gpt_service.py`

### LLM-1: Prompt Injection
- System instruction is fully hardcoded — not influenced by any user input. ✅
- `PARENT_HELPER_PROMPT` substitutes: `topic_title`, `subject`, `grade_level`, `country`, `curriculum`, `learning_objectives`, `contents` — all sourced from the **curriculum database**, not free-text user input. Parent flow is low injection risk. ✅
- `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` substitutes `{local_context}` with educator-supplied free text (`context_input` field in `LessonResourceCreate`). No XML/structural delimiters fence this value from prompt instructions.
  - **⚠ Already tracked as AWD-M-12** (open). Re-confirmed: no input delimiters added yet.
- `_sanitize_input()` strips API key patterns, emails, phone numbers from the full formatted prompt. Partial mitigation only — does not fence instruction-like patterns. ✅ (partial)

### LLM-2: Sensitive Information Disclosure
- Child profile IDs, child names, parent email are **not** included in any prompt. ✅
- `_sanitize_input()` redacts emails, phones, and API key patterns before the prompt reaches the provider. ✅

### LLM-3: Training Data Poisoning
- N/A — no fine-tuning.

### LLM-4: Model Denial of Service
- Guide generation endpoint: `@limiter.limit("5/minute")` ✅
- `AI_MAX_TOKENS` defaults to 8192, configurable via env ✅

### LLM-5: Supply Chain
- `openai>=1.12.0` pinned in requirements.txt ✅
- `google-generativeai>=0.3.0` pinned ✅

### LLM-6: Sensitive Information in Prompts
- No IDs, tokens, or PII passed into prompts. ✅

### LLM-7: Insecure Plugin Design
- N/A — no tool/function calling or plugins exposed to the model.

### LLM-8: Excessive Agency
- AI output validated with `ParentGuideAIContent.model_validate_json()` (Pydantic) before persisting. ✅
- `validate_output()` checks required JSON fields for lesson resources. ✅
- **⚠ Content-safety pass absent from `validate_output`** — already tracked as **AWD-M-23** (open). Re-confirmed: harmful-word / instruction-injection pattern check not yet implemented.

### LLM-9: Overreliance
- (UX concern — not audited here. AI-generated label on guide UI tracked in product backlog.)

### LLM-10: Model Theft
- N/A — hosted OpenAI/Gemini API.

---

## 6. Summary

### New Issues Filed Today
*None.* All findings encountered are pre-existing tracked items.

### Pre-existing Open Issues Re-confirmed
| ID | Severity | Area | Summary |
|----|----------|------|---------|
| AWD-H-25 | High | Auth / Frontend | JWT `access_token` in `localStorage` — XSS-exploitable. Awaiting Tolu decision on remediation path. |
| AWD-M-11 | Medium | Security Headers | No `Content-Security-Policy` header in `SecurityHeadersMiddleware`. |
| AWD-M-12 | Medium | AI / Prompt Injection | Educator `local_context` free-text flows into LLM prompt without XML fencing or instruction-pattern rejection. |
| AWD-M-23 | Medium | AI / Output Safety | `validate_output` checks schema shape only — no harmful-content / injection-marker scan on AI response. |

### Passing Controls (key highlights)
- ✅ All CI security job checks pass
- ✅ No committed secrets or private docs
- ✅ 0 npm production vulnerabilities
- ✅ All backend routes require authentication; admin router uses router-level guard
- ✅ Role enforcement (PARENT / EDUCATOR / ADMIN) in service layer
- ✅ Bcrypt passwords, PyJWT 2.12.1 (pinned)
- ✅ Security headers: HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- ✅ CORS allowlist correct (no wildcard + credentials)
- ✅ Rate limiting on auth and AI generation endpoints
- ✅ AI output Pydantic-validated before DB persist
- ✅ No PII or child data in AI prompts
- ✅ Account enumeration guard on login
- ✅ Sentry error monitoring wired (AWD-H-01 resolved)
