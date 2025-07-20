# Awade Curriculum Database Implementation Guide

## Overview

This document outlines the database schema and implementation steps for integrating structured curriculum data—beginning with JSS1 Mathematics—into the Awade platform using PostgreSQL and FastAPI.

## Database Schema

The curriculum database consists of the following tables:

### 1. Table: curricula
- `id` SERIAL PRIMARY KEY
- `country` VARCHAR(100)
- `grade_level` VARCHAR(10)
- `subject` VARCHAR(100)
- `theme` VARCHAR(255)
- `created_at` TIMESTAMP DEFAULT NOW()
- `updated_at` TIMESTAMP DEFAULT NOW()

### 2. Table: topics
- `id` SERIAL PRIMARY KEY
- `curriculum_id` INTEGER REFERENCES curricula(id) ON DELETE CASCADE
- `topic_code` VARCHAR(50) UNIQUE
- `topic_title` TEXT
- `description` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()
- `updated_at` TIMESTAMP DEFAULT NOW()

### 3. Table: learning_objectives
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `objective` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

### 4. Table: contents
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `content_area` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

### 5. Table: teacher_activities
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `activity` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

### 6. Table: student_activities
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `activity` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

### 7. Table: teaching_materials
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `material` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

### 8. Table: evaluation_guides
- `id` SERIAL PRIMARY KEY
- `topic_id` INTEGER REFERENCES topics(id) ON DELETE CASCADE
- `guide` TEXT
- `created_at` TIMESTAMP DEFAULT NOW()

## Implementation Steps

### 1. Database Migration

Run the migration script to create the curriculum tables:

```bash
cd apps/backend
python migrations/002_curriculum_schema.py
```

### 2. FastAPI Integration

The curriculum API is integrated using:
- **Pydantic models** in `schemas/curriculum.py`
- **SQLAlchemy models** in `models.py`
- **Service layer** in `services/curriculum_service.py`
- **API routes** in `routers/curriculum.py`

### 3. Data Insertion Workflow

Step-by-step to insert curriculum data:

1. **Insert record into `curricula`** for JSS1 Mathematics
2. **For each topic:**
   - Insert into `topics` with curriculum_id
   - Insert learning objectives, content areas, teacher/student activities, materials, and evaluation guides

## API Endpoints

### Curriculum Management
- `POST /api/curriculum/` - Create a new curriculum
- `GET /api/curriculum/` - Get all curricula with filtering
- `GET /api/curriculum/{curriculum_id}` - Get specific curriculum with topics
- `PUT /api/curriculum/{curriculum_id}` - Update curriculum
- `DELETE /api/curriculum/{curriculum_id}` - Delete curriculum

### Topic Management
- `POST /api/curriculum/topics` - Create a new topic
- `GET /api/curriculum/topics` - Get topics with filtering
- `GET /api/curriculum/topics/{topic_id}` - Get specific topic with all related data
- `GET /api/curriculum/topics/code/{topic_code}` - Get topic by unique code
- `PUT /api/curriculum/topics/{topic_id}` - Update topic
- `DELETE /api/curriculum/topics/{topic_id}` - Delete topic

### Learning Objectives
- `POST /api/curriculum/learning-objectives` - Create learning objective
- `GET /api/curriculum/topics/{topic_id}/learning-objectives` - Get objectives for topic
- `PUT /api/curriculum/learning-objectives/{objective_id}` - Update objective
- `DELETE /api/curriculum/learning-objectives/{objective_id}` - Delete objective

### Content Areas
- `POST /api/curriculum/contents` - Create content area
- `GET /api/curriculum/topics/{topic_id}/contents` - Get content areas for topic
- `PUT /api/curriculum/contents/{content_id}` - Update content area
- `DELETE /api/curriculum/contents/{content_id}` - Delete content area

### Teacher Activities
- `POST /api/curriculum/teacher-activities` - Create teacher activity
- `GET /api/curriculum/topics/{topic_id}/teacher-activities` - Get teacher activities for topic
- `PUT /api/curriculum/teacher-activities/{activity_id}` - Update teacher activity
- `DELETE /api/curriculum/teacher-activities/{activity_id}` - Delete teacher activity

### Student Activities
- `POST /api/curriculum/student-activities` - Create student activity
- `GET /api/curriculum/topics/{topic_id}/student-activities` - Get student activities for topic
- `PUT /api/curriculum/student-activities/{activity_id}` - Update student activity
- `DELETE /api/curriculum/student-activities/{activity_id}` - Delete student activity

### Teaching Materials
- `POST /api/curriculum/teaching-materials` - Create teaching material
- `GET /api/curriculum/topics/{topic_id}/teaching-materials` - Get teaching materials for topic
- `PUT /api/curriculum/teaching-materials/{material_id}` - Update teaching material
- `DELETE /api/curriculum/teaching-materials/{material_id}` - Delete teaching material

### Evaluation Guides
- `POST /api/curriculum/evaluation-guides` - Create evaluation guide
- `GET /api/curriculum/topics/{topic_id}/evaluation-guides` - Get evaluation guides for topic
- `PUT /api/curriculum/evaluation-guides/{guide_id}` - Update evaluation guide
- `DELETE /api/curriculum/evaluation-guides/{guide_id}` - Delete evaluation guide

### Bulk Operations
- `POST /api/curriculum/bulk` - Create curriculum with all topics and related data

### Search and Analytics
- `GET /api/curriculum/search/curriculums` - Search curricula by country, subject, or theme
- `GET /api/curriculum/search/topics` - Search topics by title or description
- `GET /api/curriculum/{curriculum_id}/statistics` - Get curriculum statistics

## Sample Data Structure

### JSS1 Mathematics Curriculum Example

```json
{
  "country": "Nigeria",
  "grade_level": "JSS1",
  "subject": "Mathematics",
  "theme": "Foundation Mathematics",
  "topics": [
    {
      "topic_code": "JSS1_MATH_001",
      "topic_title": "Number and Numeration",
      "description": "Introduction to numbers and basic numeration concepts",
      "learning_objectives": [
        "Students should be able to identify and write numbers up to 1000",
        "Students should be able to perform basic arithmetic operations",
        "Students should understand place value concepts"
      ],
      "contents": [
        "Whole numbers and their properties",
        "Place value and expanded form",
        "Basic arithmetic operations (addition, subtraction, multiplication, division)"
      ],
      "teacher_activities": [
        "Use number charts and manipulatives to demonstrate place value",
        "Guide students through step-by-step problem solving",
        "Provide real-world examples of number usage"
      ],
      "student_activities": [
        "Complete number pattern worksheets",
        "Practice arithmetic operations with peers",
        "Create number stories using real-life scenarios"
      ],
      "teaching_materials": [
        "Number charts and place value charts",
        "Manipulatives (counters, base-ten blocks)",
        "Whiteboard and markers for demonstrations"
      ],
      "evaluation_guides": [
        "Assess ability to write and read numbers correctly",
        "Evaluate accuracy in arithmetic operations",
        "Check understanding through word problems"
      ]
    }
  ]
}
```

## Setup and Testing

### 1. Run the Setup Script

```bash
cd scripts
python setup_curriculum_db.py
```

This script will:
- Run the database migration
- Test all API endpoints
- Create sample JSS1 Mathematics curriculum data

### 2. Manual Testing

Start the FastAPI server:

```bash
cd apps/backend
uvicorn main:app --reload
```

Test the API at: http://localhost:8000/docs

### 3. Database Verification

Connect to PostgreSQL and verify the tables:

```sql
-- Check if tables exist
\dt curricula
\dt topics
\dt learning_objectives
\dt contents
\dt teacher_activities
\dt student_activities
\dt teaching_materials
\dt evaluation_guides

-- Check sample data
SELECT * FROM curricula;
SELECT * FROM topics;
```

## Next Steps

1. **Prepare curriculum records** for other JSS1 Mathematics topics
2. **Automate input** from structured JSON or CSV files using scripts
3. **Add more subjects** and grade levels
4. **Integrate with lesson planning** to map curriculum standards to lesson plans
5. **Add validation** for curriculum data integrity
6. **Implement caching** for frequently accessed curriculum data

## File Structure

```
apps/backend/
├── models.py                          # SQLAlchemy models
├── schemas/
│   └── curriculum.py                  # Pydantic schemas
├── services/
│   └── curriculum_service.py          # Business logic
├── routers/
│   └── curriculum.py                  # API endpoints
├── migrations/
│   └── 002_curriculum_schema.py       # Database migration
└── main.py                           # FastAPI app with router included

scripts/
└── setup_curriculum_db.py            # Setup and testing script

docs/internal/
└── curriculum-database-guide.md      # This documentation
```

## Performance Considerations

- **Indexes** are created on frequently queried columns
- **Cascade deletes** ensure data integrity
- **Bulk operations** for efficient data insertion
- **Search functionality** with database-level filtering

## Security Notes

- All endpoints are currently open (no authentication required for MVP)
- Input validation is handled by Pydantic schemas
- SQL injection is prevented by SQLAlchemy ORM
- Consider adding authentication and authorization for production use 