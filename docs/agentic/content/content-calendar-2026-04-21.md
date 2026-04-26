# Content Calendar — Week of 2026-04-27

> Planned on 2026-04-21 (Tuesday) by the Content Calendar Agent.
> Covers Mon 2026-04-27 → Fri 2026-05-01.

## Context used
- `project-config.md` — brand voice (warm, encouraging, practical, Africa-centred; avoid "revolutionize / disrupt / empower / leverage / unlock")
- `.claude/skills/marketing-agent/SKILL.md` — daily format (Mon short posts, Tue Twitter thread, Wed LinkedIn, Thu email, Fri week-in-review)
- `docs/agentic/backlog.md` — ✅ Done section (only "Initial agentic framework adaptation" logged; Parent Pivot Phases 1–4 completed 2026-04-16 per footnote — worth highlighting as BIP)
- `docs/agentic/content/content-log.md` — **does not exist yet** (first run); no prior topics to dedupe against

## Channel status caveat
Per `project-config.md` §8, Twitter/X, Instagram, LinkedIn, TikTok, and Email are all marked "not set up". Drafts below are staged so they're ready when channels go live. **Flagged for Tolu** — see "Needs Tolu" section at the bottom.

---

## Plan

| Day | Platform | Content pillar | Topic | Hook line | Suggested visual | Audience |
|-----|----------|----------------|-------|-----------|------------------|----------|
| Mon 2026-04-27 (AM) | Twitter/X | Parent empowerment stories | "The maths homework moment" — parent doesn't know fractions, child does | "Your 10-year-old just asked what 3/4 of 16 is. You freeze. You're not alone — and you don't need a maths degree to help." | Warm illustrated scene: parent + child at kitchen table, maths book open, phone showing an Awade guide | parent |
| Mon 2026-04-27 (PM) | LinkedIn (short) | Behind-the-scenes product updates | Parent pivot shipped — why we added a second audience | "Six months ago Awade was teachers only. Last week we shipped parent guides. Here's what changed our mind." (3-sentence micro-post, link to longer Wed piece) | Before/after screenshot: teacher dashboard → parent dashboard | all |
| Tue 2026-04-28 | Twitter/X (thread, 7 tweets) | Curriculum insights | How a Nigerian JSS1 maths topic actually lands at home — fractions in context | "Most African primary curricula teach fractions by week 6 of term 2. Most home explanations skip straight to the algorithm. Here's what we learned building 'How to Help' guides 🧵" | Thread cover card: "Fractions, but make it jollof" — with a rice-serving diagram | parent + educator |
| Wed 2026-04-29 | LinkedIn (long, 250–320 words) | Teacher workflow tips | The 4-hour lesson plan problem — and what teachers actually need instead | "A teacher in Lagos told us she spends 4 hours every Sunday writing lesson plans. None of them reference the market her students pass on the way to school. We built something for her." | Photo/illustration: teacher marking books, cup of tea, laptop open to a lesson plan with local context callouts | educator |
| Thu 2026-04-30 | Email / newsletter draft | Africa-centred education news | Monthly roundup — education news across the continent teachers and parents are talking about (April 2026) | "What African educators are talking about this month — and one small thing you can try on Monday." | Simple email header: Awade wordmark + green banner; inline flags for featured countries | all |
| Fri 2026-05-01 | Twitter/X + LinkedIn (cross-post) | Behind-the-scenes product updates | Week-in-review: what we shipped, what we learned, what's next | "This week at Awade: [placeholder — fill from dev-log.md on Fri morning]. One thing that surprised us: [placeholder]." | Weekly recap card template: 3 panels — shipped / learned / next | all |

---

## Pillar balance across the week
Mapping requested pillars → days:
1. Parent empowerment stories → Mon AM
2. Teacher workflow tips → Wed
3. Curriculum insights → Tue
4. Africa-centred education news → Thu
5. Behind-the-scenes product updates → Mon PM + Fri

All 5 pillars covered, with BIP appearing twice (reasonable given the parent pivot is still the freshest shipping story and we have a green-field content-log).

---

## Voice checks applied
- No banned words ("revolutionize", "disrupt", "empower" in copy, "leverage", "unlock") appear in hook lines.
- The word *empowerment* is used only as a pillar label (per the task brief), never in user-facing copy.
- Hooks are specific, not generic ("3/4 of 16", "4 hours every Sunday", "week 6 of term 2") — matches SKILL.md rule "Specific > generic".
- No fabricated testimonials. The Lagos-teacher line on Wed needs Tolu confirmation (see below).

---

## Needs Tolu's input before publishing

1. **Wed LinkedIn (teacher workflow tips)** — the "teacher in Lagos told us she spends 4 hours every Sunday" line is written as a composite illustration. If it's not grounded in a real conversation, rewrite as *"Teachers we've spoken to say…"* or cite a source. Tolu: confirm which.
2. **Mon PM + Fri (BIP / parent pivot)** — numbers to include (if any): guides generated in first week, child profiles created, teacher-to-parent split. If Tolu wants real figures, pull from the analytics tool once PostHog/Amplitude lands (currently "not set up" per config §5). Otherwise keep qualitative.
3. **Fri week-in-review** — placeholders for "shipped / learned / surprised us" need the actual week's `docs/agentic/sprints/dev-log.md` entries. Auto-fill on Friday morning from the dev-log.
4. **Thu newsletter** — April 2026 Africa education news roundup needs 3–5 specific stories. Recommend Tolu picks from: Nigerian curriculum updates, South African POPIA changes affecting edtech, Kenyan CBC rollout news, and one "small thing to try Monday" sourced from the marketing-agent content pool.
5. **Channels still "not set up"** — per `project-config.md` §8, none of Twitter/X, LinkedIn, Instagram, or Email are live. Flag: before this calendar can ship, Tolu needs to decide (a) which channels launch first for the June 2026 public parent-pivot launch, and (b) who owns posting. Recommend LinkedIn + Twitter/X first — cheapest to run, highest founder-voice fit.

---

## Next steps
- Marketing-agent should draft individual posts in `docs/agentic/content/drafts/` following the schema in `.claude/skills/marketing-agent/SKILL.md` (one file per post).
- Once `docs/agentic/content/content-log.md` is created, log each draft as `[DATE] | [PLATFORM] | [PILLAR] | [TOPIC] | Draft saved`.
- Re-run this calendar planner every Wednesday; future runs will dedupe against `content-log.md`.
