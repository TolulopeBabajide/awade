# Awade API Documentation

> **Last generated: 2025-07-30 11:21:18


> **For detailed endpoint contracts and example payloads, see [Internal API Contracts](../private/api-contracts.md).**

## Overview

The Awade API provides RESTful endpoints for AI-powered lesson planning, training modules, and educator support features. Built with FastAPI, it offers automatic OpenAPI documentation and type safety.

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



## 🔐 Authentication

Currently, the API uses basic authentication. Future versions will implement JWT tokens.

**Headers:**
```
Authorization: Basic <base64-encoded-credentials>
```

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
| `404` | Not Found | Resource doesn't exist |
| `422` | Validation Error | Request validation failed |
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