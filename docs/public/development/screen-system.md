# Awade screen system

Implemented locally on 7 November 2026. Existing routes use the practical-learning-companion direction, with interactive concept learning described in [concept-learning.md](concept-learning.md).

| Screen | Route | New treatment |
| --- | --- | --- |
| Welcome | `/` | Concept-led hero, live fractions example, working footer links |
| Create account | `/signup` | Split account layout, keyboard-operable role selection, retained validation/legal links |
| Sign in and forgot password | `/login` | Shared account shell with retained recovery form and redirect handling |
| Reset password | `/reset-password` | Shared account shell, associated labels, error/success feedback, sign-in return |
| Parent setup | `/onboarding` | Context beside the profile form, optional-field guidance |
| Parent home | `/dashboard` for parents | Welcome action, curriculum-topic search, child switching and session discoveries |
| Children | `/children` | Larger profile cards, clear edit/remove controls and existing empty/error states |
| Saved guides | `/saved-guides` | Topic/subject search, visible bookmark filter, corrected active navigation |
| Guide reader | `/guides/generate` | Reading sections, section navigation, visible activity steps, inline concept model |
| Educator home and lesson creation | `/dashboard` for educators | Focused curriculum form, preparation stages, labelled inputs, exploration entry |
| Lesson library | `/lesson-plans` | Searchable, keyboard-accessible entries with real subject/grade/duration |
| Lesson detail | `/lesson-plans/:id` | Clear title, contextual model and detail/resource actions |
| Curriculum overview | `/lesson-plans/:id/edit` | Actual lesson retrieval, curriculum objectives and working resource-editor link |
| Resource library | `/lesson-resources` | Searchable, keyboard-accessible resource entries |
| Resource editing and exports | `/lesson-plans/:lessonPlanId/resources/edit` | Reader structure, contained disclosure, preserved edits/autosave/export controls |
| Concept exploration | `/explore` | Four reviewed interactive models with explanatory discovery challenges |
| Profile/access/language settings | `/settings` | Visible section navigation, retained profile editing and honest language availability |
| Legal and AI explanation | `/terms`, `/privacy-policy`, `/disclaimer` | Matching document surfaces with existing text preserved |
| Administration | `/admin/*` | Shared shell treatment, exact active dashboard link, template navigation and working return link |
| Missing page | unmatched routes | Helpful recovery links for authenticated or signed-out users |

## Components and styling

`components/design/AuthLayout.tsx` owns the account shell and equal-parts demonstration. `ScreenHeader.tsx` provides a shared page title and action layout. `SessionDiscoveries.tsx` surfaces session-only recognition without invented scores. `styles/screens.css` supplies responsive layouts and surfaces, loaded after the existing base and learning styles. All primary app screens retain the existing role-aware navigation. Dialog surfaces receive a consistent treatment while their existing consent and confirmation logic remains intact.

## Functional limits

Lesson metadata is read-only: the existing backend update service explicitly returns 501 because title and duration are not persisted as editable fields. The old hardcoded editor has been replaced with a real overview and a link to the existing teaching-resource editor. No metadata save action is offered. Resource content editing, autosave and exports retain their existing API paths.

Language switching and email/password changes are not newly implemented. Settings describes current availability. The old nonfunctional newsletter subscription, admin notification badge and misleading account-deletion menu action have been removed. No database/schema/API contract changes or deployment are part of this screen implementation.

## Verification and release

Run frontend tests, lint, TypeScript and production build from `apps/frontend`. Coverage includes account interactions, real lesson retrieval/resource navigation, library filtering, guide/lesson/resource integration, and existing auth/consent/bookmark/delete/export behaviour. Browser screenshots and small-screen visual checks were blocked by the managed localhost-origin policy; those checks remain necessary before release. Unit/component verification does not prove backend connectivity or visual layout.

📝 **Feedback prompt**: If you revise this output significantly before using it, please log it — `"Log feedback: dev-agent output was [approved / revised / rejected] — [what changed]"`. Logs go to `docs/agentic/feedback-log.md`.
