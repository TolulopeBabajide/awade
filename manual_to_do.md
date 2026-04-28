# Awade — Manual To-Do

> Things the agent cannot do autonomously (no GitHub credentials, no secrets access, requires your judgment).
> Agent updates this file whenever a task needs Tolu's hands. Check it before and after each dev session.
> Last updated: 2026-04-27 (Dev Agent — AWD-H-52 contrast fix shipped, commits cf64691 + merge 95b33f5 added)

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
| `c423fa9` | M-21 | Chore: update manual_to_do push list |
| `f0dddf4` | M-42 | Fix: replace bare print() with logger.warning in pdf_service.py |
| `3bfbbc6` | M-42 | Docs: update backlog, dev-log and manual_to_do for AWD-M-42 |
| `fb9e718` | M-35 | Security: remove unsafe-inline from CSP script-src |
| `2f79fed` | M-44 | Test: mark hollow test_rate_limiting as @pytest.mark.skip with backlog reason |
| `27a45f0` | M-44 | Merge fix/testing/AWD-M-44-fix-hollow-rate-limit-test into develop |
| `4b12ac8` | M-44 | Docs: update manual_to_do push list |
| `490b05a` | M-43 | Security: remove unsafe-inline from style-src, add font-src |
| `b63adbf` | M-43 | Merge fix/security/AWD-M-43-remove-style-src-unsafe-inline into develop |
| `3c0e2be` | M-06 | Perf: optimise landing page images (WebP, picture, fetchPriority) + Vite code splitting |
| `ebf6289` | M-06 | Merge fix/performance/AWD-M-06-lighthouse-image-optimisation into develop |
| `6f69506` | H-50 | Docs: regenerate openapi.json — consent, children, guide routes now included |
| `2813ef4` | H-50 | Merge fix/api-docs/AWD-H-50-openapi-regen into develop |
| `ef73e69` | M-51 | fix(frontend): remove console.log PII leak and unguarded debug logs (3 files) |
| `510fd89` | M-51 | Merge fix/frontend/AWD-M-51-remove-console-logs into develop |
| `ad60f1c` | M-50 | fix(backend): replace bare print() calls with structured logger in main.py |
| `561da10` | H-51 | fix(frontend): AWD-H-51 re-apply M-51 DEV guards reverted by ad60f1c |
| `a8ed1d6` | M-52 | fix(config): AWD-M-52 replace hardcoded WS URL with VITE_WS_URL env var |
| `521d702` | M-52 | Merge fix/config/AWD-M-52-vite-ws-url into develop |
| `fd9b86b` | L-06 | fix(data-model): use Boolean column for ParentGuide.is_bookmarked |
| `a9c3816` | C-09 | fix(git): restore AWD-M-52 work and AWD-L-06 docs lost by chore commits |
| `923fa87` | C-09 | chore(agentic): record AWD-C-09 commit hash in dev-log |
| `9a93d7e` | L-03 | docs(a11y): WCAG 2.1 AA audit for parent flow + 13 findings filed |
| `c9af293` | L-03 | Merge docs/parents/AWD-L-03-a11y-audit into develop |

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

### Set VITE_WS_URL in production (AWD-M-52)
The hardcoded WebSocket URL has been replaced with an env var. Before the next production deploy:
1. In Vercel → Settings → Environment Variables (Production), add:
   `VITE_WS_URL=wss://<your-backend-domain>/ws` (e.g. `wss://api.awade.app/ws`)
2. No backend change needed — value only affects the browser WebSocket client.

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

## Pending pushes

- [ ] Push develop to GitHub to trigger CI for AWD-M-45 (react ^18.3.0 bump, commit 27f9f01 / merge c863a67)
- [ ] Push develop to GitHub to trigger CI for AWD-H-52 (parent CTA contrast fix, commit cf64691 / merge 95b33f5)
- [ ] Push develop to GitHub to trigger CI for AWD-H-54 (AddChildModal dialog ARIA attrs, commit e0ed6ea / merge 5aaca85)
- [ ] Push develop to GitHub to trigger CI for AWD-H-55 (topic action button keyboard a11y + aria-labels, commit 66d9a79 / merge 11c9040, doc commit bdf97fa)
