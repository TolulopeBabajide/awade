# Security Audit Report — 2026-04-21

**Run:** Automated scheduled task (security-agent, 06:00 UTC)
**Scope:** CI security mirror + secret scan + dependency audit + OWASP Web Top 10 + OWASP LLM Top 10
**Repo root:** `/Users/tolulopebabajide/Desktop/Projects/awade/awade`
**AI stack:** OpenAI GPT (per `project-config.md` §2)
**Reference:** `.claude/rules/security.md`

> Supersedes the earlier draft from 2026-04-20 23:41 — that draft pre-dated today's scheduled run.

---

## Summary

| Severity | Count (this run) | Filed to backlog |
|---|---|---|
| Critical | 1 new | C-04 |
| High | 2 new + 1 existing recurring | H-12, H-13 (existing: H-10) |
| Medium | 1 informational | (no new IDs — covered by M-08, M-12) |
| Low / Info | 2 | (none filed) |

**Headline:** One new Critical: `apps/backend/routers/contexts.py` exposes 7 unauthenticated CRUD routes that also act as a prompt-injection sink for the lesson-resource AI generator. Filed as **C-04** immediately, per the non-negotiable in the task brief.

---

## 1. CI security mirror — `.github/workflows/ci.yml > security`

| Check | Result |
|---|---|
| `git ls-files \| grep -E '\.(env\|key\|pem\|p12)$'` | PASS — no sensitive files tracked |
| `git ls-files \| grep "docs/private/"` | PASS — no private docs tracked |
| `test -f .env.example` | PASS |
| `python -m json.tool .cursor/mcp.json` | PASS — valid JSON |
| `python -m json.tool apps/backend/app/openapi.json` | PASS — valid JSON |

All five CI security gates pass.

---

## 2. Secret scan

Custom grep across `apps/` + `packages/` for `sk_live`, `sk_test`, `AIza`, `password=`, `api_key=` (excluding `node_modules`, `__pycache__`, `test_`, `example`):

| Hit | Verdict |
|---|---|
| `apps/backend/redis_client.py:17` — `password=REDIS_PASSWORD` | OK — references env var, no literal |
| `apps/backend/init_db.py:64,82,87` — `os.getenv("ADMIN_PASSWORD")` / `EDUCATOR_PASSWORD` / `getpass.getpass(...)` | OK — env-var lookup with prompt fallback |
| `packages/ai/providers/openai_provider.py:22,27` — `os.getenv("OPENAI_API_KEY")` | OK |
| `packages/ai/providers/gemini_provider.py:24,29` — `os.getenv("GEMINI_API_KEY")` | OK |
| `packages/ai/gpt_service.py:72,74` — `OpenAIProvider(api_key=api_key)` / `GeminiProvider(api_key=api_key)` | OK — passthrough from env |

No hardcoded secrets. All five matches are env-var lookups.

---

## 3. Dependency audit

### Frontend — `npm audit` (apps/frontend)

```
{ info: 0, low: 0, moderate: 4, high: 9, critical: 0, total: 13 }
```

`npm audit --production` headline:
- `@remix-run/router <=1.23.1` → `react-router 6.0.0–6.30.2` → `react-router-dom 6.0.0-alpha.0–6.30.2`
- Advisory: GHSA-2w69-qvjg-hvjx (XSS via Open Redirects)
- Fix: `npm audit fix`

Already tracked as **H-10**. Severity counts have grown (yesterday's report noted 3 high; full audit including dev deps shows 9 high + 4 moderate today). No new criticals. **H-10 remains the right tracking issue** — not re-filed.

### Backend — `pip list --outdated`

`apps/backend/requirements.txt` already pins minimums for known CVE fixes (CVE-2024-53981, CVE-2025-27516, CVE-2024-47081, CVE-2025-50181, CVE-2024-12797, etc.). The sandbox `pip` reports system-package outdated rows that aren't representative of the project's pinned env. No new advisories observed against pinned packages this run. The looseness of `>=` minimums is already tracked as **M-08**.

---

## 4. OWASP Web Top 10

Methodology: walked every `@router.<method>(...)` decorator across `apps/backend/routers/*.py` and confirmed each route was guarded by one of: `get_current_user`, `get_current_active_user`, `require_admin`, `require_super_admin`, `require_educator`, `require_parent`, `require_admin_or_educator` (either as a `Depends(...)` parameter or as a router-level `dependencies=[...]`).

### A01 — Broken Access Control

🔴 **NEW CRITICAL — C-04 — `apps/backend/routers/contexts.py` is fully unauthenticated**

| Line | Route | Auth |
|---|---|---|
| 33 | POST `/api/contexts/` | NO AUTH |
| 42 | GET `/api/contexts/lesson-plan/{lesson_plan_id}` | NO AUTH |
| 51 | GET `/api/contexts/` | NO AUTH |
| 61 | GET `/api/contexts/{context_id}` | NO AUTH |
| 70 | PUT `/api/contexts/{context_id}` | NO AUTH |
| 80 | DELETE `/api/contexts/{context_id}` | NO AUTH |
| 89 | POST `/api/contexts/lesson-plan/{lesson_plan_id}/submit` | NO AUTH |

The router imports `get_current_user` and `require_admin_or_educator` (line 21) but never wires them into the router or any route. Any unauthenticated client can list, create, update, and delete every context in the system. Filed as **C-04** in `docs/agentic/backlog.md`.

🟠 **NEW HIGH — H-12 — `GET /api/users/{user_id}` lacks ownership check**

`routers/users.py` line 47 gates with `require_admin_or_educator`, but `UserService.get_user` does not verify that `current_user.user_id == user_id` for the EDUCATOR path. An authenticated educator can iterate user IDs and read PII (email, full name, role). The same service correctly enforces ownership in `update_user` and `get_user_profile`, so the fix is a 3-line consistency change. Filed as **H-12**.

All other routers verified properly guarded:
- `admin.py` — router-level `dependencies=[Depends(require_admin)]`
- `auth.py` — public routes are intentional (login/signup/google/refresh/logout/forgot/reset)
- `children.py` — every route uses `Depends(get_current_active_user)`
- `country.py`, `curriculum.py`, `subject.py`, `grade_level.py`, `curriculum_structure.py` — GETs use `get_current_user`, write methods use `require_admin`
- `lesson_plans.py` — uses `require_educator` on generate endpoints, `get_current_user` on reads, with rate limits
- `users.py` — see H-12 above; otherwise `require_admin` / `require_admin_or_educator`

### A02 — Cryptographic Failures

No regression. C-02 (JWT secret fallback) remains open and unchanged.

### A03 — Injection (SQL)

`grep -rEn 'text\(f"|execute\(f"|\.raw\(f"' apps/backend` → 0 hits. SQLAlchemy ORM only. Pass.

### A04 — Insecure Design

🟠 **NEW HIGH — H-13 — Auth endpoints missing rate limits**

Only `/login` (10/min) and `/signup` (5/min) carry `@limiter.limit(...)`. Missing on:
- `POST /auth/google` (line 53) — token-validation DoS
- `POST /auth/refresh` (line 138) — refresh-token brute force / DoS
- `POST /auth/forgot-password` (line 181) — email-bombing + user enumeration
- `POST /auth/reset-password` (line 189) — token brute force

Filed as **H-13**.

### A05 — Security Misconfiguration

CORS reviewed: `apps/backend/main.py` defaults to `localhost` dev origins; production reads `ALLOWED_ORIGINS` env var; `allow_credentials=True` with explicit origin list (no `*`). OK.

`/docs` and `/redoc` exposure in production already tracked as **M-10**.

### A06 — Vulnerable Components

See §3. H-10 is the open tracking issue.

### A07 — Identification & Auth Failures

Account enumeration on login already tracked as **H-05**. H-13 above adds rate-limiting gaps.

### A08 — Software & Data Integrity

`package-lock.json` and `requirements.txt` both committed. OK.

### A09 — Logging & Monitoring

`grep "logger\." apps/backend/services` filtered for `email|password|token|child` → 1 hit (`children_service.py:383` logs only `topic_id`, no PII). Pass.

`print()` audit found 6 calls in `apps/backend/worker.py` (production path):
```
worker.py:29,36,42,49,59,126,129
```
Code-quality rule §"Code Hygiene" says "no `print()` left in production paths." Informational — not severity-worthy on its own; consider rolling into a future code-hygiene sweep.

H-01 (Sentry wiring) remains open.

### A10 — SSRF

No URL-fetching endpoints introduced this cycle. Pass.

### Awade-specific frontend rule

`localStorage.setItem('access_token', ...)` confirmed in `apps/frontend/src/contexts/AuthContext.tsx` and 3 admin pages. The `.claude/rules/security.md` "Frontend" section forbids long-term token storage in localStorage. **Not re-filed** — this is an architectural rule the codebase has not yet adopted; flag for Tolu's roadmap rather than a new H this morning.

---

## 5. OWASP LLM Top 10  (AI_STACK = OpenAI GPT)

Files in scope: `packages/ai/prompts.py`, `packages/ai/gpt_service.py`, `packages/ai/providers/openai_provider.py`, `packages/ai/providers/gemini_provider.py`.

### LLM01 — Prompt Injection

Both `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` and `PARENT_HELPER_PROMPT` use `.format(**prompt_params)` with no delimiters around user-controlled fields. The fields (`topic`, `subject`, `grade_level`, `country`, `curriculum`, `learning_objectives`, `contents`, plus `local_context` for lesson resources) flow into the prompt as plain text.

Source-of-truth analysis:
- `topic`, `subject`, `grade_level`, `curriculum`, `country`, `learning_objectives`, `contents` originate from curriculum tables — write paths are admin-only (verified). Trust boundary: ADMIN.
- `Context.context_text` (lesson resources) → user-supplied via `POST /api/contexts/...` → **today, unauthenticated** (see C-04 above). **This is an active prompt-injection surface, not a theoretical one** — `services/lesson_plan_service.py:366-371` concatenates `ctx.context_text` directly into the AI prompt under a `"Stored Context:"` heading.

  C-04 closes both the access-control hole and the LLM01 surface in one fix; the existing **M-12** ("wrap user-supplied prompt fields in delimiters") then becomes the defense-in-depth follow-up.

`_sanitize_input()` scrubs API keys, emails, phone numbers — it does not escape prompt-injection markers (e.g. "ignore previous instructions"). Adequate for PII redaction; insufficient as injection defense. Already covered by **M-12**.

### LLM02 — Insecure Output Handling

`validate_output()` and `_validate_parent_guide()` do `json.loads()` + check required top-level keys. The required-key list for parent guides is shallower than the prompt's documented schema. Already tracked as **H-06**.

### LLM03 — Training Data Poisoning

N/A — no fine-tuning.

### LLM04 — Model DoS / Excessive Consumption

Rate limiting:
- `lesson_plans.py:/generate` — 5/min ✅
- `lesson_plans.py:/{lesson_id}/resources/generate` — 3/min ✅
- `children.py:/generate` parent guide — **no limit** — **H-07 (open)**

OpenAI client timeout missing — **H-09 (open)**.

### LLM05 — Supply Chain

`openai>=1.12.0` and `google-generativeai>=0.3.0` pinned in `requirements.txt`. Loose `>=` is **M-08**. No new vulnerabilities reported.

### LLM06 — Sensitive Information Disclosure

Reviewed `_make_api_call` and `prompt_metadata` construction in `gpt_service.py:generate_parent_guide`: metadata includes `topic`, `subject`, `grade`, `country`, `objectives` — all curriculum-derived. No child profile IDs, no user IDs, no tokens. Pass.

### LLM07 — Insecure Plugin Design

N/A.

### LLM08 — Excessive Agency

AI output is persisted only after `_validate_parent_guide()` returns True. Bookmark and other side effects require an explicit user action. Pass.

### LLM09 — Overreliance

Parent guides are clearly labelled AI-generated in the UI (per `apps/frontend/src/pages/GuideViewPage.tsx`). Pass.

### LLM10 — Model Theft

N/A.

---

## 6. New backlog entries filed this run

| ID | Severity | Title |
|---|---|---|
| C-04 | Critical | `contexts.py` 7 routes unauthenticated; doubles as prompt-injection sink for lesson-resource AI |
| H-12 | High | `GET /api/users/{user_id}` lacks ownership check (any educator can read any user) |
| H-13 | High | Rate limits missing on `/auth/google`, `/auth/refresh`, `/auth/forgot-password`, `/auth/reset-password` |

`docs/agentic/backlog.md` "Last updated" header bumped to `2026-04-21 06:00`.

---

## 7. Status of previously-open security findings (no change this run)

`C-01`, `C-02`, `C-03`, `H-01`, `H-05`, `H-06`, `H-07`, `H-08`, `H-09`, `H-10`, `M-08`, `M-09`, `M-10`, `M-11`, `M-12`, `L-04` — all still open. Re-verify after next sprint; no new evidence today changes their priority.

---

## 8. Next-run notes

- Re-run will re-audit `routers/contexts.py` once C-04 is fixed; expect the prompt-injection surface to disappear at the same time.
- Add a check that `localStorage.setItem('access_token', ...)` count does not increase (architectural drift sentinel).
- Consider adding a script-level check that every router file's `dependencies=[...]` or per-route `Depends(...)` uses one of the known guard helpers — would have caught C-04 immediately.
