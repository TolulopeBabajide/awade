# Awade — Manual To-Do

> Things the agent cannot do autonomously (no GitHub credentials, no secrets access, requires your judgment).
> Agent updates this file whenever a task needs Tolu's hands. Check it before and after each dev session.
> Last updated: 2026-04-25 (Dev Agent — AWD-M-21 commits c83bee8 + f97e86b added)

---

## 🔴 Urgent / Blocking

### Push commits to GitHub (triggers CI)
The sandbox has no HTTPS credentials for GitHub. All commits listed below are on your local `develop` branch and need to be pushed:

```bash
git push origin develop
```

This single push covers all commits — they are already merged to `develop` in the correct order. CI will run the full pipeline on all of them.

**Commits waiting to ship (oldest → newest):**
| Commit | Issue | Description |
|--------|-------|-------------|
| `91d758e` | H-24 | Security: suspended user auth bypass fix |
| `8628ab7` | H-18 | Security: remove str(e) from HTTPException details |
| `c38dcd4` | H-27 | Testing: fix `__new__` bypass in test_contexts_router |
| `442990d` | H-28 | Testing: fix ExceptionDetailSanitization test payloads |
| `3ce06c4` | H-29 | Testing: rate-limiter reset fixture between tests |
| `b9a089f` | H-23 | Security: pin PyJWT to 2.12.1 |
| `991c287` | H-11 | Testing: pytest coverage for children router + service |
| `5367714` | H-19 | Parents: dedicated /children page |
| `79ff2f6` | H-30 | Security: ParentRoute role guard for parent-only routes |
| `20f83ca` | H-31 | Testing: vitest coverage for ChildrenPage.tsx |
| `8b4ba55` | H-20 | Parents: parent onboarding flow on first signup |
| `364762f` | H-01 | Observability: Sentry backend + frontend wiring |
| `b552efe` | M-26 | Testing: pytest coverage for _init_sentry() |
| `4920431` | H-33 | Fix: restore Sentry stack dropped from b552efe |
| `bfef00f` | H-25 | Security: JWT access token migrated to HttpOnly cookie |
| `c96a71c` | H-34 | Security: add cookie fallback to get_optional_current_user |
| `2f0fc8a` | H-35 | Security: restore CSP header lost in M-10 merge |
| `ebefbd7` | H-35 | Merge fix/security/AWD-H-35-restore-csp-header into develop |
| `64d117b` | M-36 | Security: restrict CORS allow_methods/allow_headers from wildcard |
| `25f78c2` | M-36 | Merge fix/security/AWD-M-36-cors-restrict-methods-headers into develop |
| `db282f7` | M-13 | Performance: joinedload N+1 fix in get_child_topics |
| `f0f7a84` | M-13 | Merge fix/performance/AWD-M-13-get-child-topics-joinedload into develop |
| `ff6856c` | M-36 | Accessibility: replace nested button cards with div[role=group] in ParentDashboardPage |
| `9e25c23` | M-36 | Merge fix/parents/AWD-M-36-fix-nested-button-html into develop |
| `d9f8125` | M-14 | Performance: batch subject FK validation in create_child / update_child |
| `99981fc` | M-14 | Merge fix/children/AWD-M-14-batch-subject-fk-validation into develop |
| `34940e1` | M-02 | SEO: add OG tags, Twitter card, schema.org and og-image to landing page |
| `577921c` | M-02 | Merge feat/seo/AWD-M-02-meta-tags-og into develop |
| `d791752` | M-37 | Fix: convert og-image SVG to PNG for Open Graph compatibility |
| `7ac1c42` | M-37 | Merge fix/seo/AWD-M-37-og-image-svg-to-png into develop |
| `b25e3a0` | H-36 | Fix: restore batch subject FK query + AI guide validation |
| `67d23ce` | H-36 | Merge fix/children/AWD-H-36-restore-batch-subject-fk-query into develop |
| `af523cd` | H-37 | Test: fix TestUnauthenticated assertion from 403 to 401 |
| `a513468` | H-37 | Merge fix/children/AWD-H-37-unauthenticated-401-assertion into develop |
| `663b50a` | M-15 | Frontend: TypeScript types for children & guides API methods |
| `91b2740` | M-15 | Merge fix/frontend/AWD-M-15-api-types into develop |
| `e3627b9` | M-41 | Fix: restore typed API interfaces stripped in AWD-M-04 test commit |
| `fc55014` | M-41 | Merge fix/testing/AWD-M-04-shore-up-service-coverage into develop |
| `c83bee8` | M-21 | Parents: PDF export for "How to Help" guides (download button + backend endpoint) |
| `f97e86b` | M-21 | Docs: update backlog and dev-log for AWD-M-21 |

---

## 🟠 Decisions Required Before Agent Can Implement

_No open decisions — all cleared._

---

## 🟡 One-time Setup

### Sentry DSN — activate error monitoring (AWD-H-01 is shipped, just needs config)
1. Go to [sentry.io](https://sentry.io) → create two projects: one **FastAPI**, one **React**
2. Copy each DSN and add to your production environment:
   - Render (backend): `SENTRY_DSN=<backend-dsn>` and `SENTRY_TRACES_SAMPLE_RATE=0.1`
   - Vercel (frontend): `VITE_SENTRY_DSN=<frontend-dsn>`
3. No code changes needed — the init blocks already exist and activate when the env var is set

### project-config.md §5 — update ERROR_MONITORING field (AWD-L-10)
The line still reads `not yet connected (Sentry recommended — flagged as H-01)`.
Change it to reflect Sentry is now wired (`sentry-sdk[fastapi]==2.58.0` + `@sentry/react ^8`).

---

## 🟢 Low Priority / When You Have Time

| # | What |
|---|------|
| L-07 | Confirm no older clients call `/auth/google` without a `role` field — the default changed from `EDUCATOR` → `PARENT` in the pivot |
| GRC-01 | COPPA: add parental consent flow before first ChildProfile creation (plain-language disclosure + explicit opt-in) |
| GRC-02 | GDPR: data export endpoint so parents can download all their data |
| GRC-03 | GDPR: account deletion endpoint with cascade for ChildProfile + ParentGuide |

---

## ✅ Done (recently cleared)

| Date | Item |
|------|------|
| 2026-04-23 | AWD-C-05 git repo corruption resolved (develop ref restored to valid commit) |
| 2026-04-23 | H-25 decision made: httpOnly cookies (backlog updated, ready to implement) |
| 2026-04-23 | M-09 decision made: catalog endpoints require auth (backlog updated, ready to implement) |
