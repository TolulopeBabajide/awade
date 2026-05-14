# Awade API Documentation

> **Last updated: 2026-04-26**
> **For detailed endpoint contracts and example payloads, see the OpenAPI specification at `/docs` when running the server (development only — disabled in production).**

## Overview

The Awade API provides RESTful endpoints for AI-powered lesson planning (educators) and "How to Help" parent guides (parents). Built with FastAPI, it offers automatic OpenAPI documentation and type safety.

Two user roles are supported: `EDUCATOR` and `PARENT`. Most endpoints are role-gated — requests using the wrong role receive `403 Forbidden`.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.awade.org` (when deployed)

## 📚 API Endpoints

### Health & Status

#### GET `/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "awade-api"
}
```

### Lesson Planning

#### POST `/api/lesson-plans/generate`
Generate an AI-powered lesson plan with 6-section structure.

**Request Body:**
```json
{
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "topic": "Fractions and Decimals",
  "user_id": 1
}
```

**Response:**
```json
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
```



#### GET `/api/lesson-plans`
Retrieve all saved lesson plans.

**Response:**
```json
[
  {
    "id": "lp_001",
    "title": "Introduction to Fractions",
    "subject": "Mathematics",
    "grade": "Grade 4",
    // ... other fields
  }
]
```

#### GET `/api/lesson-plans/{plan_id}`
Retrieve a specific lesson plan by ID.

**Parameters:**
- `plan_id` (string): Unique lesson plan identifier

### Lesson Resources

#### POST `/api/lesson-plans/{lesson_id}/resources/generate`
Generate AI-powered lesson resources for a lesson plan.

**Request Body:**
```json
{
  "lesson_plan_id": 123,
  "user_id": 1,
  "context_input": "Optional context for AI generation",
  "export_format": "pdf"
}
```

#### GET `/api/lesson-plans/{lesson_id}/resources`
Retrieve all lesson resources for a lesson plan.

#### GET `/api/lesson-plans/resources/{resource_id}`
Retrieve a specific lesson resource by ID.

#### PUT `/api/lesson-plans/resources/{resource_id}/review`
Update a lesson resource with user edits.

**Request Body:**
```json
{
  "user_edited_content": "Updated lesson content",
  "status": "reviewed"
}
```

#### POST `/api/lesson-plans/resources/{resource_id}/export`
Export a lesson resource to PDF or DOCX format.

**Request Body:**
```json
{
  "format": "pdf"
}
```

**Response:** Binary file (PDF or DOCX)

**Supported Formats:**
- `pdf`: Portable Document Format
- `docx`: Microsoft Word Document

**Headers:**
```
Content-Disposition: attachment; filename="lesson-resource-{resource_id}.pdf"
Content-Type: application/pdf
```

### Curriculum Management

#### GET `/api/curriculum/map`
Map subject and grade level to curriculum standards.

**Parameters:**
- `subject` (string): Subject name
- `grade_level` (string): Grade level
- `country` (string): Country code

**Response:**
```json
{
  "curriculum_id": 1,
  "subject": "Mathematics",
  "grade_level": "Grade 5",
  "curriculum_standard": "Nigerian National Curriculum",
  "description": "Mathematics curriculum for Grade 5",
  "country": "Nigeria"
}
```

#### GET `/api/curriculum/standards`
Retrieve all curriculum standards.

#### GET `/api/curriculum/subjects`
Retrieve all available subjects.

#### GET `/api/curriculum/grade-levels`
Retrieve all available grade levels.

#### POST `/api/curriculum/standards`
Add new curriculum standards.



### Parent: Child Profiles

> **Role required**: `PARENT`. All `/api/children` and `/api/guides` endpoints return `403` for `EDUCATOR` callers.

#### POST `/api/children`
Create a child profile for the current parent.

**Request Body:**
```json
{
  "name": "Amara",
  "age": 9,
  "school_name": "Greenfield Primary",
  "country_id": 1,
  "curricula_id": 2,
  "grade_level_id": 5,
  "subjects": [3, 7]
}
```

**Response (201):**
```json
{
  "child_id": 42,
  "parent_id": 17,
  "name": "Amara",
  "age": 9,
  "school_name": "Greenfield Primary",
  "country_id": 1,
  "country_name": "Nigeria",
  "curricula_id": 2,
  "curricula_title": "Nigerian Basic Education Curriculum",
  "grade_level_id": 5,
  "grade_level_name": "Grade 4",
  "subjects": [3, 7],
  "created_at": "2026-04-26T10:00:00Z",
  "updated_at": "2026-04-26T10:00:00Z"
}
```

#### GET `/api/children`
List all child profiles for the current parent.

**Response:**
```json
{
  "children": [ { ...ChildProfileResponse... } ],
  "total": 2
}
```

#### GET `/api/children/{child_id}`
Get a single child profile by ID. Returns `404` if the child does not belong to the current parent.

#### PUT `/api/children/{child_id}`
Update a child profile. All fields are optional.

**Request Body:** same shape as `POST /api/children`, all fields optional.

#### DELETE `/api/children/{child_id}`
Delete a child profile and all associated guides. Returns `{"message": "Child profile deleted"}`.

---

### Parent: Curriculum Topics for a Child

#### GET `/api/children/{child_id}/topics`
Return curriculum topics available to a child based on their grade and curriculum.

**Query Parameters:**
- `subject_id` (optional, integer): Filter to a specific subject.

**Response:**
```json
[
  {
    "topic_id": 101,
    "title": "Fractions",
    "subject_id": 3,
    "subject_name": "Mathematics",
    "grade_level_id": 5
  }
]
```

---

### Parent: "How to Help" Guides

#### GET `/api/children/{child_id}/guides`
List all saved guides for a child.

**Query Parameters:**
- `bookmarked` (optional, boolean, default `false`): Return only bookmarked guides.

**Response:**
```json
{
  "guides": [ { ...ParentGuideResponse... } ],
  "total": 5
}
```

#### POST `/api/children/{child_id}/guides/generate`
Generate (or retrieve existing) a "How to Help" guide for a topic.
- If a guide already exists for this child+topic combination, returns the cached guide immediately (idempotent).
- If not, calls the AI service to generate a new guide and persists it.
- **Rate-limited**: 5 requests / minute per IP.

**Query Parameters:**
- `topic_id` (required, integer): Topic to generate the guide for.

**Response (201 created / 200 existing):** `ParentGuideResponse`

**Error responses:**
- `503` — AI service temporarily unavailable
- `502` — AI returned malformed output (retry)
- `404` — Child not found or not owned by caller

#### GET `/api/guides/{guide_id}`
Get a single parent guide by ID. Returns `404` if not owned by the current parent.

#### POST `/api/guides/{guide_id}/bookmark`
Toggle the bookmark status of a guide. Returns the updated `ParentGuideResponse`.

#### GET `/api/guides/{guide_id}/export`
Export a parent guide as a downloadable PDF for offline printing.

**Response:** Binary PDF (`application/pdf`)

**Headers:**
```
Content-Disposition: attachment; filename="Fractions.pdf"
Content-Type: application/pdf
```

**Error responses:**
- `422` — Guide has no content or content is malformed
- `503` — PDF generation service unavailable (WeasyPrint not installed)
- `500` — Unexpected export error

---

## 🔐 Authentication

All protected endpoints require a valid JWT. Tokens are issued as **HttpOnly cookies** (set on login/register — browser clients just need `credentials: 'include'`). API clients can alternatively pass the token in the `Authorization` header.

**HttpOnly cookie (browser clients):**
```
Cookie: access_token=<jwt>
```

**Bearer header (API clients):**
```
Authorization: Bearer <jwt>
```

Tokens are obtained via `POST /api/auth/login`, `POST /api/auth/register`, or `POST /api/auth/google`. A `POST /api/auth/logout` endpoint clears the cookie.

Requests to protected endpoints without a valid token return `401 Unauthorized`. Requests with a valid token but the wrong role return `403 Forbidden`.

## 📊 Data Models

### LessonPlanCreate
```typescript
{
  subject: string, // Subject area (e.g., Mathematics, Science)
  grade_level: string, // Grade level (e.g., Grade 4, Grade 7)
  topic: string, // Specific topic within the subject (e.g., Fractions, Photosynthesis)
  user_id: number // User ID of the lesson plan author
}
```

### LessonPlan
```typescript
{
  lesson_id: number,
  title: string,
  subject: string,
  grade_level: string,
  topic: string,
  author_id: number,
  context_description: string,
  duration_minutes: number,
  created_at: string,
  updated_at: string,
  status: "draft" | "published" | "archived"
}

// Lesson Plan Response (matches actual implementation)
{
  lesson_id: number,
  title: string,
  subject: string,
  grade_level: string,
  topic: string,
  author_id: number,
  duration_minutes: number,
  created_at: string,
  updated_at: string,
  status: "draft" | "edited" | "reviewed" | "exported" | "archived",
  curriculum_learning_objectives: string[],
  curriculum_contents: string[]
}

### LessonResourceCreate
```typescript
{
  lesson_plan_id: number,
  user_id: number,
  context_input?: string,
  export_format?: string
}
```

### LessonResourceUpdate
```typescript
{
  user_edited_content: string,
  status?: string
}
```

### LessonResourceResponse
```typescript
{
  lesson_resources_id: number,
  lesson_plan_id: number,
  user_id: number,
  context_input?: string,
  ai_generated_content?: string,
  user_edited_content?: string,
  export_format?: string,
  status: string,
  created_at: string
}
```



### ChildProfileCreate / ChildProfileUpdate
```typescript
{
  name: string,          // 1–100 chars, required on create
  age?: number,          // 3–25 (inclusive)
  school_name?: string,  // max 200 chars
  country_id?: number,
  curricula_id?: number,
  grade_level_id?: number,
  subjects?: number[]    // list of subject IDs
}
```

### ChildProfileResponse
```typescript
{
  child_id: number,
  parent_id: number,
  name: string,
  age?: number,
  school_name?: string,
  country_id?: number,
  country_name?: string,
  curricula_id?: number,
  curricula_title?: string,
  grade_level_id?: number,
  grade_level_name?: string,
  subjects?: number[],
  created_at: string,    // ISO 8601
  updated_at: string
}
```

### ChildProfileListResponse
```typescript
{
  children: ChildProfileResponse[],
  total: number
}
```

### ParentGuideResponse
```typescript
{
  guide_id: number,
  child_id: number,
  topic_id: number,
  topic_title?: string,
  subject_name?: string,
  ai_generated_content?: string,   // JSON string — ParentGuideAIContent structure
  user_edited_content?: string,
  is_bookmarked: boolean,
  created_at: string,
  updated_at: string
}
```

### ParentGuideListResponse
```typescript
{
  guides: ParentGuideResponse[],
  total: number
}
```

### ParentGuideAIContent (shape of `ai_generated_content` JSON)
```typescript
{
  topic_header: {
    topic: string,
    subject: string,
    grade_level: string,
    country: string,
    curriculum: string
  },
  simple_explanation: {
    what_it_is: string,
    why_it_matters: string
  },
  home_activity: {
    title: string,
    description: string,
    materials_needed: string[],
    steps: string[],
    what_to_look_for: string
  },
  conversation_starters: string[],
  common_mistakes: Array<{
    mistake: string,
    why_it_happens: string,
    how_to_help: string
  }>,
  curriculum_context?: {
    what_came_before?: string,
    what_comes_next?: string,
    how_long_in_school?: string
  },
  encouragement_tips?: string[]
}
```

## 🚨 Error Handling

### Error Response Format
All API errors follow a consistent format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "VALIDATION_ERROR"
}
```

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| `200` | Success | Request completed successfully |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request parameters |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Authenticated but wrong role, or accessing another user's resource |
| `404` | Not Found | Resource doesn't exist or doesn't belong to caller |
| `422` | Validation Error | Request validation failed |
| `502` | Bad Gateway | AI returned malformed output — safe to retry |
| `503` | Service Unavailable | AI or PDF generation service temporarily unavailable |
| `500` | Internal Server Error | Server error |

### Endpoint-Specific Error Responses

#### POST `/api/lesson-plans/generate`
**400 Bad Request - Invalid Parameters**
```json
{
  "detail": "Invalid subject. Must be one of: Mathematics, Science, English, History, Geography, Civics, Art, Music, Physical Education, Technology",
  "status_code": 400,
  "error_type": "VALIDATION_ERROR"
}
```

**400 Bad Request - Missing Required Fields**
```json
{
  "detail": [
    {
      "loc": ["body", "subject"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "grade_level"],
      "msg": "field required", 
      "type": "value_error.missing"
    }
  ],
  "status_code": 422,
  "error_type": "VALIDATION_ERROR"
}
```

**500 Internal Server Error - AI Service Unavailable**
```json
{
  "detail": "AI service temporarily unavailable. Please try again later.",
  "status_code": 500,
  "error_type": "AI_SERVICE_ERROR"
}
```

#### GET `/api/lesson-plans/{lesson_id}`
**404 Not Found**
```json
{
  "detail": "Lesson plan not found",
  "status_code": 404,
  "error_type": "RESOURCE_NOT_FOUND"
}
```

#### GET `/api/curriculum/map`
**404 Not Found - No Curriculum Standards**
```json
{
  "detail": "No curriculum standards found for Mathematics - Grade 13",
  "status_code": 404,
  "error_type": "CURRICULUM_NOT_FOUND"
}
```

**400 Bad Request - Invalid Parameters**
```json
{
  "detail": "Invalid grade level. Must be one of: Grade 1, Grade 2, Grade 3, Grade 4, Grade 5, Grade 6, Grade 7, Grade 8, Grade 9, Grade 10, Grade 11, Grade 12",
  "status_code": 400,
  "error_type": "VALIDATION_ERROR"
}
```

#### POST `/api/curriculum/standards`
**400 Bad Request - Duplicate Standard**
```json
{
  "detail": "Curriculum standard already exists for Mathematics - Grade 5",
  "status_code": 400,
  "error_type": "DUPLICATE_RESOURCE"
}
```

### Validation Error Details

When validation fails, the response includes field-specific errors:

```json
{
  "detail": [
    {
      "loc": ["body", "duration_minutes"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    },
    {
      "loc": ["body", "duration_minutes"],
      "msg": "ensure this value is less than 121",
      "type": "value_error.number.not_lt",
      "ctx": {"limit_value": 121}
    }
  ],
  "status_code": 422,
  "error_type": "VALIDATION_ERROR"
}
```

### Error Handling Best Practices

1. **Always check the status code** before processing the response
2. **Handle 422 errors** by displaying field-specific validation messages
3. **Implement retry logic** for 500 errors (with exponential backoff)
4. **Cache curriculum data** to avoid repeated 404 errors
5. **Provide user-friendly messages** based on error_type

### Example Error Handling (JavaScript)
```javascript
async function generateLessonPlan(data) {
  try {
    const response = await fetch('/api/lesson-plans/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      if (error.status_code === 422) {
        // Handle validation errors
        error.detail.forEach(fieldError => {
          console.error(`${fieldError.loc.join('.')}: ${fieldError.msg}`);
        });
      } else if (error.status_code === 500) {
        // Handle server errors
        console.error('Server error:', error.detail);
      } else {
        // Handle other errors
        console.error('API error:', error.detail);
      }
      return null;
    }
    
    return await response.json();
  } catch (err) {
    console.error('Network error:', err);
    return null;
  }
}
```

## 🔄 Rate Limiting

- **Free Tier**: 100 requests per hour
- **Premium Tier**: 1000 requests per hour
- **Enterprise**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642233600
```

## 📝 Examples

### Generate a Science Lesson Plan
```bash
curl -X POST "http://localhost:8000/api/lesson-plans/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Science",
    "grade_level": "Grade 6",
    "topic": "Photosynthesis",
    "user_id": 1
  }'
```

### Export a Lesson Resource to PDF
```bash
curl -X POST "http://localhost:8000/api/lesson-plans/resources/123/export" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "format": "pdf"
  }' \
  --output lesson-resource-123.pdf
```



## 🔗 Related Documentation

- [AI Integration](ai-integration.md) - How AI is used in the platform
- [Database Schema](database.md) - Database structure and relationships
- [Development Guide](../development/README.md) - Setting up the development environment

## 🆘 Support

For API support:
- Check the [OpenAPI documentation](http://localhost:8000/docs) for interactive testing
- Review [error codes](#error-handling) for troubleshooting
- Contact the development team for additional help 