# Interactive concept learning

Awade includes four bounded interactive models: fractions as parts of a whole, whole-number place value, rectangle area/perimeter, and a simple battery/switch/lamp circuit. Adults can open them from Explore on desktop or mobile, from either dashboard, and from matching guides, lesson plans and lesson-resource views. The landing page includes an account-free fractions activity.

## How it works

`components/learning/concepts.ts` is the reviewed model registry. `/explore?concept=<id>` selects a model; unknown IDs safely select fractions. `TopicConcept` matches a narrow allowlist of topic titles and the subject, then renders a supporting model. For example, Fractions in Mathematics matches; Algebraic fractions, Poetry, decimal place value and unsupported circuit topics do not. A model explains the stated foundational concept; it does not replace a complete lesson or guarantee curriculum coverage.

There are no AI-generated executable visualisations, extra generation calls, new endpoints or database migrations. Model parameters stay within fixed ranges. Whole-number place value covers 10–49; rectangle dimensions cover 1–6 units per side; fraction denominators are 2, 3, 4, 6, 8 and 12. The circuit assumes a working battery, lamp and conducting wire; it does not simulate voltage/current magnitude or household wiring.

## Recognition and privacy

An explanatory challenge can collect one discovery per concept per visit. Repeating a correct check does not increase the count. Progress exists only in React memory, persists while navigating within the app, and resets on reload or account change/logout. No child profile, scores, mastery claims, rankings, daily streaks or activity events are stored or transmitted. Future durable history requires its own product/data design.

## Accessibility and motion

Inputs have visible labels, native keyboard interactions and bounded values. Models provide textual descriptions, live results, focus indicators and physical-material alternatives. Fraction shade/position, rectangle dimensions and lamp state respond to input; discovery recognition uses a brief animation. `prefers-reduced-motion` removes non-essential transitions and suppresses existing app motion while retaining all controls and explanations. Visual QA at 320px, larger text and assistive-technology testing remain part of release review.

## Extension and checks

Add a typed concept ID and metadata, a deterministic model, a meaningful challenge, conservative topic matches and domain/integration tests. Do not infer an executable model from arbitrary generated prose. Require subject review before adding more complex simulations or claiming a topic is fully supported.

Run `npm run test:run`, `npx tsc --noEmit`, `npm run lint` and `npm run build` from `apps/frontend`. Tests cover fraction invariants, regrouping, area/perimeter, prediction-before-experiment, duplicate recognition, session account isolation, unsupported topics, URL selection and guide/lesson/resource rendering.

📝 **Feedback prompt**: If you revise this output significantly before using it, please log it — `"Log feedback: dev-agent output was [approved / revised / rejected] — [what changed]"`. Logs go to `docs/agentic/feedback-log.md`.
