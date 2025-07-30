# Awade API Contracts Documentation (MVP)

## 🔐 Authentication

**Endpoint:** `POST /api/auth/login`

* **Description:** Authenticate a user and return access token
* **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
* **Response:**
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "email": "grace@awade.com",
    "full_name": "Grace John",
    "role": "educator",
    "country": "Nigeria",
    "region": "Lagos",
    "school_name": "Community School",
    "subjects": ["Mathematics", "Science"],
    "grade_levels": ["Grade 4", "Grade 5"],
    "languages_spoken": "English, Yoruba",
    "created_at": "2025-01-27T10:00:00Z",
    "last_login": "2025-01-27T10:00:00Z"
  }
}
```

---

## 👤 User Profile

**Endpoint:** `GET /api/user/profile`

* **Description:** Fetch logged-in user's profile info
* **Response:**
```json
{
  "user_id": 1,
  "email": "grace@awade.com",
  "full_name": "Grace John",
  "role": "educator",
  "country": "Nigeria",
  "region": "Lagos",
  "school_name": "Community School",
  "subjects": ["Mathematics", "Science"],
  "grade_levels": ["Grade 4", "Grade 5"],
  "languages_spoken": "English, Yoruba",
  "created_at": "2025-01-27T10:00:00Z",
  "last_login": "2025-01-27T10:00:00Z"
}
```

---

## 📝 Lesson Plan Generation

**Endpoint:** `POST /api/lesson-plans/generate`

* **Description:** Generate a comprehensive lesson plan with AI-powered 6-section structure
* **Request Body:**
```json
{
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "objectives": ["Understand fraction-decimal relationships"],
  "duration_minutes": 45,
  "local_context": "Rural school with limited resources, students familiar with local market activities",
  "language": "en",
  "cultural_context": "African",
  "country": "Nigeria",
  "author_id": 1
}
```
* **Response:**
```json
{
  "lesson_id": 123,
  "title": "Mathematics: Fractions and Decimals",
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "author_id": 1,
  "duration_minutes": 45,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z",
  "status": "draft"
}
```

**Endpoint:** `GET /api/lesson-plans/{lesson_id}/detailed`

* **Description:** Get detailed lesson plan with AI-generated 6-section content
* **Response:**
```json
{
  "lesson_id": 123,
  "title": "Mathematics: Fractions and Decimals",
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "author_id": 1,
  "duration_minutes": 45,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z",
  "status": "generated",
  "learning_objectives": "1. Students will understand fraction-decimal relationships\n2. Students will apply concepts using local market examples",
  "local_context_section": "Integrates local market activities, uses available resources like fruits and vegetables",
  "core_content": "Main concepts and knowledge breakdown...",
  "activities": "3-5 engaging activities with local resources...",
  "quiz": "5-8 assessment questions with answer key...",
  "related_projects": "2-3 community-linked projects..."
}
```

**Endpoint:** `GET /api/lesson-plans/{lesson_id}/export/pdf`

* **Description:** Export lesson plan as professional PDF
* **Response:** PDF file download

---

## 📚 Curriculum Management

### Curriculum Mapping

**Endpoint:** `GET /api/curriculum/maps`

* **Description:** Get curriculum mapping for subject and grade level
* **Query Parameters:**
  - `subject`: Subject area (e.g., "Mathematics")
  - `grade_level`: Grade level (e.g., "Grade 5")
  - `country`: Country for curriculum mapping (optional)
* **Response:**
```json
{
  "curriculum_id": 456,
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "standard_code": "CCSS.MATH.CONTENT.5.NF.A.1",
  "standard_description": "Add and subtract fractions with unlike denominators",
  "country": "Nigeria",
  "lesson_plan_id": 123,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

**Endpoint:** `POST /api/curriculum/maps`

* **Description:** Create new curriculum mapping
* **Request Body:**
```json
{
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "standard_code": "CCSS.MATH.CONTENT.5.NF.A.1",
  "standard_description": "Add and subtract fractions with unlike denominators",
  "country": "Nigeria",
  "lesson_plan_id": 123
}
```
* **Response:**
```json
{
  "curriculum_id": 789,
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "standard_code": "CCSS.MATH.CONTENT.5.NF.A.1",
  "standard_description": "Add and subtract fractions with unlike denominators",
  "country": "Nigeria",
  "lesson_plan_id": 123,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

**Endpoint:** `PUT /api/curriculum/maps/{id}`

* **Description:** Update curriculum mapping
* **Request Body:**
```json
{
  "topic": "Updated Topic",
  "standard_description": "Updated description",
  "lesson_plan_id": 124
}
```
* **Response:** Updated curriculum mapping object

**Endpoint:** `DELETE /api/curriculum/maps/{id}`

* **Description:** Delete curriculum mapping
* **Response:**
```json
{
  "message": "Curriculum mapping deleted successfully"
}
```

**Endpoint:** `GET /api/curriculum/standards`

* **Description:** Get all curriculum standards for a subject and grade level
* **Query Parameters:**
  - `subject`: Subject area
  - `grade_level`: Grade level
* **Response:**
```json
[
  {
    "curriculum_id": 456,
    "subject": "Mathematics",
    "grade_level": "Grade 5",
    "topic": "Fractions and Decimals",
    "standard_code": "CCSS.MATH.CONTENT.5.NF.A.1",
    "standard_description": "Add and subtract fractions with unlike denominators",
    "country": "Nigeria",
    "lesson_plan_id": 123,
    "created_at": "2025-01-27T10:00:00Z",
    "updated_at": "2025-01-27T10:00:00Z"
  }
]
```

**Endpoint:** `GET /api/curriculum/subjects`

* **Description:** Get all available subjects
* **Response:**
```json
{
  "subjects": ["Mathematics", "Science", "English", "Social Studies"]
}
```

**Endpoint:** `GET /api/curriculum/grade-levels`

* **Description:** Get all available grade levels
* **Query Parameters:**
  - `subject`: Filter by subject (optional)
* **Response:**
```json
{
  "grade_levels": ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"]
}
```

---

## 📚 Micro-Training Modules

**Endpoint:** `GET /api/modules`

* **Description:** List available training modules
* **Response:**
```json
[
  {
    "id": 1,
    "title": "Classroom Management Essentials",
    "duration": "5 min",
    "tags": ["discipline", "engagement"]
  },
  {
    "id": 2,
    "title": "Inclusive Teaching Practices",
    "duration": "7 min",
    "tags": ["equity", "accessibility"]
  }
]
```

---

## ✅ Bookmark Resource

**Endpoint:** `POST /api/bookmark`

* **Description:** Save a lesson or module to bookmarks
* **Request Body:**
```json
{
  "type": "lesson",  // or "module"
  "id": 12
}
```
* **Response:**
```json
{
  "status": "success",
  "message": "Resource bookmarked."
}
```

---

## 🔄 Sync/Offline Status

**Endpoint:** `GET /api/sync/status`

* **Description:** Return last sync time and offline readiness
* **Response:**
```json
{
  "last_synced": "2025-01-27T10:00:00Z",
  "resources_cached": true
}
```

---

## 📊 Lesson Plan Status Values

The lesson plan status follows this lifecycle:
- **draft**: Initial state after creation
- **generated**: AI has generated the 6-section content
- **edited**: Teacher has made modifications
- **reviewed**: Final review completed
- **exported**: Lesson plan has been exported
- **used_offline**: Lesson plan has been used in classroom
- **archived**: Lesson plan saved for future reuse 