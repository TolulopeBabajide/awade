# Lesson Plan Feature Architecture

This document describes the end-to-end architecture for the **Lesson Plan** feature in the Awade MVP, detailing components, data models, service interactions, and deployment considerations.

---

## 1. Overview

The Lesson Plan feature enables teachers to generate, edit, and export curriculum-aligned lesson plans using AI augmentation. Core flows include:

1. **Curriculum Mapping** (subject & grade → curriculum standard)
2. **AI Generation** (prompt templates → structured lesson output)
3. **Frontend Editing** (editable template UI)
4. **Persistence & Export** (save, PDF export, offline caching)

---

## 2. High-Level Components

| Layer          | Technology       | Responsibility                                              |
| -------------- | ---------------- | ----------------------------------------------------------- |
| **Frontend**   | React/Pug + JS   | UI for lesson inputs, AI suggestions, editing, export       |
| **API Layer**  | FastAPI          | REST endpoints for curriculum, generation, export           |
| **Business**   | Python services  | Curriculum mapping logic, prompt templating, PDF generation |
| **AI Module**  | OpenAI GPT-4     | Generates lesson content based on prompts                   |
| **Data Store** | PostgreSQL       | Stores lesson plan metadata, mapping caches                 |
| **Cache**      | IndexedDB/SQLite | Offline lesson plan & PDF storage in browser                |

---

## 3. Data Models

```python
# Pydantic models
class CurriculumMap(BaseModel):
    curriculum_id: int
    description: str

class LessonPrompt(BaseModel):
    subject: str
    grade_level: str
    topic: str
    objectives: List[str]
    local_context: Optional[str]

class LessonPlan(BaseModel):
    id: int
    title: str
    objectives: List[str]
    activities: List[str]
    resources: List[str]
    explanation: str  # AI rationale
    curriculum_id: int
    created_by: int  # user_id
    created_at: datetime
```

**Database Tables:**

* `curriculum_map` (id, subject, grade\_level, curriculum\_id, description)
* `lesson_plan` (id, user\_id, curriculum\_id, title, objectives, activities, resources, explanation, created\_at)
* `lesson_context` (plan\_id, input\_key, input\_value)
  *Stores teacher-provided local context entries.*

---

## 4. Service Flow

1. **Request Generation**

   * Frontend calls `POST /api/lesson/generate` with a `LessonPrompt` payload.
2. **Curriculum Mapping**

   * API invokes `curriculum_service.map(subject, grade_level)` → returns `CurriculumMap`.
3. **Prompt Assembly**

   * Business logic merges `LessonPrompt` + `CurriculumMap` into GPT prompt template.
4. **AI Call**

   * Send prompt to OpenAI; receive structured JSON response.
5. **Data Persistence**

   * Save new `lesson_plan` record and any `lesson_context` entries.
6. **Response to Frontend**

   * Return `LessonPlan` JSON for UI rendering.
7. **Export Flow**

   * On `GET /api/lesson/{id}/export/pdf`, service retrieves plan, renders PDF via `WeasyPrint` (or similar), streams file.
8. **Offline Caching**

   * Frontend intercepts API responses, stores JSON and exported PDF blobs in IndexedDB.

---

## 5. Sequence Diagram (Textual)

```
Teacher UI -> API: POST /api/lesson/generate
API -> Curriculum Service: map(subject, grade_level)
Curriculum Service -> API: CurriculumMap
API -> AI Module: generateLesson(prompt)
AI Module -> API: LessonPlan JSON
API -> Database: insert lesson_plan, lesson_context
API -> Teacher UI: return LessonPlan

Teacher UI -> API: GET /api/lesson/{id}/export/pdf
API -> Database: fetch lesson_plan
API -> PDF Service: render PDF
PDF Service -> API: PDF stream
API -> Teacher UI: download PDF
```

---

## 6. Deployment & Scaling

* **Backend:** Containerized FastAPI service behind NGINX; auto-scaling via Kubernetes.
* **AI Module:** Requests to OpenAI API; implement rate limiting and caching of common prompts.
* **Database:** PostgreSQL with read replicas for scaling read-heavy endpoints (curriculum lookup).
* **Frontend:** Static assets served via CDN; service worker for offline caching.

---

## 7. Security & Compliance

* **Auth & Access:** JWT tokens for secure API access; user\_id enforced on plan retrieval.
* **Data Privacy:** Only metadata stored server-side; exported PDFs contain no sensitive student data.
* **Input Validation:** Strict schema validation on all endpoints to prevent injection.

---

## 8. Implementation Status

### ✅ Completed
- Database schema for lesson plans (see `apps/backend/models.py`)
- Basic FastAPI structure
- PostgreSQL setup with secure credentials
- AI service integration framework

### 🚧 In Progress
- Curriculum mapping service
- Lesson plan generation endpoints
- Frontend lesson plan UI components

### 📋 Planned
- PDF export functionality
- Offline caching implementation
- Advanced AI prompt templates
- Curriculum database population

---

## 9. API Endpoints

### Core Lesson Plan Endpoints
```python
# Lesson Plan Generation
POST /api/lesson-plans/generate
GET /api/lesson-plans
GET /api/lesson-plans/{id}
PUT /api/lesson-plans/{id}
DELETE /api/lesson-plans/{id}

# Export & Download
GET /api/lesson-plans/{id}/export/pdf
GET /api/lesson-plans/{id}/export/docx

# Curriculum & Context
GET /api/curriculum/map
POST /api/lesson-plans/{id}/context
```

### Request/Response Examples
```json
// POST /api/lesson-plans/generate
{
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "objectives": ["Understand fraction-decimal relationships"],
  "local_context": "Rural school with limited resources"
}

// Response
{
  "id": 123,
  "title": "Understanding Fractions and Decimals",
  "objectives": ["..."],
  "activities": ["..."],
  "resources": ["..."],
  "explanation": "AI rationale for lesson structure...",
  "curriculum_id": 456,
  "created_at": "2025-07-10T16:00:00Z"
}
```

---

*This architecture ensures a robust, extensible, and teacher-centric lesson plan feature that aligns with Awade's core principles.*

---

**Last Updated:** 2025-07-10  
**Next Review:** 2025-08-10  
**Document Owner:** Backend Team  
**MCP Integration:** Available via `internal` server 