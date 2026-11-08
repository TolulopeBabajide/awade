# Awade UX overhaul exploration

Exploratory direction, 7 November 2026. Scope: UX direction and an interactive concept. Proposed features below are design hypotheses, not shipped functionality.

## What the current product tells us

`project-config.md` defines two adult audiences: parents helping children at home and educators preparing curriculum-aligned lessons. The voice is warm, practical and Africa-centred, with mobile and low-bandwidth use central to the design.

Source review: `ParentDashboardPage.tsx` provides child selection followed by subject/topic grids; `DashboardPage.tsx` begins with country, curriculum, subject, grade and topic selection; `GuideViewPage.components.tsx` groups content into stacked sections. `Sidebar.tsx` already separates navigation by role. Existing CSS uses earthy green, terracotta, Inter/Poppins and broad hover/entrance effects. `docs/public/development/gamification.md` proposes XP, achievements and streaks but identifies them as planned.

These findings come from source inspection, not user research or observation of the running app. Validate the friction hypotheses below with parents and teachers.

## Recommended direction: a practical learning companion

Lead with one useful next action, retain topic browsing, and make return visits easy. Parents should feel able to start a short activity. Teachers should be able to reuse their class context and produce a reviewed, usable lesson.

Two layouts are explored in the interactive concept:

- **Daily companion (recommended starting point):** child/class context, one suggested activity, then a topic journey and flexible weekly goal. Suits users asking “what can I do now?”
- **Learning journey:** topic map first, followed by the featured activity and weekly rhythm. Suits users who already know the curriculum area they want to explore.

The suggested activity is a proposal, not an assertion about what a child is currently studying. In production let adults choose the current topic or confirm a suggestion.

## Visual system

- Leaf green `#345D39`: actions and completed practice.
- Ink green `#263E2B`: primary text.
- Paper `#F8FAF6` and white `#FFFFFF`: reading surfaces.
- Sage `#E9F0DF`: focused activity areas.
- Clay `#8D482F`: restrained recognition accents.
- Seed gold `#F1D88C`: current step, paired with a text label.

Retain Inter for body and navigation; use a clearer scale and less competing display typography. Use 16px body text in production, compact secondary labels, generous line spacing and short reading measures. The concept uses theme-specific light and dark equivalents. Complete contrast auditing is still required before implementation.

Give the featured activity the strongest shape and spacing. Use quiet lists for libraries and curriculum topics. The fractions illustration explains the activity itself rather than providing generic decorative artwork. Keep alignment left and reserve emphasis for one primary action per stage.

## Journey overhaul

| Area | Proposed experience | Important states |
| --- | --- | --- |
| Landing and authentication | Clearly choose helping at home or preparing lessons; preview a real example before account creation where feasible | Returning user, authentication failure, interrupted signup |
| Parent onboarding | Explain child-data use; collect only the profile and curriculum details needed; allow correction before confirmation | Consent, unsupported curriculum, incomplete profile |
| Teacher onboarding | Save class/curriculum context once; let teachers change it before generation | New class, missing curriculum, switching class |
| Home | Continue a recent activity or choose a topic; expose duration and required materials | First use, multiple children, no curriculum topics |
| Parent guide | Read overview or use an optional four-step activity mode; include practical materials and adaptations | Loading, generation error, previous/next, resume |
| Lesson creation | Confirm context, generate draft, review/adapt, create resources, export | Quota reached, failed generation, unsaved edits, export failure |
| Library | Distinguish saved, drafted, reviewed and practised content; keep search and subject filters available | Empty library, stale content, missing/deleted content |
| Progress | Show recorded practice and preparation; let adults revisit and correct records | No data, incomplete history, multiple children |
| Settings and accessibility | Accessible text sizing, reduced motion, private goals, profile controls and account settings | Save failure, data deletion confirmation |

Keep full guide reading available alongside guided mode; optional steps should not force experienced users through extra clicks. Preserve existing role restrictions and consent behaviour.

## Concept visualisation: the primary learning feature

Clarified direction: visualisation means making the subject matter visible and interactive. Progress displays are secondary navigation feedback.

Place an “Explore the concept” experience inside parent guides and educator lesson plans. Parents can use it alongside their child; teachers can demonstrate it to a class. Start with a concrete model, invite a prediction, let the adult/learner change a variable, animate the resulting relationship, then ask for an explanation. Keep a static explanation and physical-material alternative available.

The revised fractions concept demonstrates equal partitions of the same whole, an adjustable shaded amount, fraction notation, and the matching point on a number line. “Split every part in two” doubles numerator and denominator while preserving shaded area. A short challenge asks the learner to represent one half using six parts; feedback explains whether the amount is below, above or equal to the target. This is formative feedback, not an assessment of mastery.

Candidate concept families to validate:

| Subject | Concept | Meaningful interaction |
| --- | --- | --- |
| Mathematics | Fractions and equivalence | Shade parts, repartition the same whole, compare equivalent amounts |
| Mathematics | Place value | Regroup ten units into one ten while preserving total value |
| Mathematics | Area and perimeter | Resize a rectangle and compare how the two quantities change |
| Basic science | Electric circuits | Open/close a switch and see how a complete path affects a lamp |
| Basic science | Water cycle | Follow water through named stages and change conditions in a carefully scoped model |
| Geography | Day and night | Rotate Earth relative to a fixed light source and track one location |

Build a small library of reviewed concept templates, mapped to supported curriculum topics and learning objectives. AI may suggest a matching template and validated parameters; do not execute arbitrary AI-generated simulation code. Use bounded inputs, explicit model limitations, accurate relationships, accessible alternatives and subject-expert review. Unsupported topics should retain the text/physical activity instead of showing a generic animation. Start with fractions before expanding to more complex causal models.

Animations should show a conceptual change: regrouping units, preserving area during repartition, completing a circuit, or rotation relative to a light source. Cosmetic movement does not satisfy this requirement. Reduced-motion mode retains all states and explanations with immediate updates.

## Practice history and feedback

Start with a topic journey showing available, selected and practised topics, plus a weekly activity record. These describe actions adults recorded. They do not establish child mastery or curriculum coverage. Teacher status should say drafted/reviewed/taught only when that action is explicitly recorded.

Add adult-reported reflections such as “needed support”, “getting there” and “explained it clearly”. Store the observation and its date rather than converting it into an invented proficiency score. Show trends only after enough comparable records exist. Avoid estimates of time saved unless a defensible measurement method is defined.

## Gamification

Use private, optional weekly goals and descriptive milestones: first activity together, first reviewed lesson, and a locally adapted activity. Let people choose days and return after gaps without losing accumulated progress. Celebrate effort without implying that struggling learners or busy families are failing.

Reconsider the draft plan to grant XP for repeated generation/export. Reward meaningful, deduplicated actions such as an adult-confirmed practice session or a reviewed adaptation. Reopening, regenerating or exporting the same content should not farm rewards. Do not gate learning resources behind points. Exclude public child rankings. Adult institutional comparisons, if retained later, need a separate opt-in discovery exercise.

## Motion system

| Trigger | Motion proposal | Reduced-motion behaviour |
| --- | --- | --- |
| Open an activity | Brief 160–220ms spatial transition showing where the content opened | Immediate content replacement |
| Move between steps | Current-step indicator changes with a short directional transition | Immediate step/status update |
| Generation | Honest indeterminate status; show actual stages only if the server reports them | Static status with accessible text |
| Save or review | Checkmark and concise confirmation | Same confirmation without animation |
| Milestone reached | One restrained 250–350ms scale/check response | Static milestone message |
| Change progress view | Marks move to updated values; avoid repeated entrance effects | Immediate value change |

Avoid looping celebrations, decorative background motion, and blanket card scaling. Use CSS transforms/opacity for small responses. A new motion dependency is unnecessary for this exploration. Never announce every animation frame to assistive technology.

## What the interactive concept demonstrates

The initial shell concept demonstrates two home-layout alternatives, parent/teacher switching, topic navigation, library navigation, a four-step sample activity, teacher context entry, parent reflection, and a completion milestone. The revised concept focuses directly on interactive fractions, equivalence, number-line position and explanatory challenge feedback. Both use fictional sample data and local interaction only; neither calls AI, saves to the app, exports files, implements consent, or introduces backend models. “Save guide” in the shell demonstrates the resulting library view only.

## Delivery sequence

1. Validate the two home layouts with parents and educators on small screens. Observe first-action success, comprehension of topic status, and ability to resume.
2. Define shared tokens and shell, clarify navigation and rewrite empty/error states. Keep the existing generation flows working.
3. Improve context reuse, guide reading, lesson review and saved-content retrieval. Pilot the fractions visualisation within both adult flows. Verify its mathematical invariants and accessible non-animated explanation before adding other concept families.
4. Instrument meaningful events and introduce private practice/preparation history. Define corrections, deduplication and retention before claiming progress.
5. Pilot optional weekly goals and milestones. Compare useful return visits, completed activities, and reviewed lesson use against a baseline; also observe opt-outs and perceived pressure.

Production implementation needs a feature specification and design handoff before entering the repository's ready stage. The exploration does not change app routes or production components.

📝 **Feedback prompt**: If you revise this output significantly before using it, please log it — `"Log feedback: design-agent output was [approved / revised / rejected] — [what changed]"`. Logs go to `docs/agentic/feedback-log.md` and improve future prompts.
