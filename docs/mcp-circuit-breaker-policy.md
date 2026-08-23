# MCP Circuit Breaker Policy

> **Owner**: improvement-agent (IMP-06)
> **Created**: 2026-04-26
> **Applies to**: All agents that call session-level MCP tools

---

## Why This Exists

Session-level MCPs (Stripe, Sentry, Slack, Mixpanel, Intercom, Figma, Gmail, etc.) can be unavailable
at any time — the user may not have the session open, the connector may have timed out, or the service
may be down. Without a circuit breaker, agents hang or crash silently and produce no output.

This policy ensures every MCP-dependent agent:
1. Detects unavailability before acting on missing data
2. Logs the failure to `.agent-health/mcp-failures.log`
3. Continues with a documented degradation path rather than stopping

---

## How to Use the Circuit Breaker

`scripts/circuit-breaker.sh` wraps any MCP call. Call it before using a tool:

```bash
# Pattern: ./scripts/circuit-breaker.sh <tool-name> <health-check-command>
# Exit 0 = available, proceed normally
# Exit 2 = unavailable, use degraded path

./scripts/circuit-breaker.sh "stripe" bash -c "echo 'stripe-ping'" 2>/dev/null
if [ $? -eq 2 ]; then
  # MCP unavailable — use degraded path (see table below)
fi
```

For agents running in Claude/Cowork (not shell), apply the equivalent logic:
- Attempt the MCP tool call
- If it returns an error or times out: log to `.agent-health/mcp-failures.log` and follow the degraded path
- **Never block the run or leave output empty** because an MCP is unavailable

### Logging unavailability (in-agent, non-shell)

When an MCP tool call fails inside a Cowork session, append to the failures log manually:

```bash
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | UNAVAILABLE | <tool-name> | mcp-error" \
  >> .agent-health/mcp-failures.log
```

---

## Degradation Paths by Agent

Every MCP-dependent agent must follow the degraded path below when its primary tool is unavailable.
The degraded path must still produce a complete output file — never an empty one.

### analytics-agent — Mixpanel / Amplitude / PostHog

| State | Behaviour |
|-------|-----------|
| MCP available | Pull metrics directly from the analytics tool |
| **MCP unavailable** | Read `docs/analytics/` for the most recent report as prior-period baseline. Read `docs/sprints/dev-log.md` for proxy signals (PRs merged, features shipped). Write the report section header: `> ⚠️ Analytics MCP unavailable — data sourced from docs/ proxy signals. Manual update required.` File an `L-##` backlog item: "Connect analytics MCP for next run." |

### finance-agent — Stripe

| State | Behaviour |
|-------|-----------|
| MCP available | Pull MRR, churn, and payment events from Stripe |
| **MCP unavailable** | Read `docs/finance/` for the most recent figures. Use last known values and label them: `> ⚠️ Stripe unavailable — using last known figures from docs/finance/. Verify manually.` Do not omit the revenue section. |

### support-agent — Intercom / support inbox

| State | Behaviour |
|-------|-----------|
| MCP available | Pull open tickets, message volume, and CSAT from Intercom |
| **MCP unavailable** | Read `docs/support/support-log.md` for any manually-logged messages. Write: `> ⚠️ Support tool unavailable — check inbox manually. Reporting on logged messages only.` Still produce the weekly digest from what is available in docs/. |

### marketing-agent — Email tool / social APIs

| State | Behaviour |
|-------|-----------|
| MCP available | Pull send stats, open rates, follower counts from connected tool |
| **MCP unavailable** | Skip metrics sections that require live data. Label each skipped section: `> ⚠️ [Tool] unavailable — metrics not available this run.` Complete all non-metric sections (content calendar, copy drafts, etc.) normally. |

### growth-agent — Experiment platforms

| State | Behaviour |
|-------|-----------|
| MCP available | Pull experiment results and variant performance |
| **MCP unavailable** | Report on any results already written to `docs/growth/`. Write: `> ⚠️ Experiment platform unavailable — reporting on locally-logged results only.` Do not block experiment planning or copy output. |

### performance-agent — Analytics MCP (Core Web Vitals)

| State | Behaviour |
|-------|-----------|
| MCP available | Pull Core Web Vitals (LCP, CLS, FID/INP, TTFB) from the analytics tool |
| **MCP unavailable** | Skip the Real User Metrics section. Write: `> ⚠️ Analytics MCP unavailable — Core Web Vitals not available this run. Check manually.` Continue with all synthetic benchmark sections (API times, bundle size, N+1 patterns, etc.). Log to `.agent-health/mcp-failures.log`. |

### design-agent — Figma MCP

| State | Behaviour |
|-------|-----------|
| MCP available | Call `get_design_context` and `get_screenshot` to pull component names and design tokens |
| **MCP unavailable** | Fall back to `project-config.md` §7 (brand config) and the feature spec. Prefix every design decision that relied on Figma data with `ASSUMPTION:`. Write in the handoff doc: `> ⚠️ Figma MCP unavailable — design tokens and component names sourced from spec and brand config. Verify against Figma before dev implementation.` Continue and deliver the handoff. Log to `.agent-health/mcp-failures.log`. |

### ops-agent — Connected MCP health checks

| State | Behaviour |
|-------|-----------|
| MCP available | Report the tool as active in the health check |
| **MCP unavailable** | Mark the tool as unavailable in the report with note: "Not reachable this run — verify manually." Continue checking all remaining tools. Log each failure to `.agent-health/mcp-failures.log`. Never stop the health check because one tool is unreachable. |

### nightly-monitor — All MCPs (aggregate)

The nightly-monitor reads `.agent-health/mcp-failures.log` at runtime and includes an **MCP Health**
section in the morning brief. This is already implemented. No degradation is needed — if the log is
absent or empty, it reports "No MCP unavailability recorded."

---

## Infrastructure Dependencies (Fail-Open vs Fail-Closed)

Some agents depend on infrastructure that is not an MCP — a cache, a session/token store, a
queue. When such a dependency is down, the agent must make a deliberate **fail-open vs
fail-closed** choice and document the risk it accepts. Record each one in the table below so
the decision is auditable.

| Dependency | Used by | When down | Mode | Risk accepted |
|------------|---------|-----------|------|---------------|
| _example:_ session / token store | auth-critical paths | treat the lookup as "not found" | **fail-open** | A revoked token could be briefly honoured. Accepted because failing closed would lock out every active user — a worse outcome. Revisit if the store is down > 1h. |

Fail-open keeps the system usable but accepts a bounded risk; fail-closed is safer but can halt
the product. Neither is correct by default — the choice belongs to the founder. Add a row here,
with the **risk accepted** spelled out, before relying on either mode, and raise any open
question as a founder decision in the morning brief.

---

## Failure Log Format

`.agent-health/mcp-failures.log` is append-only. Each entry:

```
2026-04-26T03:00:00Z | UNAVAILABLE | stripe | exit=1
2026-04-26T04:15:22Z | UNAVAILABLE | intercom | mcp-error
```

Fields: `timestamp | UNAVAILABLE | tool-name | reason`

The nightly-monitor reads this log and surfaces it in the morning brief under `## MCP Health`.

---

## Acceptance Criteria (IMP-06)

- [x] `scripts/circuit-breaker.sh` exists and is callable
- [x] `.agent-health/mcp-failures.log` is created and described
- [x] Each affected agent has a documented degradation path (this file)
- [x] nightly-monitor reads `mcp-failures.log` and includes it in the morning brief (already implemented)
- [x] CLAUDE.md global section directs all MCP-using agents to this policy
- [x] No agent crashes or produces empty output when its MCP is down

---

## Related Files

- `scripts/circuit-breaker.sh` — the shell circuit breaker wrapper
- `.agent-health/mcp-failures.log` — append-only failure log
- `docs/daily-briefs/morning-brief.md` — where MCP health is surfaced each morning
- `CLAUDE.md §MCP Circuit Breaker` — global directive for all agents
