# Awade API Documentation

> **Last generated: 2025-07-20 22:47:46


> **For detailed endpoint contracts and example payloads, see [Internal API Contracts](../internal/api-contracts.md).**

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
  "objectives": ["Understand fraction-decimal relationships"], // Optional
  "duration_minutes": 45,
  "local_context": "Rural school with limited resources, students familiar with local market activities",
  "language": "en",
  "cultural_context": "African",
  "country": "Nigeria",
  "author_id": 1
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

#### GET `/api/lesson-plans/{id}/detailed`
Retrieve a detailed lesson plan with all 6 sections.

**Response:**
```json
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

### Training Modules

#### GET `/api/training-modules`
Retrieve all available training modules.

**Response:**
```json
[
  {
    "id": "tm_001",
    "title": "Effective Classroom Management",
    "description": "Learn strategies for maintaining an engaging classroom",
    "duration": 15,
    "category": "Classroom Management",
    "language": "en",
    "is_offline": true,
    "objectives": ["Understand key concepts", "Apply new knowledge"],
    "steps": ["Introduction", "Main content", "Practice", "Reflection"]
  }
]
```

#### GET `/api/training-modules/{module_id}`
Retrieve a specific training module by ID.

## 🔐 Authentication

Currently, the API uses basic authentication. Future versions will implement JWT tokens.

**Headers:**
```
Authorization: Basic <base64-encoded-credentials>
```

## 📊 Data Models

### LessonPlanRequest
```typescript
{
  subject: "Mathematics" | "Science" | "English" | "History" | "Geography" | "Civics" | "Art" | "Music" | "Physical Education" | "Technology",
  grade_level: "Grade 1" | "Grade 2" | "Grade 3" | "Grade 4" | "Grade 5" | "Grade 6" | "Grade 7" | "Grade 8" | "Grade 9" | "Grade 10" | "Grade 11" | "Grade 12",
  topic: string,
  objectives?: string[], // Optional - AI can generate these
  duration_minutes: number, // 15-120 minutes
  local_context?: string, // Local environment, resources, community context
  language: "en" | "fr" | "sw" | "yo" | "ig" | "ha",
  cultural_context?: string,
  country: string,
  author_id: number
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

// Detailed Lesson Plan (6 sections)
{
  lesson_id: number,
  title: string,
  subject: string,
  grade_level: string,
  topic: string,
  learning_objectives: string, // AI-generated section
  local_context: string,       // AI-generated section
  core_content: string,        // AI-generated section
  activities: string,          // AI-generated section
  quiz: string,               // AI-generated section
  related_projects: string    // AI-generated section
}
```

### TrainingModule
```typescript
{
  id: string,
  title: string,
  description: string,
  duration: number,
  category: "Classroom Management" | "Pedagogy" | "Technology Integration" | "Assessment" | "Cultural Relevance" | "Special Needs" | "Leadership",
  language: Language,
  is_offline: boolean,
  objectives: string[],
  steps: string[],
  created_at: string,
  completion_rate?: number
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
    "grade": "Grade 6",
    "objectives": ["Understand photosynthesis", "Identify plant parts"],
    "duration": 60,
    "language": "en"
  }'
```

### Get All Training Modules
```bash
curl -X GET "http://localhost:8000/api/training-modules" \
  -H "Accept: application/json"
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