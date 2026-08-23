2026-06-03T00:00:00Z | H-08 | fix check-permissions.sh path traversal and prefix-sibling bypass | 8c6aeed | ✅ Done
2026-06-04T00:00:00Z | H-07 | Wire circuit-breaker into analytics-agent, ops-agent, performance-agent, design-agent | 812e7d6 | ✅ Done
2026-06-04T01:16:05Z | H-09 | sanitize-input.sh misinvoked in 4 user-input skills | 3d5e53a | ✅ Done
2026-06-04T02:14:55Z | H-16 | Dashboard redesign R7 — emit per-agent run counts in the data block | 03e8d99 | ✅ Done
2026-06-04T03:25:00Z | H-10 | Dashboard redesign R1 — inbox three-pane home (React + esbuild) | 047dcbf | ✅ Done
2026-06-04T05:00:00Z | H-11 | Dashboard redesign R2 — reading pane renders source-artifact content inline | 2d23fc9 | ✅ Done
2026-06-04T06:16:09Z | H-13 | Dashboard R4 — Outputs view grouped by category, review state badges, soft scroll tip | 8b579d2 | ✅ Done
2026-06-04T07:17:55Z | H-14 | Dashboard redesign R5 — Roster org chart with agent detail pane, status filter incl. critical | 1c70f8b | ✅ Done
2026-06-04T08:57:00Z | H-15 | Dashboard redesign R6 — Pulse hourly-loop strip + Pipeline stage kanban | 05ef44c | ✅ Done
2026-06-04T10:25:25Z | L-01 | Add pre-commit hooks for lint and type check | b7662dd | ✅ Done
2026-06-04T19:32:22Z | — | dev-agent run: no stage=ready items in backlog — idle cycle | — | ⏭ Skipped
2026-06-05T09:00:00Z | C-01 | fix(tooling): C-01 explicit origin branch in all pull --rebase calls | 519f444 | ✅ Done (push deferred — merge commit local, push manually via `git push origin develop`)
2026-06-05T09:27:47Z | H-23 | Rewrite codebase-map.md with actual project layout | 1bfc7ed | ✅ Done
2026-06-05T10:27:03Z | H-24 | Unblock improvement-agent; implement IMP-11 anomaly detection | e51c846 | ✅ Done
2026-06-05T11:24:27Z | M-36 | Branch name placeholders never substituted in workflow.md | 4198c12 | ✅ Done
2026-06-05T12:24:01Z | M-35 | Add --test smoke-test mode to all 10 infrastructure scripts | e3a97aa | ✅ Done
2026-06-09T21:50:00Z | H-25 | Apply prompt-defense baseline to all 33 SKILL.md | 1d562a8 | ✅ Done
2026-06-11T20:35:00Z | H-26 | run-secret-scan-docs.sh bash-3.2 crash fix | — | ⛔ Blocked — check-permissions.sh denies dev-agent write to scripts/run-secret-scan-docs.sh; agent-permissions.json (v1.0, unchanged since setup) grants dev-agent no source-code write paths, so every stage=ready item (H-26/27/28, L-11/12) is unimplementable under SKILL.md §Permission Check. No code changes made; feature branch deleted. Filed H-29. Founder question: should dev-agent's write list in agent-permissions.json be extended to cover code paths (scripts/, .gitignore, tests/), or should the permission gate exclude dev-agent code work?
2026-06-12T00:00:00Z | BLOCKED | H-26/H-27/H-28/L-11/L-12 all at stage=ready but permission-denied — dev-agent write manifest lacks scripts/ and .gitignore paths; H-29 (founder decision) must be resolved to unblock the dev loop | — | ⛔ Blocked
2026-06-13T00:00:00Z | H-27 | prompt-injection-rules.md gitignored — unignore security contract on fresh clones | 795f01a | ✅ Done
2026-06-14T00:00:00Z | H-26 | run-secret-scan-docs.sh bash 3.2 compat (mapfile→while/read), binary exit code, extend scope to .claude/ | 81d1c28 | ✅ Done
2026-06-15T05:55:00Z | H-28 | H-28 sanitize-input.sh delimiter escape | 13fdc6b | ✅ Done
2026-06-16T00:00:00Z | L-11 L-12 | add *.tmp to .gitignore, delete stale err.tmp; L-11 *.p12 already present (no-op close) | 66e0c7a | ✅ Done (push deferred — permission denied; commit on local develop)
2026-06-21T00:00:00Z | M-41 L-07 | commit orphaned test suite (42 checks, 6 files) + schemas/template-manifest.json from prior run; add schemas/ to dev-agent permissions; remove stale L-01 backlog row (L-07) | 0891d08 | ✅ Done
2026-07-06T05:50:56Z | M-46 | wire check-template-integrity.py into TEST_COMMAND | a15e25e | ✅ Done
2026-07-13T05:50:29Z | — | No ready issues — backlog has 0 items at stage=ready (54 open at define/discover); skipped | — | ⏭ Skipped
2026-07-14T05:50:51Z | — | No ready issues — backlog has 0 items at stage=ready; all open issues at define/discover; skipped | — | ⏭ Skipped
