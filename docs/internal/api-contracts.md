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
  "token_type": "bearer"
}
```

---

## 👤 User Profile

**Endpoint:** `GET /api/user/profile`

* **Description:** Fetch logged-in user's profile info
* **Response:**
```json
{
  "id": 1,
  "name": "Grace John",
  "email": "grace@awade.com",
  "language": "en",
  "grade_level": "Secondary",
  "region": "Nigeria"
}
```

---

## 📝 Lesson Plan Generation

**Endpoint:** `POST /api/lesson/generate`

* **Description:** Generate a lesson plan using AI and curriculum inputs
* **Request Body:**
```json
{
  "subject": "Mathematics",
  "grade_level": "JSS2",
  "topic": "Fractions",
  "learning_objectives": ["Identify types of fractions", "Compare fractions"]
}
```
* **Response:**
```json
{
  "lesson_title": "Understanding Fractions",
  "objectives": ["Identify types of fractions", "Compare fractions"],
  "activities": ["Introduction with real-life objects", "Group exercise"],
  "resources": ["Flashcards", "Chalkboard"],
  "explanation": "This plan is based on WAEC curriculum and local pedagogy."
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
  "last_synced": "2025-07-20T14:33:21Z",
  "resources_cached": true
}
``` 