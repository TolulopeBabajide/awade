# Monday Prep — 2026-04-28

**Prepared by:** weekend-ops / Ops Agent (Saturday 2026-04-25)
**Sprint window:** 2026-04-28 → 2026-05-02 (5 working days)
**Launch target:** Parent pivot public launch — June 2026

---

## ⚡ Before the dev agent picks up any new work

**Run this first, right now:**

```bash
cd /Users/tolulopebabajide/Desktop/Projects/awade/awade
git push origin develop
```

All 112 commits from the past week are local-only. CI has never seen them. Nothing is deployed. This one command unblocks everything.

---

## Top 5 recommended sprint issues

| Priority | Issue | Area | Effort | Why now |
|---|---|---|---|---|
| 1 | **H-41** — Fix GuideViewPage.test.tsx (6 TS errors + 1 failing test) | Testing | S | **CI blocker.** Will fail `frontend-test` on first push. Remove `React` import, change 5× `null` → `undefined`, add `waitFor` wrapper. Must land with or immediately after the push. |
| 2 | **M-35** — Replace `'unsafe-inline'` in CSP with nonce-based approach | Security | M | Last meaningful security gap after the sprint. `'unsafe-inline'` in `script-src` defeats most XSS protection CSP provides. Remove for `script-src` first; test frontend. Agents can implement nonce injection in middleware. |
| 3 | **M-04** — Backend coverage shore-up (children_service + lesson_plan_service) | Testing | M | Coverage was 70% floor at the start of the security sprint; the 50+ new commits have added many code paths that may not be covered. Run `pytest --cov` to see current state; close any module below 70%. |
| 4 | **GRC-01** — COPPA parental consent flow before first ChildProfile creation | Compliance | M | June launch blocks on this. Creating a ChildProfile without capturing a dated parental consent record would violate COPPA. Plain-language disclosure modal + explicit opt-in + DB record. The earlier this lands, the more time for QA. |
| 5 | **M-17** — Consolidate migration systems (pick Alembic, port 008 migration) | DX / Infra | M | Blocks M-16 (join table for subjects analytics). Three migration systems coexist right now; `migrate_database.py` uses `create_all()` which means rollbacks are impossible. Needs a Tolu decision on the approach first (see decisions below). |

---

## Carry-over items (pending push from last week)

All of these are already committed to local `develop` — they just need `git push origin develop` to be visible to CI and Render/Vercel:

- **M-03** (pre-commit hooks): Files applied by agent; Tolu must run `npm install` in `apps/frontend/` + `sh scripts/setup-hooks.sh` to activate husky. Then commit `apps/frontend/package-lock.json` + `.husky/pre-commit`.
- **H-39/L-12/H-40/M-05**: All committed as part of the f4ebdb3 batch recovery commit. Will ship with the push.
- **M-38, M-39, M-40**: Committed and merged. Will ship with the push.

---

## Decisions needed from Tolu

These are specific, blocking questions — the dev agent will skip these items until answered:

1. **Migration system (M-17 prerequisite):** Do you want to consolidate onto Alembic (recommended) and port `migrations/008_add_parent_role_and_child_profiles.py` into `alembic/versions/`? Or is there a reason to keep the sequential `migrations/` directory? _This blocks M-16 (join table for subjects)._

2. **GoogleAuthRequest.role default (L-07):** Are there any pre-pivot educator clients (browser extension, older app version, test scripts) that call `POST /api/auth/google` without passing a `role` field? If yes, those clients will now create PARENT accounts (since the default changed). If no pre-pivot clients remain, this item can be closed. _15-minute decision, low stakes but needs your knowledge._

3. **require_parent wiring vs. delete (L-05):** `require_parent` and `require_any_role` helpers were added to `dependencies.py` but are unused. Options: (a) wire `require_parent` into `children.py` router so role is enforced at the router level (cleaner than the current ParentRoute frontend guard + backend role check), or (b) delete the helpers since ParentRoute already handles the frontend gate and each endpoint checks ownership. Which do you prefer?

4. **Admin parent/child views (H-03):** The admin panel has no UI for viewing or managing parent/child data. Is this needed before June launch, or is direct DB access sufficient for the beta period? This is L-effort — not urgent, but needs a yes/no before it enters any sprint plan.

---

## One growth initiative for the week

**Run the first end-to-end parent user journey test with a real account.**

The parent flow is fully implemented (onboarding, child profile, topic selection, guide generation, WhatsApp share, bookmarking). Before the June launch marketing push, Tolu should walk through the entire journey as a real parent would — on a mobile device if possible — and note any friction. The agents have been building features; someone needs to actually use the product.

Suggested test: create a new parent account via Google OAuth → complete onboarding → add a child (Nigerian curriculum, JSS1 Maths) → navigate to a topic → generate a guide → share via WhatsApp → bookmark. File anything that feels wrong as a new backlog item.

This costs 20 minutes and will surface UX issues that no automated test can catch.

---

## At-a-glance health entering the week

- 🔴 0 Criticals open (down from 3 last week — full security sprint completed)
- 🟠 2 Highs open: H-41 (CI blocker, S), H-03 (admin panel, L)
- 🟡 11 Mediums open: M-35 (security), M-04 (coverage), M-17 (migrations), M-16, M-15, M-06, M-07, M-19, M-20, M-21, M-39
- 🟢 10 Lows open — several trivial (L-10, L-09, L-02)
- 🟣 5 Compliance items open — GRC-01 is launch-critical
- CI: **❌ Not validated** — 112 commits are local-only. Push before anything else.
- Latest local develop HEAD: `d9e5d53`
