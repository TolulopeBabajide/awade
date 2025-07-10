# Lesson Plan Feature Architecture

This document describes the end-to-end architecture for the **Lesson Plan** feature in the Awade MVP, detailing components, data models, service interactions, and deployment considerations.

---

## 1. Overview

The Lesson Plan feature enables teachers to generate, edit, and export curriculum-aligned lesson plans using AI augmentation with a structured 6-section format. Core flows include:

1. **Curriculum Mapping** (subject & grade → curriculum standard)
2. **AI Generation** (prompt templates → structured 6-section lesson output)
3. **Local Context Integration** (local environment, resources, and community needs)
4. **Frontend Editing** (editable template UI)
5. **Persistence & Export** (save, PDF export, offline caching)

### 6-Section Lesson Plan Structure

Each generated lesson plan follows a consistent 6-section format:

1. **Learning Objectives** (3-5 measurable objectives aligned with curriculum)
2. **Local Context** (local environment integration, real-life examples, local resources)
3. **Core Content** (main concepts and knowledge breakdown)
4. **Activities** (3-5 engaging activities using locally available resources)
5. **Quiz** (5-8 assessment questions with answer key)
6. **Related Projects** (2-3 community-linked projects where applicable)

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
    objectives: Optional[List[str]]  # AI generates if not provided
    local_context: Optional[str]
    duration_minutes: int
    language: str
    cultural_context: str

class LessonPlan(BaseModel):
    id: int
    title: str
    subject: str
    grade_level: str
    topic: str
    objectives: List[str]
    learning_objectives: str  # AI-generated section
    local_context: str       # AI-generated section
    core_content: str        # AI-generated section
    activities: str          # AI-generated section
    quiz: str               # AI-generated section
    related_projects: str   # AI-generated section
    curriculum_id: int
    created_by: int  # user_id
    created_at: datetime
```

**Database Tables:**

* `curriculum_map` (curriculum_id, subject, grade_level, curriculum_standard, description, country, created_at)
* `lesson_plan` (lesson_id, title, subject, grade_level, author_id, context_description, duration_minutes, status, created_at, updated_at)
* `lesson_context` (context_id, lesson_id, context_key, context_value, created_at)
  *Stores teacher-provided local context entries for lesson customization.*

---

## 4. Service Flow

1. **Request Generation**

   * Frontend calls `POST /api/lesson-plans/generate` with a `LessonPrompt` payload.
2. **Curriculum Mapping**

   * API invokes `curriculum_service.map(subject, grade_level, country)` → returns `CurriculumMap`.
3. **Prompt Assembly**

   * Business logic merges `LessonPrompt` + `CurriculumMap` + local context into structured GPT prompt template.
4. **AI Call**

   * Send prompt to OpenAI; receive structured 6-section response.
5. **Section Extraction**

   * Parse AI response into structured sections (Learning Objectives, Local Context, Core Content, Activities, Quiz, Related Projects).
6. **Data Persistence**

   * Save new `lesson_plan` record and any `lesson_context` entries.
7. **Response to Frontend**

   * Return `LessonPlan` JSON for UI rendering.
8. **Export Flow**

   * On `GET /api/lesson-plans/{id}/export/pdf`, service retrieves plan, renders PDF via `WeasyPrint`, streams file.
9. **Offline Caching**

   * Frontend intercepts API responses, stores JSON and exported PDF blobs in IndexedDB.

---

## 5. Sequence Diagram (Textual)

```
Teacher UI -> API: POST /api/lesson-plans/generate
API -> Curriculum Service: map(subject, grade_level, country)
Curriculum Service -> API: CurriculumMap
API -> AI Module: generateLesson(prompt with local context)
AI Module -> API: Structured 6-section response
API -> Section Parser: extract sections
API -> Database: insert lesson_plan, lesson_context
API -> Teacher UI: return LessonPlan

Teacher UI -> API: GET /api/lesson-plans/{id}/detailed
API -> Database: fetch lesson_plan with sections
API -> Teacher UI: return detailed lesson plan

Teacher UI -> API: GET /api/lesson-plans/{id}/export/pdf
API -> Database: fetch lesson_plan
API -> PDF Service: render PDF with sections
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
- Database schema for lesson plans with curriculum mapping (see `apps/backend/models.py`)
- FastAPI structure with comprehensive endpoints
- PostgreSQL setup with secure credentials
- AI service integration with structured 6-section generation
- Curriculum mapping service with country-specific standards
- PDF export functionality using WeasyPrint
- Local context integration and customization
- Section extraction and parsing methods
- Enhanced AI prompts for local environment integration

### 🚧 In Progress
- Frontend lesson plan UI components
- Advanced curriculum database population
- Offline caching implementation

### 📋 Planned
- Real-time collaboration features
- Advanced analytics and insights
- Integration with external curriculum databases
- Mobile app development

---

## 9. API Endpoints

### Core Lesson Plan Endpoints
```python
# Lesson Plan Generation & Management
POST /api/lesson-plans/generate
GET /api/lesson-plans
GET /api/lesson-plans/{id}
GET /api/lesson-plans/{id}/detailed
PUT /api/lesson-plans/{id}
DELETE /api/lesson-plans/{id}

# Export & Download
GET /api/lesson-plans/{id}/export/pdf

# Curriculum Management
GET /api/curriculum/map
GET /api/curriculum/standards
GET /api/curriculum/subjects
GET /api/curriculum/grade-levels
POST /api/curriculum/standards

# Context Management
POST /api/lesson-plans/{id}/context
GET /api/lesson-plans/{id}/context
```

### Request/Response Examples
```json
// POST /api/lesson-plans/generate
{
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "objectives": ["Understand fraction-decimal relationships"], // Optional
  "duration_minutes": 45,
  "local_context": "Rural school with limited resources, students familiar with local market activities",
  "language": "en",
  "cultural_context": "African",
  "country": "Nigeria",
  "author_id": 1
}

// Basic Response
{
  "lesson_id": 123,
  "title": "Mathematics: Fractions and Decimals",
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "author_id": 1,
  "context_description": "Rural school with limited resources",
  "duration_minutes": 45,
  "created_at": "2025-07-10T16:00:00Z",
  "updated_at": "2025-07-10T16:00:00Z",
  "status": "draft"
}

// GET /api/lesson-plans/{id}/detailed Response
{
  "lesson_id": 123,
  "title": "Mathematics: Fractions and Decimals",
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "learning_objectives": "1. Students will understand fraction-decimal relationships\n2. Students will apply concepts using local market examples",
  "local_context": "Integrates local market activities, uses available resources like fruits and vegetables",
  "core_content": "Main concepts and knowledge breakdown...",
  "activities": "3-5 engaging activities with local resources...",
  "quiz": "5-8 assessment questions with answer key...",
  "related_projects": "2-3 community-linked projects..."
}
```

---

*This architecture ensures a robust, extensible, and teacher-centric lesson plan feature that aligns with Awade's core principles.*

---

**Last Updated:** 2025-07-10  
**Next Review:** 2025-08-10  
**Document Owner:** Backend Team  
**MCP Integration:** Available via `internal` server 