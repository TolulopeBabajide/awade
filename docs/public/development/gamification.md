# Gamification Design (Planned)

Status: Planned (no implementation yet)

## Goals
- Increase teacher engagement in lesson planning and resource generation
- Reward use of local context and curriculum alignment
- Encourage sustainable, healthy usage habits (streaks)
- Provide institution-scoped visibility (opt-in)

## MVP Scope
- Experience Points (XP) for key actions (plan created, resource generated, exported)
- Streaks (daily/weekly creation)
- Badges for milestones (subjects covered, topics completed)
- Optional institution leaderboards (opt-in)

## Proposed Data Model
- achievements (id, key, name, description, category, points, rarity)
- user_achievements (user_id, achievement_id, unlocked_at)
- user_xp (user_id, total_xp, current_level, last_action_at, streak_days)
- activity_log (id, user_id, event_key, points, metadata, created_at)

## API (Proposed)
- POST /api/gamification/track { event_key, metadata }
- GET  /api/gamification/summary
- GET  /api/gamification/achievements
- GET  /api/gamification/leaderboard?scope=institution

Event keys:
- lesson_plan.created
- lesson_resource.generated
- lesson_resource.exported
- context.added

## XP & Badges (Draft)
- XP: 10 (plan.created), 15 (resource.generated), 5 (context.added), 20 (exported)
- Badges: "First Plan", "Local Context Champion", "Subject Explorer", "Weekly Streak 7"

## Frontend UX (Proposed)
- Profile: XP, level, streak, recent badges
- Toasts: "+15 XP for resource generation"
- Dashboard widget: progress toward next badge/level
- Settings: opt-in/out of public leaderboards

## Privacy & Ethics
- Leaderboards opt-in and institution-scoped
- Positive reinforcement only; no punitive mechanics
- Minimal data retention in activity logs

## Rollout Plan
1) Instrument events in lesson planning flows
2) Compute XP and basic streaks server-side
3) Ship profile summary + achievement toasts
4) Add badges and leaderboards

## Non-Goals (for now)
- Student-facing gamification
- Monetary rewards
- Global cross-tenant leaderboards

## Open Questions
- Institution boundaries and membership sync
- Badge localization
- Offline accrual and sync conflict handling




