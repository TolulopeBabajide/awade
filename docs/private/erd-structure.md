# Awade Database ERD Structure

This document provides a comprehensive overview of the Awade database Entity Relationship Diagram (ERD) structure, reflecting the current implementation after all fixes and consolidations.

---

## 📊 Database Overview

The Awade database follows a normalized structure optimized for:
- **User Management**: Consolidated user profiles with educator information
- **Lesson Planning**: 6-section AI-generated lesson plans with curriculum mapping
- **Content Management**: Flexible tagging, resources, and context systems
- **Assessment**: Quiz and feedback systems
- **Curriculum Alignment**: Standards mapping for different countries and subjects

---

## 🗂️ Core Tables

### 1. Users Table
**Purpose**: Consolidated user management with educator profiles

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('educator', 'admin')),
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    school_name VARCHAR(255),
    subjects JSON, -- Array of subjects taught
    grade_levels JSON, -- Array of grade levels
    languages_spoken TEXT, -- Comma-separated languages
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Key Features**:
- Consolidated profile information (previously split between `users` and `educator_profiles`)
- JSON fields for flexible subject and grade level storage
- Role-based access control
- Geographic and institutional information

### 2. Lesson Plans Table
**Purpose**: Core lesson plan storage with 6-section AI-generated content

```sql
CREATE TABLE lesson_plans (
    lesson_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    grade_level VARCHAR(50) NOT NULL,
    topic VARCHAR(255),
    author_id INTEGER NOT NULL REFERENCES users(user_id),
    duration_minutes INTEGER NOT NULL,
    
    -- 6-Section AI-generated content
    learning_objectives TEXT,
    local_context_section TEXT,
    core_content TEXT,
    activities TEXT,
    quiz TEXT,
    related_projects TEXT,
    
    status VARCHAR(50) NOT NULL DEFAULT 'draft' 
        CHECK (status IN ('draft', 'generated', 'edited', 'reviewed', 'exported', 'used_offline', 'archived')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Key Features**:
- Complete 6-section structure for AI-generated content
- Comprehensive status lifecycle management
- Topic-based organization
- Author relationship with users

### 3. Curriculum Maps Table
**Purpose**: Standards mapping for curriculum alignment

```sql
CREATE TABLE curriculum_maps (
    curriculum_id SERIAL PRIMARY KEY,
    subject VARCHAR(100) NOT NULL,
    grade_level VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    standard_code VARCHAR(255) NOT NULL,
    standard_description TEXT NOT NULL,
    country VARCHAR(100),
    lesson_plan_id INTEGER REFERENCES lesson_plans(lesson_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Key Features**:
- Links curriculum standards to lesson plans
- Country-specific curriculum support
- Topic-based organization
- Flexible relationship (optional lesson plan association)

---

## 🔗 Relationship Tables

### 4. Lesson Sections Table
**Purpose**: Additional content sections beyond the core 6-section structure

```sql
CREATE TABLE lesson_sections (
    section_id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    section_title VARCHAR(255) NOT NULL,
    content_text TEXT NOT NULL,
    media_link VARCHAR(500),
    order_number INTEGER NOT NULL
);
```

### 5. Lesson Contexts Table
**Purpose**: Teacher-provided local context information

```sql
CREATE TABLE lesson_contexts (
    context_id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    context_key VARCHAR(100) NOT NULL, -- e.g., 'local_resources', 'student_background'
    context_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Resource Links Table
**Purpose**: External resources linked to lesson plans

```sql
CREATE TABLE resource_links (
    resource_id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    link_url VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('pdf', 'video', 'tool', 'external')),
    description TEXT
);
```

---

## 🏷️ Categorization Tables

### 7. Tags Table
**Purpose**: Flexible categorization system

```sql
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);
```

### 8. Lesson Tags Association Table
**Purpose**: Many-to-many relationship between lessons and tags

```sql
CREATE TABLE lesson_tags (
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (lesson_id, tag_id)
);
```

---

## 📝 Assessment Tables

### 9. Quizzes Table
**Purpose**: Assessment creation and management

```sql
CREATE TABLE quizzes (
    quiz_id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 10. Questions Table
**Purpose**: Individual quiz questions

```sql
CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('mcq', 'open-ended'))
);
```

### 11. Answers Table
**Purpose**: Answer options for questions

```sql
CREATE TABLE answers (
    answer_id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE
);
```

### 12. Feedback Table
**Purpose**: User feedback and ratings for lesson plans

```sql
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔍 Indexes and Performance

### Primary Indexes
```sql
-- User lookup by email
CREATE INDEX idx_users_email ON users(email);

-- Lesson plan lookups
CREATE INDEX idx_lesson_plans_author ON lesson_plans(author_id);
CREATE INDEX idx_lesson_plans_subject_grade ON lesson_plans(subject, grade_level);
CREATE INDEX idx_lesson_plans_status ON lesson_plans(status);

-- Curriculum mapping lookups
CREATE INDEX idx_curriculum_subject_grade ON curriculum_maps(subject, grade_level);
CREATE INDEX idx_curriculum_lesson_plan ON curriculum_maps(lesson_plan_id);

-- Context lookups
CREATE INDEX idx_context_lesson_key ON lesson_contexts(lesson_id, context_key);

-- Tag lookups
CREATE INDEX idx_tags_name ON tags(name);
```

---

## 🔄 Data Flow Relationships

### Lesson Plan Lifecycle
1. **Creation**: User creates lesson plan → `draft` status
2. **AI Generation**: AI generates 6-section content → `generated` status
3. **Editing**: Teacher modifies content → `edited` status
4. **Review**: Final review completed → `reviewed` status
5. **Export**: Lesson plan exported → `exported` status
6. **Usage**: Used in classroom → `used_offline` status
7. **Archive**: Saved for reuse → `archived` status

### Curriculum Mapping Flow
1. **Standards Lookup**: Query curriculum maps by subject/grade
2. **Lesson Association**: Link standards to lesson plans
3. **Country-Specific**: Filter by country for local curricula
4. **Topic Alignment**: Match topics between standards and lessons

### User Profile Integration
1. **Authentication**: Email/password login
2. **Profile Access**: Consolidated user information
3. **Lesson Creation**: Author relationship with lesson plans
4. **Feedback System**: User ratings and comments

---

## 🛡️ Data Integrity Constraints

### Foreign Key Relationships
- All lesson plans must have valid authors
- Curriculum maps can optionally link to lesson plans
- All child records cascade delete with parent
- Feedback requires both valid lesson and user

### Check Constraints
- User roles limited to 'educator' or 'admin'
- Lesson status follows defined lifecycle
- Resource types limited to defined values
- Question types limited to 'mcq' or 'open-ended'
- Ratings must be 1-5 scale

### Unique Constraints
- User emails must be unique
- Tag names must be unique
- Lesson-tag combinations must be unique

---

## 📈 Scalability Considerations

### Partitioning Strategy
- Lesson plans can be partitioned by creation date
- Curriculum maps can be partitioned by country
- User data can be partitioned by region

### Caching Strategy
- Curriculum standards cached by subject/grade/country
- User profiles cached after login
- Lesson plan metadata cached for list views

### Backup Strategy
- Daily full backups
- Hourly incremental backups
- Point-in-time recovery capability

---

## 🔧 Migration Notes

### Recent Changes Applied
1. **Consolidated User Profile**: Merged `educator_profiles` into `users`
2. **6-Section Structure**: Added direct fields for AI-generated content
3. **Status Lifecycle**: Updated to match documented states
4. **Curriculum Mapping**: Added lesson plan relationships
5. **Table Naming**: Standardized to plural forms
6. **Index Optimization**: Added performance indexes

### Backward Compatibility
- All existing data preserved during migration
- API endpoints updated to match new structure
- Documentation aligned with implementation
- No breaking changes to core functionality 