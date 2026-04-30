# Awade Agentic Team — Control Center

> **Last updated**: 2026-04-29
> **Status**: 19 scheduled tasks defined · 18 agent skills available · CI-aligned dev loop

---

## Quick Commands

| What you want | What to say |
|---------------|-------------|
| Fix a bug from the backlog | "Fix issue AWD-H-03" |
| Write tests for a feature | "Write tests for children_service" |
| Plan this week's sprint | "Run sprint planning" |
| Create social media posts | "Create this week's social content" |
| Write a blog post | "Write a blog post about helping parents with fractions" |
| Check financial health | "Generate this week's financial snapshot" |
| Full status review | "Run the weekly review" |
| Handle a support question | "How should I respond to this parent: [message]" |
| Security audit | "Run a security audit" |
| Plan a growth experiment | "Design an experiment to increase parent signups" |
| Review code quality | "Run a code review on the latest commits" |
| Audit tech debt | "Run a tech debt audit" |
| Check dependency CVEs | "Run a dependency security scan" |
| Architecture drift check | "Run an architecture review" |
| Access control audit | "Run an access review" |
| Compliance check | "Run a compliance audit" |
| Incident triage | "We have an incident: [description]" |
| Deploy to main | "Run devops agent — promote develop to main" |
| Inspect DB schema | Use the `db` MCP (Postgres introspect) |
| Check OpenAPI spec | Use the `openapi` MCP (`apps/backend/app/openapi.json`) |

---

## Hourly Dev + QA Loop

```
:00  dev-execution   →  picks top backlog issue (stage=ready)  →  implements  →  mirrors CI locally  →  merges to develop  →  push triggers CI
:15  code-review     →  structural review of every commit (SOLID, complexity, coupling)  →  files H-## for violations
:30  qa-validation   →  validates  →  cross-references CI  →  if fail: auto-files H-## into backlog  →  dev picks up next :00
:45  dashboard-refresh  →  regenerates agentic dashboard from latest logs
```

All self-gate: dev skips if commit within 50 min, QA skips if no new commits within 40 min.

---

## Full Schedule

| Time | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|------|-----|-----|-----|-----|-----|-----|-----|
| 6am | security-scan | security-scan | security-scan | security-scan | security-scan | security-scan | security-scan |
| 6:30am | compliance-audit† | access-review† | dependency-security | — | — | — | — |
| 7am | performance-audit | architecture-review‡ | — | — | tech-debt | — | — |
| 8am | health-check | health-check | health-check | health-check | health-check | — | — |
| 9am | weekly-review | — | content-calendar | — | — | — | — |
| 9:30am | sprint-planning | — | — | — | — | — | — |
| Hourly :00 | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution |
| Hourly :15 | code-review | code-review | code-review | code-review | code-review | code-review | code-review |
| Hourly :30 | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation |
| Hourly :45 | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh |
| 3pm | growth-daily | growth-daily | growth-daily | growth-daily | growth-daily | — | — |
| 5pm | — | — | — | — | friday-finance | — | — |
| 10am | — | — | — | — | — | weekend-ops | — |
| 11pm | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor |

† First occurrence of that weekday in the month only.
‡ Scheduled weekly but agent's 20160-min idempotency gate enforces biweekly cadence.

---

## Department Map

| Department | Agents | Auto-runs? |
|------------|--------|------------|
| Engineering | dev-agent, qa-agent, code-review-agent, devops-agent, incident-response-agent | ✅ Hourly (:00 / :15 / :30); devops + incident on demand |
| Architecture | architecture-agent, performance-agent, tech-debt-agent | ✅ Biweekly Tue 7am / Mon 7am / Fri 7am |
| Product | pm-agent, sprint-planning, weekly-review | ✅ Mon 9am + 9:30am |
| Security & Compliance | security-agent, access-review-agent, compliance-agent, dependency-security-agent | ✅ Daily 6am + Wed 6:30am + monthly |
| Marketing | marketing-agent, seo-agent, growth-agent | ✅ Daily 3pm + Wed 9am |
| Content | content-agent | On demand |
| Operations | finance-agent, analytics-agent, ops-agent | ✅ Fri 5pm + Sat 10am |
| Support | support-agent | On demand |

---

## Key Output Files

All under `docs/agentic/` (kept separate from `docs/public/` and `docs/private/`).

| File | Written by | Read by |
|------|-----------|---------|
| `docs/agentic/daily-briefs/morning-brief.md` | nightly-monitor | You, every morning |
| `docs/agentic/daily-briefs/monday-prep.md` | weekend-ops | You, every Monday |
| `docs/agentic/backlog.md` | pm-agent, qa-validation (auto-files failures), code-review-agent | dev-execution |
| `docs/agentic/sprints/dev-log.md` | dev-execution | weekly-review, weekend-ops |
| `docs/agentic/sprints/qa-log.md` | qa-validation | nightly-monitor, weekly-review |
| `docs/agentic/audits/security-report-[date].md` | security-scan | weekly-review |
| `docs/agentic/content/drafts/` | growth-daily | You (approve before posting) |
| `docs/agentic/weekly-reviews/` | weekly-review, weekend-ops | You |
| `docs/agentic/finance/` | friday-finance, you (balance.md) | You, weekly-review |
| `docs/performance/` | performance-agent | You, weekly-review |
| `docs/tech-debt/` | tech-debt-agent | You, architecture-agent |
| `docs/audits/` | access-review-agent, compliance-agent, dependency-security-agent | You, security-scan |
| `docs/agentic/feedback-log.md` | All on-demand agents | You (improvement tracking) |
| `.agent-health/` | All scheduled agents (heartbeats + MCP failures) | nightly-monitor |

---

## CI / CD Integration

Awade's CI pipeline lives at `.github/workflows/ci.yml` and runs on every push/PR to `main` and `develop`. The agentic framework is built around it:

- **dev-execution** runs the same commands as `backend-test` + `frontend-test` + `contract-test` locally before committing
- **qa-validation** re-runs them after commit and cross-references the real CI via `gh run list` if the GH CLI is available
- **security-scan** mirrors the `security` CI job's checks, then adds OWASP Web + LLM Top 10
- **nightly-monitor** reports the last CI verdict on `develop`

Deploy target: Render (backend via `render.yaml`) + Vercel (frontend via `apps/frontend/vercel.json`). The `deploy` CI job only runs on push to `main`.

---

## MCP Servers (repo-level, always available)

Defined in `.cursor/mcp.json` — all agents can use these:

| MCP | What it gives you |
|-----|-------------------|
| `openapi` | FastAPI OpenAPI spec (`apps/backend/app/openapi.json`) — ask about endpoints, payloads, contracts |
| `env` | `env.example` file only — read variable names without touching real `.env` |
| `db` | Postgres schema introspection on local dev DB — ask about tables, columns, indexes |
| `docs` | All public markdown (README, `docs/public/**`, `packages/**`, `apps/**`) |
| `internal` | Internal dev/api/deployment docs (`docs/internal/**`, etc.) |
| `external` | User-facing docs (`docs/external/**`, `docs/user-guide/**`) |
| `design` | Design brief + README for brand voice / design work |
| `code` | Python + TS/JS source under `apps/` + `packages/` + `scripts/` |

Use these before reaching for raw grep — they're faster and scoped.

---

## Session-level MCPs (connect as needed)

### Connected
- [ ] Gmail
- [ ] Google Drive
- [ ] GitHub (enables `gh run list` for CI status checks)

### Connect for full automation
- [ ] **Stripe** — MRR, payments (enables finance-agent; currently pre-revenue)
- [ ] **Sentry** — error monitoring (unblocks AWD-H-01 + supercharges security-scan + health-check)
- [ ] **Linear** — replaces manual backlog.md (optional)
- [ ] **Slack** — alerts and notifications
- [ ] **Mixpanel / Amplitude / PostHog** — product analytics for NORTH_STAR_METRIC
- [ ] **Intercom / Crisp** — customer support

---

## What You Do vs What Agents Do

| Tolu's job | Agents' job |
|----------|-------------|
| Product vision (parent-first vs teacher-first balance) | Implement the decisions |
| Approve social content before posting | Draft all content (parent + educator audiences alternated) |
| Review PRs (optional) | Write, test, merge to develop, push for CI |
| Handle complex parent/teacher conversations | Draft support responses |
| Connect paid tools | Use connected tools |
| Set pricing when ready | Model pricing scenarios |
| Decide when to promote `develop → main` | Never auto-promote to main |

---

## First-week checklist (for the agentic framework)
- [ ] Create all 19 scheduled tasks from `docs/agentic/SCHEDULED-TASKS.md`
- [ ] Click "Run now" on each scheduled task once to pre-approve tools
- [ ] Read the first `morning-brief.md` — you're live
- [ ] Connect GitHub MCP so the dev+QA loop can read real CI status
- [ ] Pick the top High issue from the backlog and let the dev loop take it
- [ ] Run access-review-agent and compliance-agent once manually to get baseline reports
