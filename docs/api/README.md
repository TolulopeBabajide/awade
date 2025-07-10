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