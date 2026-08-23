// Direction C — extension data that the redesign needs but A/B never had.
// Per the spec these become real fields in `build-dashboard.py`'s data block;
// for the prototype we inline them next to the existing data.jsx exports.

/* R7 — per-agent run counts (24h window).
   In the real system: derived from docs/agent-run-log.jsonl (count rows
   where agent==name and ts > now-24h). Here: realistic mock that matches
   the cadence of each agent. */
const AGENT_RUNS_24H = {
  // hourly loop
  'dev-agent':                 18,
  'qa-agent':                  18,
  'code-review-agent':         18,
  'dashboard-refresh':         18,
  // every 3h
  'improvement-agent':         8,
  // daily / weekday
  'security-agent':            1,
  'daily-health-check':        1,
  'marketing-agent':           1,
  'analytics-agent':           1,
  'nightly-monitor':           1,
  // weekly / biweekly / monthly — zero in the last 24h
  'weekly-review':             0,
  'sprint-planning':           0,
  'content-agent':             0,
  'finance-agent':             0,
  'weekend-ops':               0,
  'support-agent':             0,
  'seo-agent':                 0,
  'performance-agent':         0,
  'architecture-agent':        0,
  'tech-debt-agent':           0,
  'dependency-security-agent': 0,
  'compliance-agent':          0,
  'access-review-agent':       0,
  // on-demand — counted from manual invocations only
  'discovery-agent':           1,
  'pm-agent':                  2,
  'gtm-agent':                 0,
  'onboarding-agent':          0,
  'design-agent':              3,
  'devops-agent':              1,
  'legal-agent':               0,
  'incident-response-agent':   0,
  'growth-agent':              0,
  'ops-agent':                 0,
};

/* R2 — content of the source artifact each inbox item points at.
   In the real system: build-dashboard.py reads the originPath and bakes
   the file contents into the data block (same pattern it already uses
   for OUTPUTS[*].content). Here: realistic mock. Keep these short but
   document-shaped — markdown that the founder would actually scan. */
const SOURCE_CONTENT = {
  'docs/sprints/qa-log.md': `# QA Log

## 2026-05-25 — 14:31 — Verdict: \`STOP\`

**Build:** \`3f9a2c1\` (dev-agent, H-119: type strict-null on /api/users)

### Tests
- Type check: ✓ pass
- Lint: ✓ pass
- Unit: ✗ **2 failures** in \`app/api/users/route.test.ts\`
- E2E: ✗ **1 failure** in \`tests/users-list.spec.ts\`

### Root cause (suspected)
Strict-null tightened the return type but \`findOne()\` can still return \`null\` when the id is unknown. The route returns 200 with \`undefined\` instead of 404.

### What dev-execution will do at :00
\`\`\`
Skip — qa-log last verdict is STOP.
Refusing to start work until founder clears.
\`\`\`

### Filed
- Backlog: **H-128** (regression) — area=Engineering, sev=high
- Owner: qa-agent → reassign on resolution

> Founder: clear by fixing H-128, overriding (\`:type=qa-override\`), or rolling back \`3f9a2c1\`.`,

  'docs/audits/security-report-2026-05-22.md': `# Security Audit — 2026-05-22

**Agent:** security-agent · **Run:** \`security-scan @ 06:00\`
**Scope:** OWASP Web Top 10 + OWASP LLM Top 10 + secret rotation

## Summary
- 0 new criticals, **1 carried forward**
- 0 high, 4 medium (auto-filed to backlog)
- 0 LLM-class findings this run

## C-12 — Rotate expired GCP service-account key
- **Resource:** \`gcp-sa-prod-deploy@…iam.gserviceaccount.com\`
- **Created:** 2026-02-19 · **Age:** 95 days · **Policy:** 90 days
- **Used by:** \`ci/deploy.yml\` (build push), \`scripts/db-migrate.py\`
- **Risk:** medium-high. No evidence of compromise; policy violation.
- **Action required:** founder rotates in GCP console, then runs:
  \`\`\`
  gcloud iam service-accounts keys list --iam-account=…
  \`\`\`
  to confirm only the new key exists.

> security-agent cannot rotate the key itself — \`agent-permissions.json\`
> denies cloud-credential writes. Founder action only.`,

  'docs/content/drafts/2026-05-22-linkedin.md': `# LinkedIn — v2.4 launch

**Pillar:** Launch · **Drafted:** 2026-05-22 15:02 · **Tone check:** ✓ matches brand voice (project-config.md §brand)

---

Six months ago we asked a question: what if your founding team was 33 agents instead of 33 people?

We have been answering it in production ever since.

Today **v2.4** ships with three things our customers asked for most:

→ **Async review queues.** Every artifact an agent writes lands in one inbox. Decide, never scan.
→ **Sprint-aware planning.** Backlog items move through stages, not statuses.
→ **One-click overrides.** When the system gets it wrong, fixing it takes a click, not a PR.

Three founders shipped on v2.3-beta with zero PMs and zero engineers. Their average review time per founder-blocking item dropped from 11 hours to 38 minutes.

If you are a founder who has been wondering whether you really need to hire that fifth engineer:

[Link in comments — v2.4 changelog]`,

  'docs/sprint-plans/sprint-2026-05-18.md': `# Sprint Plan — Week of 2026-05-18

**Agent:** sprint-planning · **Run:** \`sprint-planning @ 09:30 Mon\`
**Capacity:** 34 pts · **Selected:** 12 items

## Selected items
| ID | Pts | Title | Stage |
|----|-----|-------|-------|
| H-126 | 5 | /api/orders P95 over 800ms | define |
| H-119 | 3 | Type strict-null on /api/users | ready |
| M-43  | 2 | Strict-null follow-ups | in-progress |
| M-42  | 2 | Remove deprecated dateFmt() | ready |
| L-21  | 1 | Meta descriptions on docs pages | ready |
| … | | (7 more) | |

## Decisions needed from founder
1. **Pricing tier (H-125).** Hold tier-3 for v2.5 launch, or include in this sprint? \`pm-agent\` recommends hold; \`marketing-agent\` wants it now.
2. **/billing refactor scope (H-127).** Architecture review verdict is "refactor required" — split into hooks (3 pts) or extract submachine (8 pts)?
3. **Priority swap.** Promote H-119 over H-118? Same area, H-119 unblocks a customer thread; H-118 unblocks an internal cleanup.

> Sprint cannot start until all three clear.`,

  'docs/support/digest-2026-05-21.md': `# Support Digest — 2026-05-21

**Agent:** support-agent · **Window:** Sun 09:00 → Tue 09:00

## Volume
- 14 threads · 11 self-resolved · 1 routed to docs · **2 escalations pending**

## Escalations pending (need founder voice)

### 1. Acme Co. — SSO timeline
**Thread:** \`#cust-acme-co\` · **Last touched:** 2026-05-20 16:44
> "We're approving the renewal contingent on SSO landing before Q3.
> What's the earliest you can commit?"

Roadmap shows SAML in Q3, OIDC in Q4. Acme is on a $48k/year plan, renewal Aug 1.

### 2. Verge LLC — performance regression
**Thread:** \`#cust-verge\` · **Last touched:** 2026-05-21 08:12
> "/orders list is 4× slower than last week. We can't ship like this."

Cross-references **H-126** filed this morning. performance-agent confirms baseline drift on /api/orders. Renewal at risk.

> Per SKILL.md, support-agent surfaces only. Founder approval needed to draft replies.`,

  'docs/code-reviews/review-2026-05-22-a1b2c3d.md': `# Code Review — \`a1b2c3d\` BillingFlow.tsx

**Agent:** code-review-agent · **Verdict:** 🛑 **Refactor Required**

## Metrics
- Cyclomatic complexity: **18** (threshold: 10)
- Lines: 412 (threshold: 250)
- Branches: 24
- Nested ternaries: 3

## Issues
1. \`useBillingFlow\` hook owns state for 7 unrelated steps (plan select, address, tax, coupons, retry, 3DS, receipt).
2. Effects fire on stale closures — \`step\` is captured by index, not ref.
3. Error handling branches duplicate the same toast wiring six times.

## Recommended approaches

### Option A — Split into per-step hooks
- Effort: ~3 pts · Risk: low
- Each step becomes its own hook + component; state lifts via context.

### Option B — Extract state submachine (xstate or custom reducer)
- Effort: ~8 pts · Risk: medium (introduces a pattern not used elsewhere)
- Pays off if billing grows past current 7 steps.

> Filed as **H-127** with stage=discover. Founder picks the approach, then it moves to ready for dev-agent.`,

  'docs/legal/compliance-audit-2026-05-04.md': `# Compliance Audit — 2026-05-04 (monthly)

**Agent:** compliance-agent · **Standards:** GDPR, CCPA, internal PII retention

## Pass
- Data retention policy ✓
- Right-to-delete endpoint ✓
- DPA template on file ✓

## 🔴 GRC-08 — Cookie consent banner missing for EU users

**Severity:** medium (GDPR Art. 7 + ePrivacy)

### Evidence
GTM script (\`/scripts/gtm.js\`), Segment, and PostHog all fire on page load for users geolocated in the EU, before any consent prompt.

### What needs scoping (founder decision)
1. **Which regions trigger the banner?** EU/EEA only, or "EU + UK + CH"?
2. **Which scripts gate behind consent?** All three, or just GTM (the other two argue legitimate-interest)?
3. **Which CMP?** Build in-house (1 wk), or integrate Cookiebot (2 days, $89/mo)?

> Once scoped, the compliance-agent moves GRC-08 to stage=ready and dev-agent picks it up. **Today this has been open 18 days.**`,

  'docs/finance/snapshot-2026-05-16.md': `# Finance Snapshot — 2026-05-16

**Agent:** finance-agent · **Run:** \`friday-finance @ 17:00\`

## Top-line
- MRR: $42,180 (+3.1% WoW)
- Burn: $58,400/mo
- Runway: 14.2 months
- Net new logos · 7 days: 3

## Decision: Q3 observability spend

Three tools needed before traffic doubles in August:
- **Sentry** — $190/mo
- **Datadog APM** — $420/mo
- **PostHog Pro** — $230/mo
- **Total à la carte:** $840/mo

**Bundled alternative (Sentry + LogRocket + Mixpanel via stripe):** $520/mo — same coverage, signs before Fri 5pm.

### Recommendation
finance-agent recommends the bundled plan. Saves $3,840/yr; only downside is migrating PostHog dashboards (~4h of design-agent time).

> Renewal lapses Friday. Default is the à la carte plan if no decision is logged.`,

  'docs/discovery/queue.md': `# Discovery Queue

## 2026-05-24 — anomaly source: analytics-daily

### Activation −22% day-over-day
- D1 activation (signup → first action): 41.2% → 32.1%
- Window: 2026-05-23 vs 2026-05-22
- Significance: yes (n=412, p=0.003)

### Possible explanations
- Onboarding step 3 drop-off (already filed as M-44)
- Email-verification timing — checked, no change
- Signup form A/B — yes, **B variant rolled to 100% on 2026-05-23**

### What discovery-agent will do on next run
1. Re-cohort by signup variant
2. Pull session replays for 20 dropped users
3. File a follow-up if step-3 is confirmed as the cause

> Status: filed. discovery-agent runs on demand — founder triggers, or it pulls during the next scheduled review.`,

  'docs/weekly-reviews/review-2026-05-18.md': `# Weekly Review — Week of 2026-05-18

**Agent:** weekly-review · **Run:** \`weekly-review @ 09:00 Mon\`

## Department rollup

### Engineering
- 12 merges · 0 reverts · 2 hotfixes
- CI green rate: 96.4% · P95 build time: 4m 12s

### Security & Compliance
- 0 new criticals · 1 carried forward (**C-12**)
- 4 mediums auto-filed · 0 LLM findings

### Growth & Marketing
- 5 LinkedIn posts shipped · 2 Twitter · 1 long-form
- CTR up 14% WoW on top performer

### Customer Success
- 11 self-resolved · 2 escalations pending

## Highlights
- v2.4 RC built and signed off
- Activation dropped 22% on Mon — under investigation
- GRC-08 unresolved 18 days — needs scope

## Asks
- Acknowledge this review (clears it from inbox)
- Decide on Q3 observability bundle (Fri deadline)
- Scope GRC-08`,
};

/* R4 — content of each output artifact, rendered inline in the Outputs view.
   In the real system: this is already what build-dashboard.py emits (the
   prototypes' OUTPUTS dropped the `content` field — restoring it). Here:
   a representative subset; everything else falls back to a placeholder. */
const OUTPUT_CONTENT = {
  'docs/content/drafts/2026-05-22-linkedin.md':
    SOURCE_CONTENT['docs/content/drafts/2026-05-22-linkedin.md'],
  'docs/sprint-plans/sprint-2026-05-18.md':
    SOURCE_CONTENT['docs/sprint-plans/sprint-2026-05-18.md'],
  'docs/weekly-reviews/review-2026-05-18.md':
    SOURCE_CONTENT['docs/weekly-reviews/review-2026-05-18.md'],
  'docs/audits/security-report-2026-05-22.md':
    SOURCE_CONTENT['docs/audits/security-report-2026-05-22.md'],
  'docs/legal/compliance-audit-2026-05-04.md':
    SOURCE_CONTENT['docs/legal/compliance-audit-2026-05-04.md'],
  'docs/code-reviews/review-2026-05-22-a1b2c3d.md':
    SOURCE_CONTENT['docs/code-reviews/review-2026-05-22-a1b2c3d.md'],
  'docs/support/digest-2026-05-21.md':
    SOURCE_CONTENT['docs/support/digest-2026-05-21.md'],
  'docs/finance/snapshot-2026-05-16.md':
    SOURCE_CONTENT['docs/finance/snapshot-2026-05-16.md'],
  'docs/content/drafts/2026-05-21-twitter.md':
`# Twitter — v2.3.1 patch

**Pillar:** Patch notes · **Drafted:** 2026-05-21

Five small fixes shipped in v2.3.1:

→ Backlog filter now respects URL state
→ /api/orders P95 in steady-state down to 240ms
→ Dark mode contrast on muted text (thanks @aedwards)
→ One-click mode handshake retry on transient 503
→ Audit log timestamps are now timezone-aware

Tiny ship, real-feeling.`,
  'docs/content/content-calendar-2026-05-20.md':
`# Content Calendar — Week of 2026-05-20

## Pillars
- Mon · Build-in-public — sprint plan
- Tue · Launch — v2.4 LinkedIn
- Wed · Customer story — Acme onboarding
- Thu · Long-form — agent-permissions deep dive
- Fri · Recap — weekly review summary`,
  'docs/daily-briefs/morning-brief.md':
`# Morning Brief — 2026-05-25

**Generated:** 04:17 UTC by nightly-monitor

## Overnight
- 0 incidents · all agents healthy
- 4 hourly loops completed cleanly
- CI: all green

## To watch today
- Friday finance snapshot at 17:00 — observability decision lapses
- Sprint-planning Monday at 09:30 needs pricing-tier decision
- GRC-08 has been open 18 days

> Read first thing. dev-execution at :00 will pause if QA STOP from the night persists.`,
};

/* R-P1.2 — Upcoming runs, precomputed by build-dashboard.py from cron.
   Times are computed at build time (so the dashboard does not need a cron
   parser at render time) and shown relative to "now" (2026-05-25 14:42). */
const UPCOMING_RUNS = [
  { agent:'dev-agent',                    schedule:'Hourly :00',         when:'in 18m',  at:'15:00 today',  task:'dev-execution' },
  { agent:'code-review-agent',            schedule:'Hourly :15',         when:'in 33m',  at:'15:15 today',  task:'code-review-loop' },
  { agent:'qa-agent',                     schedule:'Hourly :30',         when:'in 48m',  at:'15:30 today',  task:'qa-validation' },
  { agent:'dashboard-refresh',            schedule:'Hourly :45',         when:'in 1h 3m', at:'15:45 today', task:'dashboard-refresh' },
  { agent:'marketing-agent',              schedule:'Weekdays 3pm',       when:'tomorrow', at:'Tue 15:00',    task:'marketing-daily' },
  { agent:'analytics-agent',              schedule:'Weekdays 4pm',       when:'tomorrow', at:'Tue 16:00',    task:'analytics-daily' },
  { agent:'finance-agent',                schedule:'Fridays 5pm',        when:'today',    at:'Fri 17:00',    task:'friday-finance' },
  { agent:'nightly-monitor',              schedule:'Daily 11pm',         when:'today',    at:'23:00 today',  task:'nightly-monitor' },
  { agent:'security-agent',               schedule:'Daily 6am',          when:'tomorrow', at:'Tue 06:00',    task:'security-scan' },
  { agent:'daily-health-check',           schedule:'Weekdays 8am',       when:'tomorrow', at:'Tue 08:00',    task:'daily-health-check' },
  { agent:'tech-debt-agent',              schedule:'Fridays 7am',        when:'today',    at:'Fri 07:00 ✓',  task:'tech-debt-audit', past:true },
];

/* Render-status overrides for agents whose presentation differs from
   their base status (R-P1.5, R-P1.6). The status field stays the same;
   `renderAs` decides which dot/treatment to use in the UI. */
const AGENT_RENDER = {
  'compliance-agent':       { renderAs:'scheduled-monthly', label:'Monthly · next cycle Jun 1' },
  'access-review-agent':    { renderAs:'scheduled-monthly', label:'Monthly · next cycle Jun 2' },
  'incident-response-agent':{ renderAs:'standby',           label:'Standby · never fired (good)' },
  'onboarding-agent':       { renderAs:'unused',            label:'On-demand · unused 12 days' },
};

Object.assign(window, {
  AGENT_RUNS_24H,
  SOURCE_CONTENT,
  OUTPUT_CONTENT,
  UPCOMING_RUNS,
  AGENT_RENDER,
});
