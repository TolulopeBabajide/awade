# Awade MVP Design Brief

## 1. Project Overview

Awade is an educator-centric AI platform aimed at enhancing teaching quality for African educators through:

* **AI-Assisted Lesson Planning:** Curriculum-aligned, editable lesson plans.
* **Micro-Training Modules:** Bite-sized professional development accessible via mobile.
* **Offline & Localization:** Support for low-bandwidth environments and local languages.
* **Transparency & Control:** Explainable AI suggestions with teacher override.

This MVP will validate core value: empowering teachers, not replacing them.

---

## 2. Design Goals

1. **Empathy & Usability:** Map to teachers' workflows; minimize learning curve.
2. **Inclusivity & Access:** Mobile-first, offline-capable, multilingual UI.
3. **Trust & Transparency:** Clear AI recommendations, editable and explainable.
4. **Contextual Relevance:** Align with local curricula and cultural practices.
5. **Iterative Learning:** Gather feedback to refine features rapidly.

---

## 3. Target Users & Scenarios

| Persona         | Scenario                                                      |
| --------------- | ------------------------------------------------------------- |
| Grace (Rural)   | Needs offline lesson plans and training modules on her phone. |
| Mr. Ade (Admin) | Monitors teacher progress and disseminates resources.         |
| Fatima (New)    | Seeks AI guidance and peer insights to innovate lessons.      |

---

## 4. Key User Needs

* **Structured Planning:** Fast generation of lesson outlines.
* **Relevant Training:** Quick modules on pedagogy and tech use.
* **Control Over AI:** Ability to accept or modify generated content.
* **Offline & Local:** Downloadable resources and language options.
* **Simplified Collaboration:** Bookmark and share best practices.

---

## 5. MVP Feature Scope

| Feature                        | Description                                                        |
| ------------------------------ | ------------------------------------------------------------------ |
| Lesson Plan Generator          | Input: subject, grade, objectives → AI-driven plan with rationale. |
| Training Module Library        | List of micro-modules with progress tracking.                      |
| AI Explanation & Edit Controls | Tooltip explanations; accept/edit/reject toggles.                  |
| Offline Mode                   | Cache selected plans/modules; sync indicator.                      |
| Multi-Language Support         | UI and content switcher for English and local languages.           |
| Saved Resources                | Bookmark lessons/modules; view saved list.                         |

---

## 6. Technical Considerations

* **Monorepo Structure:** Frontend (HTML/Pug or React), Backend (FastAPI), Shared AI logic.
* **AI Engine:** GPT-4 via OpenAI API plus rule-based personalization.
* **Data Storage:** PostgreSQL for user data; SQLite cache for offline.
* **Dev Tools:** Cursor Agent for rapid coding; Docker for local dev.

---

## 7. Testing & Validation

* **Functional:** Verify generation, editing, offline workflows.
* **Usability:** Remote think-aloud sessions; measure task completion time.
* **Performance:** Page load <2s on 3G; API latency <300ms.
* **Accessibility:** Mobile-first, WCAG AA compliance.

---

## 8. Success Metrics

* **Adoption:** 80% of pilot teachers generate ≥1 plan and complete ≥1 module.
* **Engagement:** Average of 2 sessions per week per user.
* **Satisfaction:** ≥4/5 rating on usability and AI trust in feedback surveys.


---

*Awade – Empowering educators with ethical, localized AI support.* 