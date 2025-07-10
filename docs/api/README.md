# Awade API Documentation

> **Last generated: 2025-07-10 16:21:07


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
Generate an AI-powered lesson plan.

**Request Body:**
```json
{
  "subject": "Mathematics",
  "grade": "Grade 4",
  "objectives": ["Understand basic fractions", "Identify numerator and denominator"],
  "duration": 45,
  "language": "en",
  "cultural_context": "African"
}
```

**Response:**
```json
{
  "id": "lp_001",
  "title": "Mathematics Lesson Plan",
  "subject": "Mathematics",
  "grade": "Grade 4",
  "objectives": ["Understand basic fractions", "Identify numerator and denominator"],
  "activities": ["Introduction activity (5 min)", "Main content (30 min)", "Assessment (10 min)"],
  "materials": ["Whiteboard", "Markers", "Student worksheets"],
  "assessment": "Formative assessment through observation",
  "rationale": "This lesson plan follows best practices for active learning",
  "created_at": "2025-01-15T10:00:00Z",
  "language": "en",
  "is_offline": true,
  "ai_explanation": "This approach uses visual learning..."
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
  grade: "Grade 1" | "Grade 2" | "Grade 3" | "Grade 4" | "Grade 5" | "Grade 6" | "Grade 7" | "Grade 8" | "Grade 9" | "Grade 10" | "Grade 11" | "Grade 12",
  objectives: string[],
  duration: number, // 15-120 minutes
  language: "en" | "fr" | "sw" | "yo" | "ig" | "ha",
  cultural_context?: string
}
```

### LessonPlan
```typescript
{
  id: string,
  title: string,
  subject: Subject,
  grade: GradeLevel,
  objectives: string[],
  activities: string[],
  materials: string[],
  assessment: string,
  rationale: string,
  created_at: string,
  updated_at?: string,
  language: Language,
  is_offline: boolean,
  ai_explanation?: string
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
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (invalid data format)
- `500` - Internal Server Error

### Example Error Response
```json
{
  "success": false,
  "error": "Lesson plan not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "details": {
    "plan_id": "lp_999"
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