# WCAG 2.1 AA Audit — Parent Flow

> **Issue**: AWD-L-03 — Run WCAG 2.1 AA audit on parent flow, file specific items
> **Auditor**: Lead Dev Agent (automated)
> **Date**: 2026-04-27
> **Standard**: WCAG 2.1, conformance level **AA**

---

## 1. Scope

Pages and components covered:

| File | Lines | Surface |
|---|---|---|
| `apps/frontend/src/pages/ParentDashboardPage.tsx` | 367 | Authenticated parent home |
| `apps/frontend/src/pages/ChildrenPage.tsx` | 264 | Child profile management |
| `apps/frontend/src/pages/ParentOnboardingPage.tsx` | 320 | First-run onboarding form |
| `apps/frontend/src/pages/GuideViewPage.tsx` | 372 | "How to Help" guide reader |
| `apps/frontend/src/pages/SavedGuidesPage.tsx` | 189 | Bookmarked / generated guides list |
| `apps/frontend/src/components/AddChildModal.tsx` | 271 | Add/edit child modal |
| `apps/frontend/src/components/ConsentModal.tsx` | 144 | COPPA consent modal |

Out of scope: educator pages, landing page, admin panel, Sidebar/MobileNavigation chrome (re-used across roles — should be audited separately).

---

## 2. Methodology

Static analysis against WCAG 2.1 AA success criteria, focused on:

1. **Perceivable** — colour contrast (1.4.3), use of colour (1.4.1), images of text (1.4.5), text resize (1.4.4), reflow (1.4.10), non-text contrast (1.4.11).
2. **Operable** — keyboard access (2.1.1, 2.1.2), focus visible (2.4.7), focus order (2.4.3), bypass blocks (2.4.1), page titled (2.4.2), link purpose (2.4.4), headings & labels (2.4.6).
3. **Understandable** — language of page (3.1.1), labels or instructions (3.3.2), error identification (3.3.1), error suggestion (3.3.3).
4. **Robust** — name/role/value (4.1.2), status messages (4.1.3), parsing (4.1.1).

Contrast ratios computed against the Tailwind palette in `apps/frontend/tailwind.config.js`. No dynamic states (live device test, automated axe scan, screen-reader pass-through) were performed in this pass — see §5 follow-ups.

---

## 3. Summary

| Severity | Count |
|---|---|
| 🔴 Blocker (AA failure, blocks shipping) | 0 |
| 🟠 High (AA failure, common path) | 4 |
| 🟡 Medium (AA failure, edge path) or AAA gap with parent-flow impact | 5 |
| 🟢 Low (best-practice / minor) | 4 |
| **Total findings** | **13** |

No level-A or level-AA failures block the parent flow today, but four High findings should be fixed before any external accessibility certification.

---

## 4. Findings

Each finding is keyed `A11Y-PF-##` so it can be referenced from the backlog. WCAG references use the SC number (e.g. 1.4.3) followed by level.

### 🟠 High

#### A11Y-PF-01 — Primary CTA contrast 3.66:1 — FAIL **WCAG 1.4.3 (AA, normal text)**

**Where**:
- `apps/frontend/src/pages/ParentDashboardPage.tsx:160-166, 189-196` ("Add Your Child" / "Add Child")
- `apps/frontend/src/pages/ChildrenPage.tsx:92-98, 139-146` ("Add Child" / "Add Your First Child")
- `apps/frontend/src/pages/ParentOnboardingPage.tsx:286-302` ("Get Started")
- `apps/frontend/src/components/ConsentModal.tsx:122-130` ("I Agree — Add a Child")
- `apps/frontend/src/components/AddChildModal.tsx:255-264` ("Add Child" / "Save Changes")

**Detail**: `bg-accent-600` (`#c46f52`) with `text-white` is the primary CTA across the parent flow. Computed contrast = **3.66:1**, below the 4.5:1 required for normal-weight text. Tailwind's `font-semibold` is `font-weight: 600`, which does not qualify as "bold" under WCAG's large-text definition (which requires 700+ at 14pt or 18pt regular). At 16px / weight 600, this remains normal text under WCAG.

**Fix**: shift the default CTA background one step darker. `accent-700` (`#a55a42`) gives ~5.07:1 against white and is already the hover state, so swap default ↔ hover (default = accent-700; hover = accent-800). Verify visual identity sign-off from Tolu before applying. Alternative: tighten `accent-600` itself in `tailwind.config.js` to a darker brown (e.g. `#b25e44`) so all uses are fixed in one change.

---

#### A11Y-PF-02 — Icon-only action buttons fall below non-text contrast minimum **WCAG 1.4.11 (AA)**

**Where**:
- `apps/frontend/src/pages/ParentDashboardPage.tsx:251-265` (Edit / Trash icons on child selector cards)
- `apps/frontend/src/pages/GuideViewPage.tsx:179-210` (Download / WhatsApp / Bookmark in top bar)

**Detail**: icons use `text-gray-400` (`#9ca3af`) on white — computed contrast **2.53:1**. WCAG 1.4.11 requires **3:1** for graphical objects that convey information. The Edit/Trash buttons in `ParentDashboardPage` carry meaning (only `title=` provides a tooltip, no visible label), so they qualify as informational graphics.

**Fix**: bump default icon colour to `text-gray-500` (`#6b7280` → 4.86:1) or `text-gray-600`. Hover states (`hover:text-primary-600` etc.) already pass.

---

#### A11Y-PF-03 — `AddChildModal` is missing dialog semantics **WCAG 4.1.2 (AA)**

**Where**: `apps/frontend/src/components/AddChildModal.tsx:122-127`

**Detail**: the wrapping `<div>` has no `role="dialog"`, no `aria-modal="true"`, and no `aria-labelledby`. Screen-reader users have no signal that a modal has opened, no announcement of its title ("Add Your Child" / "Edit Child Profile"), and no constraint that focus is now in a modal context. `ConsentModal` does this correctly — `AddChildModal` should mirror it.

**Fix** (mirror lines 35-40 + 47-53 of `ConsentModal.tsx`):
```tsx
<div
  className="fixed inset-0 ... "
  role="dialog"
  aria-modal="true"
  aria-labelledby="add-child-modal-title"
  onClick={onClose}
>
  <div className="..." onClick={e => e.stopPropagation()}>
    <div className="flex items-center justify-between ...">
      <h2 id="add-child-modal-title" className="...">
        {editData ? 'Edit Child Profile' : 'Add Your Child'}
      </h2>
```

Same modal also lacks Escape-key dismiss and focus-trap (see A11Y-PF-08).

---

#### A11Y-PF-04 — Topic action cards reveal label only on hover (keyboard users miss it) **WCAG 1.4.13 (AA), 2.1.1 (A)**

**Where**: `apps/frontend/src/pages/ParentDashboardPage.tsx:319-332`

**Detail**: each topic button shows `"Get 'How to Help' guide →"` with `opacity-0 group-hover:opacity-100`. A keyboard user tabbing onto the button never sees the prompt — `group-focus-within` is not applied. Worse, the topic text alone (`{topic.topic_title}`) is the only accessible name; there's no `aria-label` describing the action ("Generate guide for X").

**Fix**: change the conditional class to `opacity-0 group-hover:opacity-100 group-focus-within:opacity-100` and add `aria-label={`Generate "How to Help" guide for ${topic.topic_title}`}` on the `<button>`. Same pattern applies to the SavedGuides cards (`SavedGuidesPage.tsx:158-176`).

---

### 🟡 Medium

#### A11Y-PF-05 — Required-field indication relies on colour + glyph only **WCAG 1.4.1 (A) / 3.3.2 (A)**

**Where**: `apps/frontend/src/pages/ParentOnboardingPage.tsx:167-169`, `apps/frontend/src/components/AddChildModal.tsx:145`

**Detail**: required name field uses `Child's Name <span class="text-red-500">*</span>` (or `*` literal in modal). Screen readers announce "asterisk" with no semantic meaning, and users with red/green colour blindness may miss the cue. The field also lacks `required` / `aria-required="true"`.

**Fix**: add `required aria-required="true"` to the `<input>` and append a visually-hidden `(required)` to the label:
```tsx
<label className="...">
  Child's Name
  <span className="text-red-500" aria-hidden="true">*</span>
  <span className="sr-only"> (required)</span>
</label>
```

---

#### A11Y-PF-06 — Inline form errors are not announced to assistive tech **WCAG 4.1.3 (AA), 3.3.1 (A)**

**Where**:
- `apps/frontend/src/pages/ParentOnboardingPage.tsx:161-163` (form-level error banner)
- `apps/frontend/src/components/AddChildModal.tsx:139-141`
- `apps/frontend/src/pages/ChildrenPage.tsx:104-108` (delete-error banner)

**Detail**: error messages are rendered into a static `<div className="bg-red-50 ...">…</div>`. They appear after a failed submit, but with no `role="alert"`, `aria-live="polite"`, or `aria-live="assertive"`, screen readers do not announce them. The user has to manually navigate to find the error. `ConsentModal` already does this correctly (line 116) — propagate the pattern.

**Fix**: add `role="alert"` (which implies `aria-live="assertive"`) to each error container. For loading states that produce status text ("Generating your guide…", `GuideViewPage.tsx:104-107`), wrap in `<div role="status" aria-live="polite">`.

---

#### A11Y-PF-07 — Form inputs do not surface `aria-invalid` after server validation **WCAG 3.3.1 (A) / 4.1.2 (AA)**

**Where**: `apps/frontend/src/pages/ParentOnboardingPage.tsx:170-191` (name/age), `apps/frontend/src/components/AddChildModal.tsx:146-167`

**Detail**: when `setError("Please enter your child's name")` fires, the `<input>` is not flagged as invalid programmatically. Screen-reader users cannot tell *which* field failed. Browser-native validation messaging is also absent (no `pattern`, `minlength`, `required`).

**Fix**: track an `invalidFields: Set<string>` in component state and set `aria-invalid={invalidFields.has('name')}` plus `aria-describedby="name-error"` on the input, with the error text rendered into `<p id="name-error" role="alert">`.

---

#### A11Y-PF-08 — Modals lack focus management (no initial focus, no trap, no Escape) **WCAG 2.4.3 (A) / 2.1.2 (A)**

**Where**:
- `apps/frontend/src/components/AddChildModal.tsx`
- `apps/frontend/src/components/ConsentModal.tsx`

**Detail**: when either modal opens, focus stays on the triggering button. A sighted keyboard user can Tab into the modal, but a screen-reader user is not told a dialog has opened (compounded by A11Y-PF-03 for `AddChildModal`). Tab can also escape past the dialog into the page behind. Escape does not close.

`AddChildModal` does have `autoFocus` on the name input (line 152), which moves focus *but* leaves no trap — Shift+Tab from name escapes back into the page. `ConsentModal` puts no initial focus.

**Fix**: introduce a `useFocusTrap(ref)` hook (or adopt `@headlessui/react` `Dialog` which handles trap, Escape, and `aria-modal` for free). Minimum bar: on mount, focus the dialog title or first interactive element; bind Escape to call `onCancel/onClose`.

---

#### A11Y-PF-09 — Skip-to-main-content link missing **WCAG 2.4.1 (A)**

**Where**: all parent flow pages (rendered through `ParentDashboardPage`, `ChildrenPage`, `ParentOnboardingPage`, `GuideViewPage`, `SavedGuidesPage`)

**Detail**: the `Sidebar` contains primary navigation but there is no skip link to bypass it. A keyboard-only user must Tab through every nav item on every page load before reaching the page's content.

**Fix**: at the top of the layout chrome (likely `Sidebar.tsx` or a shared `<AppLayout>`), add an `sr-only focus:not-sr-only` skip link before the `<nav>`:
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-white px-4 py-2 rounded shadow z-50">
  Skip to main content
</a>
```
Then add `id="main-content" tabIndex={-1}` to each page's `<main>` element.

---

### 🟢 Low

#### A11Y-PF-10 — Visible focus rings rely entirely on browser defaults **WCAG 2.4.7 (AA)**

**Where**: every `<button>` in the parent flow that uses raw utility classes rather than the `.btn-primary/.btn-accent` classes defined in `apps/frontend/src/index.css:77-89`.

**Detail**: `index.css` defines composed button classes with `focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2` — but the parent flow pages reach for utility classes directly and never include `focus:` states. `grep -c "focus:" apps/frontend/src/pages/{Parent,Children,Guide,SavedGuides}*.tsx` returns `0` for all five pages. Browser-default focus outlines satisfy AA in most browsers, but Safari macOS produces a faint ring on coloured buttons that is hard to see on `bg-accent-600`. The risk is borderline AA, hence Low rather than High.

**Fix**: either migrate the CTAs to use the existing `.btn-accent` / `.btn-primary` component classes, or add a single project-level rule (e.g. in `index.css` `@layer base`):
```css
button:focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}
```

---

#### A11Y-PF-11 — `<nav>` elements lack `aria-label` to disambiguate **WCAG 1.3.1 (A) / 4.1.2 (AA)**

**Where**: `apps/frontend/src/components/Sidebar.tsx:71`, presumably also `MobileNavigation.tsx`

**Detail**: each `<nav>` has no `aria-label` or `aria-labelledby`. When a user pulls a screen-reader landmarks list, both navs read as "navigation" with no way to distinguish them. WCAG SC 1.3.1 (info & relationships) is satisfied, but the experience is poor.

**Fix**: `<nav aria-label="Primary">` for `Sidebar`, `<nav aria-label="Mobile primary">` for `MobileNavigation`. Add `aria-current="page"` to whichever link matches `currentPage`.

---

#### A11Y-PF-12 — Touch targets in `ParentDashboardPage` action buttons fall below 44×44 px **WCAG 2.5.5 (AAA, recommended)**

**Where**: `apps/frontend/src/pages/ParentDashboardPage.tsx:251-265`

**Detail**: Edit/Trash buttons inside the child selector card use `<FaEdit className="w-3 h-3" />` (12px icon) with **no padding** on the `<button>` — effective hit target is ~12×12 px. WCAG 2.5.5 (Target Size) at AAA requires 44×44; even AA-leaning best practice is 24×24. The same buttons on `ChildrenPage.tsx:172-188` correctly use `p-2 rounded-lg` (~32px target).

**Fix**: add `p-2 rounded-lg` to the Edit/Trash buttons in `ParentDashboardPage` for parity with `ChildrenPage`. Stays within the existing card layout.

---

#### A11Y-PF-13 — `<select>` and `<input>` field labels not programmatically associated **WCAG 1.3.1 (A) / 3.3.2 (A) — borderline pass**

**Where**: `apps/frontend/src/pages/ParentOnboardingPage.tsx:165-254`, `apps/frontend/src/components/AddChildModal.tsx:144-227`

**Detail**: every `<label>` is a sibling of its `<input>` / `<select>` rather than wrapping it (or using `htmlFor`). It works visually because each label is the immediately preceding sibling, but semantically the association depends on browser heuristics. Adding `htmlFor` + `id` is a one-line per-field change that turns this from a "browsers usually do the right thing" pattern into a guaranteed pass.

**Fix**: assign `id="child-name"` (etc.) to each input and `htmlFor="child-name"` to each label. Same change for ChildrenPage's `confirm()` calls — those are browser dialogs, no fix needed there.

---

## 5. Recommendations (next passes)

The static audit above should be followed by:

1. **axe-core CI run** — wire `@axe-core/react` or `jest-axe` into the existing vitest suite; assert zero AA violations on each parent-flow page render. Suggested as `M-effort` follow-up.
2. **Screen-reader walkthrough** — VoiceOver (macOS) and TalkBack (Android) pass over `ParentDashboard → AddChild → ConsentModal → GuideView` to validate fixes for A11Y-PF-03/06/08 work end to end.
3. **Real-device keyboard test** — verify focus order, focus visibility, and skip-link behaviour after the fixes land.
4. **Touch-target audit on real Android** — bundles with the existing AWD-M-19 mobile audit.
5. **Reduced-motion check** — `animate-spin` loaders honour `prefers-reduced-motion: reduce`? Currently no `motion-reduce:` overrides; outside this pass's scope but worth tracking.

---

## 6. Backlog entries to file

This audit closes AWD-L-03. The 13 findings should be filed as:

| New ID | Severity | Source finding | Effort |
|---|---|---|---|
| AWD-H-52 | 🟠 High | A11Y-PF-01 (CTA contrast 3.66:1) | S |
| AWD-H-53 | 🟠 High | A11Y-PF-02 (icon contrast 2.53:1) | S |
| AWD-H-54 | 🟠 High | A11Y-PF-03 (AddChildModal dialog semantics) | S |
| AWD-H-55 | 🟠 High | A11Y-PF-04 (hover-only topic prompt + missing aria-label) | S |
| AWD-M-53 | 🟡 Medium | A11Y-PF-05 (required-field indicator) | S |
| AWD-M-54 | 🟡 Medium | A11Y-PF-06 (inline error not announced) | S |
| AWD-M-55 | 🟡 Medium | A11Y-PF-07 (aria-invalid not surfaced) | S |
| AWD-M-56 | 🟡 Medium | A11Y-PF-08 (modal focus management) | M |
| AWD-M-57 | 🟡 Medium | A11Y-PF-09 (skip-to-main-content) | S |
| AWD-L-13 | 🟢 Low | A11Y-PF-10 (focus-visible defaults) | S |
| AWD-L-14 | 🟢 Low | A11Y-PF-11 (nav aria-label / aria-current) | S |
| AWD-L-15 | 🟢 Low | A11Y-PF-12 (dashboard touch targets) | S |
| AWD-L-16 | 🟢 Low | A11Y-PF-13 (label htmlFor association) | S |

These IDs are assigned in this commit's `docs/agentic/backlog.md` patch.
