# [PROJECT_NAME] Agentic Team — Control Center

> **Last updated**: 2026-05-21
> **Status**: 23 scheduled tasks · 33 skills deployed · full lifecycle coverage active

---

## Quick Commands

### Discovery & Research
| What you want | What to say |
|---------------|-------------|
| Add an idea to the queue | "Add this idea to the discovery queue: [idea]" |
| Research an idea | "Run discovery on [idea]" |
| Competitive analysis | "Write a competitive brief on [competitor/feature area]" |
| User research plan | "Create a research plan for [topic]" |

### Strategy & Planning
| What you want | What to say |
|---------------|-------------|
| Write a feature spec | "Write a spec for [feature]" |
| Run GTM strategy (new projects) | "Run GTM strategy for [project/feature]" |
| Update the roadmap | "Update the roadmap — add [initiative]" |
| Plan this week's sprint | "Run sprint planning" |
| Full status review | "Run the weekly review" |

### Design
| What you want | What to say |
|---------------|-------------|
| Design a feature | "Design [feature] and produce a handoff doc" |
| Critique a design | "Review this design: [Figma link or description]" |
| Write UX copy | "Write copy for [screen/component]" |
| Accessibility audit | "Audit accessibility for [page/component]" |

### Engineering
| What you want | What to say |
|---------------|-------------|
| Fix a bug from the backlog | "Fix issue H-03" |
| Implement a feature | "Implement the feature at stage=ready" |
| Write tests | "Write tests for [feature]" |
| Security audit | "Run a security audit" |
| Prepare a release | "Prepare release from [INTEGRATION_BRANCH]" |
| Debug an issue | "Debug: [error message or description]" |
| Deep code review | "Review this code / review this PR" |
| Performance audit | "Run performance audit" or "Check API latency" |
| Architecture review | "Architecture review" or "Create ADR for [decision]" |
| Incident triage | "We have an incident" or "Production is down" |
| Postmortem | "Write a postmortem for [incident]" |
| Tech debt audit | "Tech debt audit" or "What should we refactor?" |

### Growth & Marketing
| What you want | What to say |
|---------------|-------------|
| Create social content | "Create this week's social content" |
| Write a blog post | "Write a blog post about [topic]" |
| SEO keyword research | "Research keywords for [topic/feature]" |
| SEO content brief | "Write a content brief for [topic]" |
| Growth experiment | "Design an experiment to increase [metric]" |
| Handle a support message | "Draft a response to this user message: [message]" |

### Security & Compliance
| What you want | What to say |
|---------------|-------------|
| Dependency CVE scan | "Dependency audit" or "Check CVEs" or "Scan packages" |
| License compliance check | "License audit" |
| Privacy / GDPR audit | "Compliance audit" or "GDPR check" or "Privacy review" |
| Data retention audit | "Data retention audit" |
| Access control review | "Review access controls" or "Permission audit" or "Check auth coverage" |
| API key rotation check | "Check API key rotation" |

### Analytics & Finance
| What you want | What to say |
|---------------|-------------|
| Analytics report | "Run the analytics report" |
| Check north star metric | "How is [NORTH_STAR_METRIC] trending?" |
| Financial snapshot | "Generate this week's financial snapshot" |
| Support digest | "Run the weekly support digest" |

### Feedback & Improvement
| What you want | What to say |
|---------------|-------------|
| Log feedback on last output | "Log feedback: [agent] output was [approved/revised/rejected] — [what changed]" |
| View feedback log | "Show me the feedback log" |
| Run improvement agent | "Run the improvement agent" or "Implement next system improvement" |

---

## Lifecycle Stages

```
[Discover] → [Define] → [GTM*] → [Design] → [Build] → [Ship] → [Learn] → ↩
                                   *new projects only
```

| Stage | Triggered by | Key output |
|-------|-------------|------------|
| Discover | You or analytics insights | docs/discovery/[date]-[slug].md |
| Define | Discovery "proceed" recommendation | docs/specs/[slug]-spec.md |
| GTM | Spec complete (new projects) | docs/gtm/strategy-[date].md |
| Design | GTM complete or spec approved | docs/design/handoff-[id].md |
| Build | stage=ready in backlog | Merged commit on INTEGRATION_BRANCH |
| Ship | Green build, release prepared | docs/sprints/release-[date].md |
| Learn | Post-ship | docs/analytics/weekly-[date].md → discovery queue |

**Existing projects enter at Build.** Run the onboarding-agent first.

---

## Hourly Engineering Loop

```
:00  dev-execution    →  picks top stage=ready item  →  implements  →  tests  →  merges
:15  code-review      →  SOLID + complexity + coupling + security patterns  →  files H-## if needed
:30  qa-validation    →  type check + lint + tests + CI gate  →  if fail: auto-files H-##
```

All three self-gate: dev skips if commit within 50 min, code-review skips if no new commits within 45 min, QA skips if no new commits within 40 min. If code-review verdicts 🛑, QA will catch the same commit and escalate — both signals surface to morning-brief.

---

## Full Schedule

| Time | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|------|-----|-----|-----|-----|-----|-----|-----|
| 6am | security-scan | security-scan | security-scan | security-scan | security-scan | security-scan | security-scan |
| 6:30am | **compliance-audit** *(1st Mon)* | **access-review** *(1st Tue)* | **dep-security-scan** | — | — | — | — |
| 7am | **perf-benchmark** | **arch-review** *(bi-wk)* | — | — | **tech-debt-audit** | — | — |
| 8am | health-check | health-check | health-check | health-check | health-check | — | — |
| 9am | weekly-review | support-digest | content-calendar | support-digest | seo-weekly | — | — |
| 9:30am | sprint-planning | — | — | — | — | — | — |
| 10am | — | — | — | — | — | weekend-ops | — |
| Hourly :00 | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution | dev-execution |
| Hourly :15 | **code-review** | **code-review** | **code-review** | **code-review** | **code-review** | **code-review** | **code-review** |
| Hourly :30 | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation | qa-validation |
| Hourly :45 | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh | dashboard-refresh |
| 3pm | marketing-daily | marketing-daily | marketing-daily | marketing-daily | marketing-daily | — | — |
| 4pm | analytics-daily | analytics-daily | analytics-daily | analytics-daily | analytics-daily | — | — |
| 5pm | — | — | — | — | friday-finance | — | — |
| 11pm | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor | nightly-monitor |

> **Continuous:** `improvement-loop` runs every 3 hours, around the clock — it is not shown on the weekly grid above.

> **Runtimes:** `security-scan`, `dev-execution`, `code-review-loop`, and `qa-validation` run on **Claude Code** (native git + CI access, no sandbox); the other 19 scheduled tasks run on **Cowork**. See `docs/SCHEDULED-TASKS.md` §Runtimes.

---

## Agent Roster

| Agent | Phase | Auto-runs? | On demand? |
|-------|-------|-----------|------------|
| discovery-agent | Discover | — | ✅ |
| onboarding-agent | All (existing projects) | — | ✅ once |
| pm-agent | Define | — | ✅ |
| gtm-agent | GTM | — | ✅ |
| design-agent | Design | — | ✅ |
| dev-agent | Build | ✅ Hourly :00 | ✅ |
| **code-review-agent** | **Build** | ✅ **Hourly :15** | ✅ |
| qa-agent | Build | ✅ Hourly :30 | ✅ |
| security-agent | Build | ✅ Daily 6am | ✅ |
| **dependency-security-agent** | **Build** | ✅ **Wed 6:30am** | ✅ |
| **compliance-agent** | **Build+Learn** | ✅ **Monthly (1st Mon 6:30am)** | ✅ |
| **access-review-agent** | **Build** | ✅ **Monthly (1st Tue 6:30am)** | ✅ |
| legal-agent | Build+Ship | — | ✅ |
| **performance-agent** | **Build+Learn** | ✅ **Mon 7am** | ✅ |
| **architecture-agent** | **Build** | ✅ **Bi-weekly Tue 7am** | ✅ |
| **tech-debt-agent** | **Build** | ✅ **Fri 7am** | ✅ |
| **incident-response-agent** | **Ship+Build** | — | ✅ |
| devops-agent | Ship | — | ✅ |
| marketing-agent | Ship | ✅ Daily 3pm | ✅ |
| growth-agent | Ship | — | ✅ |
| content-agent | Ship | — | ✅ |
| seo-agent | Ship+Learn | ✅ Fri 9am | ✅ |
| analytics-agent | Learn | ✅ Weekdays 4pm | ✅ |
| support-agent | Learn | ✅ Tue+Thu 9am | ✅ |
| finance-agent | Learn | ✅ Fri 5pm | ✅ |
| ops-agent | Learn | — | ✅ |
| weekly-review | Learn | ✅ Mon 9am | ✅ |
| sprint-planning | Learn→Build | ✅ Mon 9:30am | ✅ |
| improvement-agent | All (meta) | ✅ Every 3 hours | ✅ |
| nightly-monitor | Monitoring | ✅ Daily 11pm | ✅ |
| daily-health-check | Monitoring | ✅ Weekdays 8am | ✅ |
| weekend-ops | Monitoring | ✅ Sat 10am | ✅ |
| dashboard-refresh | Monitoring | ✅ Hourly :45 | ✅ |

**Plugin skills (on demand via conversation):**
Design: design-critique, ux-copy, design-handoff, design-system, accessibility-review, user-research, research-synthesis
PM: write-spec, competitive-brief, product-brainstorming, roadmap-update, stakeholder-update, metrics-review, synthesize-research, sprint-planning

---

## Key Output Files

| File | Written by | Read by you? |
|------|-----------|--------------|
| `docs/daily-briefs/morning-brief.md` | nightly-monitor, daily-health-check | ✅ Every morning |
| `docs/dashboard/index.html` | dashboard-refresh | ✅ Anytime — agent monitoring dashboard |
| `docs/daily-briefs/monday-prep.md` | weekend-ops | ✅ Every Monday |
| `docs/discovery/queue.md` | discovery-agent, you | ✅ When reviewing ideas |
| `docs/backlog.md` | pm-agent, qa-agent (auto-files) | ✅ As needed |
| `docs/gtm/strategy-[date].md` | gtm-agent | ✅ Once per project |
| `docs/design/handoff-[id].md` | design-agent | Optional |
| `docs/sprints/dev-log.md` | dev-agent | Optional |
| `docs/sprints/release-[date].md` | devops-agent | ✅ Before each release |
| `docs/analytics/weekly-[date].md` | analytics-agent | ✅ Weekly |
| `docs/support/digest-[date].md` | support-agent | ✅ Weekly |
| `docs/content/drafts/` | content-agent, marketing-agent | ✅ Before posting |
| `docs/weekly-reviews/review-[date].md` | weekly-review | ✅ Weekly |
| `docs/audits/security-report-[date].md` | security-agent | When flagged |
| `docs/audits/dep-security-[date].md` | dependency-security-agent | Weekly |
| `docs/security/sbom-[date].md` | dependency-security-agent | Updated weekly |
| `docs/legal/compliance-audit-[date].md` | compliance-agent | Monthly |
| `docs/audits/access-review-[date].md` | access-review-agent | Monthly |
| `docs/code-reviews/review-[date]-[hash].md` | code-review-agent | When verdict ⚠️ or 🛑 |
| `docs/performance/benchmark-[date].md` | performance-agent | Weekly |
| `docs/performance/baseline.md` | performance-agent | Updated weekly |
| `docs/architecture/arch-review-[date].md` | architecture-agent | Bi-weekly |
| `docs/architecture/adr-[NNN]-[slug].md` | architecture-agent | Per architectural decision |
| `docs/tech-debt/debt-report-[date].md` | tech-debt-agent | Weekly |
| `docs/tech-debt/debt-register.md` | tech-debt-agent | Updated weekly |
| `docs/incidents/incident-[date]-[slug]/postmortem.md` | incident-response-agent | Per incident |

---

## What You Do vs What Agents Do

| Your job | Agents' job |
|----------|-------------|
| Product vision and decisions | Implement the decisions |
| Review and approve GTM strategy | Research, draft, and validate it |
| Approve social and long-form content before publishing | Draft all content |
| Approve support responses before sending | Draft and classify all responses |
| Review PRs (optional) | Write, test, and merge code |
| Handle complex customer situations | Draft responses, surface patterns |
| Decide what to build next | Research, spec, and design it |
| Connect paid tools | Use connected tools automatically |
| Set pricing | Model scenarios, flag risks |

---

## Connected Tools

### Connect for full automation
- [ ] **Stripe** — enables live MRR/churn data in finance-agent
- [ ] **Sentry** — supercharges security-scan and nightly-monitor
- [ ] **Linear / GitHub Issues** — replaces manual backlog.md updates
- [ ] **Slack** — alerts, notifications, support message intake
- [ ] **Mixpanel / PostHog / Amplitude** — enables analytics-agent with real data
- [ ] **Intercom / Crisp / Help Scout** — enables support-agent with ticket queue
- [ ] **Figma** — enables design-agent to read/reference real design files
- [ ] **Google Search Console** — enables seo-agent with real ranking data
