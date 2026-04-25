# Awade: Full Codebase Review & Parent-Pivot Analysis
*Prepared April 6, 2026*

---

## 1. What Awade Is Today

Awade is an AI-powered lesson planning platform built for **African teachers**. The product helps educators generate curriculum-aligned lesson plans and resources tailored to their local context. The stack is a React + TypeScript frontend, FastAPI (Python) backend, PostgreSQL database, and Docker for containerization. AI generation is supported through both OpenAI and Gemini providers.

### Current User Journey
Sign Up → Dashboard (select Country / Curriculum / Subject / Grade / Topic) → Generate Lesson Plan → Edit → Export PDF or DOCX → Use in class.

### Current Routes
- `/` — Landing page (hero, features, footer)
- `/signup` `/login` `/reset-password` — Auth
- `/dashboard` — The core lesson-plan generator form
- `/lesson-plans` — List of created lesson plans
- `/lesson-plans/:id` — Plan detail and resource generation
- `/lesson-resources` — All generated resources
- `/settings` — Profile / security / language
- `/admin/*` — Full admin panel (users, curriculum, moderation, audit logs, templates)

### Current Data Model (simplified)
```
User (role: EDUCATOR | ADMIN | SUPER_ADMIN)
  └── LessonPlan
        ├── Context (local context text)
        └── LessonResource (AI-generated content, export format)

Country → Curriculum → CurriculumStructure (Subject + GradeLevel)
  └── Topic
        ├── LearningObjective
        └── TopicContent
```

### Design System
- **Palette:** Earthy green primary (#5f7e3a) + terracotta accent (#c46f52) + warm neutral backgrounds
- **Typography:** Poppins (headings) + Inter (body)
- **Component pattern:** Tailwind utility classes, no UI library
- **Layout:** Fixed left sidebar (desktop) + bottom mobile nav

---

## 2. What's Working Well

**Backend architecture is solid.** The FastAPI service is well-structured: clean separation of routers, schemas, services, and models. Security is taken seriously — rate limiting, SQL injection prevention, audit logging, input sanitization, and JWT auth with refresh token logic are all in place. This infrastructure is directly reusable for the parent pivot.

**Curriculum data model is a genuine asset.** The Country → Curriculum → Subject → GradeLevel → Topic hierarchy is precisely what a parent-focused product needs too. A parent helping their child in JSS 1 Mathematics in Nigeria navigates the exact same structure a teacher does. This does not need to be rebuilt.

**AI provider abstraction is well done.** The `packages/ai` module cleanly abstracts OpenAI and Gemini behind a common interface with caching. Swapping or extending prompts for a parent audience is straightforward.

**Admin panel is mature.** User management, curriculum editing, moderation, and audit logging are all implemented. This gives you operational control over the new audience from day one.

**Design tokens are strong.** The earthy green / terracotta palette is warm and approachable — well-suited for parents, not just professional educators.

---

## 3. Gaps and Pain Points (Current State)

**The dashboard UX is teacher-centric and form-heavy.** The current dashboard asks users to navigate Country → Curriculum → Subject → Grade → Topic across multiple dependent dropdowns before anything useful happens. For a teacher, this is a professional workflow. For a busy parent helping with homework at 8pm, it's a barrier.

**There is no child concept in the data model.** The platform only knows about the logged-in user. A parent needs to manage one or more child profiles — each with their own grade level, school, and subjects. This is the most significant structural gap for the pivot.

**Prompts are written for classroom delivery, not home support.** The current `COMPREHENSIVE_LESSON_RESOURCE_PROMPT` generates content with "step-by-step instructions for classroom delivery," "class assessment tasks," and "community projects." A parent helper prompt needs to explain concepts in plain language, suggest home activities with household materials, and tell the parent how to help — not create a lesson plan.

**The landing page speaks only to teachers.** "Transform Your Teaching," "AI-powered lesson planning designed specifically for African educators," "large class sizes, limited resources" — all of this messaging is irrelevant to a parent. The value proposition needs to be rewritten from scratch.

**The `UserRole` enum has no PARENT role.** The entire permission system — including what the admin panel shows — assumes users are educators or admins.

**Code quality: some duplication and `any` types.** The `DashboardPage.tsx` and `LessonPlansPage.tsx` both contain duplicated click-outside handlers and user menu logic that could be extracted. Several state types are typed as `any[]`. This is manageable but worth cleaning up during the refactor.

**No state management library.** State is managed locally per-page with `useState`. This works now, but as a parent product grows to include child profiles, progress, and homework sessions, shared global state (Zustand or React Query) will become necessary.

---

## 4. What the Parent Pivot Requires

### New Core Concept: The Child Profile
Every parent needs to register one or more children. A child profile holds:
- Name and age
- School name
- Country / Curriculum / Grade Level (the existing hierarchy handles this)
- Subjects they need help with

This replaces the current per-lesson-plan curriculum selection. The parent sets it once on their child's profile; the dashboard then adapts to that child's context.

### Revised User Journey
Sign Up (as a parent) → Add Child Profile → Dashboard shows child's curriculum topics → Parent selects topic → Gets a "How to Help" guide → Can save, revisit, and track what topics they've covered.

### New AI Output: "How to Help" Guide
Instead of a teacher-facing lesson resource, the AI should generate:
- **Simple explanation** of the topic in plain language for a non-expert adult
- **Home activity** — something the parent and child can do together using household items
- **Conversation starters** — questions to ask their child to check understanding
- **Common mistakes** — what children typically get wrong on this topic, and how to address it
- **Curriculum context** — what this topic leads to next, so the parent understands the bigger picture

### What Changes, What Stays

| Area | Action |
|---|---|
| User model | Add `PARENT` role; add `ChildProfile` table linked to User |
| Landing page | Full rewrite — new headline, new features, new testimonials |
| Dashboard | Replace form-heavy generator with child-selector + topic browser |
| AI prompts | New "parent helper" prompt template alongside existing teacher prompt |
| Sidebar nav | Replace "Lesson Plans / Resources" with "My Children / Topics / Saved Guides" |
| Backend API | Add `/children` endpoint family; extend auth for parent role |
| Admin panel | Add parent/child management views |
| Design system | Keep — the palette and typography work for this audience |
| Curriculum data | Keep — it's directly reusable |
| Auth system | Keep — JWT, refresh tokens, security all carry over |
| Export (PDF/DOCX) | Keep — parents may want to print guides |
| Docker / infra | Keep entirely |

---

## 5. Recommended Refactor Approach

### Phase 1 — Data model and auth (backend)
Add the `PARENT` role to `UserRole`. Create a `ChildProfile` model:
```
ChildProfile
  child_id (PK)
  parent_id (FK → users.user_id)
  name
  school_name
  country_id (FK → countries)
  curricula_id (FK → curricula)
  grade_level_id (FK → grade_levels)
  created_at
```
Add `/api/children` CRUD endpoints. Ensure the parent only sees their own children's data.

### Phase 2 — New AI prompt
Write a `PARENT_HELPER_PROMPT` in `packages/ai/prompts.py` that generates the "How to Help" guide format described above. Keep the existing teacher prompt untouched — you may want to serve both audiences eventually.

### Phase 3 — Landing page
Rewrite the landing page entirely. Suggested headline direction: *"Understand what your child is learning. Help them at home."* New features section should lead with: "Know their curriculum," "Help with homework," "Track what you've covered."

### Phase 4 — Dashboard and navigation
Replace the current multi-step dropdown form with a child-selector dashboard:
- If a parent has no children: prompt to add one
- If they have children: show a child card per child
- Clicking a child shows their current curriculum topics grouped by subject
- Clicking a topic generates the parent helper guide

The sidebar nav items should become: Home, My Children, Saved Guides, Settings.

### Phase 5 — Frontend state management
Introduce React Query for data fetching (children, topics, guides). This removes the duplicated loading/error state boilerplate spread across every page and makes caching child profiles straightforward.

---

## 6. What to Preserve and Protect

- The curriculum data already seeded in the database is valuable. Do not reset it.
- The admin panel's curriculum management tools are what you'll use to keep curriculum data accurate for the parent pivot. Keep them.
- The audit log and moderation infrastructure protects you from AI-generated content issues. Keep it active even for parent-facing content.
- The export service (WeasyPrint PDF / DOCX) is immediately useful — parents may want to print guides to use offline.

---

## 7. Risks to Plan For

**Re-registration friction.** If any teachers currently use the platform and you pivot fully, they'll need to be migrated or the platform will need to support both roles simultaneously. The cleanest path is keeping the `EDUCATOR` role active and routing users to different experiences based on their role.

**AI content quality for non-educators.** The "how to help" content must be genuinely useful to a non-expert parent, not a rephrased lesson plan. Prompt iteration and content review will be important early work.

**Curriculum accuracy.** Parents will trust the curriculum content to be correct for their child's school system. The existing curriculum data needs to be verified and kept current. This is an ongoing editorial responsibility, not just a technical one.

**Scope creep.** The roadmap already lists gamification, student-facing experiences, offline sync, and progress tracking. For the pivot to succeed, focus the first version on a single, tight loop: parent finds topic → gets guide → helps child. Everything else can follow.

---

## Summary

Awade's backend, curriculum model, AI infrastructure, and design system are all strong foundations that transfer directly to a parent-facing product. The work is concentrated in three areas: adding the child profile data model, rewriting the AI prompt to produce parent-appropriate content, and refactoring the frontend to replace the teacher workflow with a parent-friendly child/topic browser. The landing page and onboarding also need a full rewrite to speak to the new audience. None of this requires starting over — it's a targeted pivot on top of a solid base.
