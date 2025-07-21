# Awade Project Requirements Document (Internal)

## 1. Introduction

This Project Requirements Document (PRD) outlines the functional and non-functional requirements for the Awade MVP — an AI-powered educator support platform for African teachers. It serves as a blueprint for development, ensuring alignment between stakeholder needs, design, and engineering.

---

## 2. Stakeholders

* **Primary:** K–12 and tertiary teachers in Sub-Saharan Africa
* **Secondary:** School administrators, teacher trainers, curriculum developers
* **Tertiary:** Ministry of Education, EdTech partners, donor agencies

---

## 3. Business Objectives

* Empower teachers with localized, curriculum-aligned AI tools
* Improve teaching quality and student outcomes through professional development
* Facilitate ethical, explainable, and teacher-controlled AI integration
* Ensure platform accessibility in low-bandwidth, multilingual contexts

---

## 4. Functional Requirements

### 4.1 Authentication & User Management

#### User Flow (Signing Up)
- **Landing Page:** User lands on Awade homepage with clear sign up/login options.
- **Sign Up:** User can register with Google or email, set and confirm password.
- **Password Policy:** Passwords must be at least 8 characters and alphanumeric (letters and numbers only).
- **Confirmation:** Registration is confirmed; user is prompted about a skill quiz (can skip to dashboard).
- **Quiz Preview:** User is briefed about the quiz, modal, and question type.
- **Quiz:** User answers skill quiz (can skip/return later).
- **Dashboard:** After quiz or skipping, user is taken to dashboard.

#### Requirements
* Users must register and log in via email/password or SSO (Google OAuth).
* Passwords are validated on the frontend and securely hashed with bcrypt on the backend.
* JWT-based authentication is used for all sessions.
* Users have a profile: name, email, role, region, language, grade level.
* Password reset and secure token-based sessions.

#### Technical Specifications
- **Authentication Method**: JWT-based authentication (access token returned on signup/login)
- **Password Requirements**: Minimum 8 characters, alphanumeric (letters and numbers)
- **Session Management**: Configurable token expiration (default: 24 hours)
- **SSO Integration**: OAuth 2.0 support for Google
- **Profile Fields**: 
  - Required: name, email, role, region, language
  - Optional: grade_level, school, phone, bio

#### Database Schema
```sql
-- Users table (consolidated profile)
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

-- User sessions table
CREATE TABLE user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 Lesson Planning

#### Requirements
* Teachers can generate lesson plans by specifying subject, grade, topic, and objectives.
* AI-powered suggestions include activities, resources, and rationale.
* Editable lesson templates with save, export (PDF), and offline download.

#### Technical Specifications
- **AI Integration**: OpenAI GPT-4 API with custom prompts
- **Template System**: JSON-based lesson plan templates
- **Export Formats**: PDF, DOCX, HTML
- **Offline Storage**: SQLite for local caching
- **Version Control**: Track lesson plan revisions

#### API Endpoints
```python
# Lesson Planning API
POST /api/lesson-plans/generate
GET /api/lesson-plans
GET /api/lesson-plans/{id}
PUT /api/lesson-plans/{id}
DELETE /api/lesson-plans/{id}
POST /api/lesson-plans/{id}/export
GET /api/lesson-plans/templates
```

### 4.3 Micro-Training Modules

#### Requirements
* List and view bite-sized training modules (title, duration, tags).
* Progress tracking: mark modules as complete and revisit history.
* Reflective journal prompt at end of each module with save capability.

#### Technical Specifications
- **Module Format**: Markdown with embedded multimedia
- **Progress Tracking**: Completion status, time spent, quiz scores
- **Reflection System**: Structured journal entries with prompts
- **Offline Access**: Pre-downloaded modules for offline use

#### Database Schema
```sql
-- Training modules table
CREATE TABLE training_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    duration INTEGER NOT NULL, -- minutes
    category VARCHAR(100) NOT NULL,
    tags TEXT[], -- array of tags
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    is_offline BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID REFERENCES training_modules(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    progress_percentage INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0, -- seconds
    reflection TEXT,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, module_id)
);
```

### 4.4 Feedback & AI Controls

#### Requirements
* Display explanation toggle for AI recommendations.
* Accept/Edit/Reject controls for AI-suggested content.
* Store user override decisions for personalization analytics.

#### Technical Specifications
- **AI Explanation System**: Contextual explanations for each AI suggestion
- **Override Tracking**: Store user decisions for model improvement
- **Confidence Scoring**: AI confidence levels for each suggestion
- **Personalization**: Learn from user preferences and overrides

#### Database Schema
```sql
-- AI interactions table
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- 'lesson_plan', 'training_module'
    content_id UUID NOT NULL,
    ai_suggestion TEXT NOT NULL,
    user_action VARCHAR(20) NOT NULL CHECK (user_action IN ('accept', 'edit', 'reject')),
    user_edit TEXT,
    ai_confidence FLOAT,
    explanation_requested BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.5 Offline & Synchronization

#### Requirements
* Download lesson plans and training modules for offline use.
* Indicate sync status and last synchronized timestamp.
* Automatic sync when connectivity is restored.

#### Technical Specifications
- **Offline Storage**: SQLite database with encrypted storage
- **Sync Protocol**: RESTful API with conflict resolution
- **Conflict Resolution**: Last-write-wins with user notification
- **Bandwidth Optimization**: Compressed data transfer, delta updates

#### Sync Status Tracking
```sql
-- Sync status table
CREATE TABLE sync_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    local_version INTEGER DEFAULT 1,
    server_version INTEGER DEFAULT 1,
    last_synced TIMESTAMP,
    sync_status VARCHAR(20) DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'conflict', 'failed')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.6 Localization & Accessibility

#### Requirements
* Multi-language support with a language selector.
* Curriculum tagging by region and national standard.
* WCAG AA compliance: keyboard navigation, clear labels, high-contrast mode.

#### Technical Specifications
- **Supported Languages**: English, French, Swahili, Yoruba, Igbo, Hausa
- **Translation System**: JSON-based translation files
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Curriculum Standards**: Region-specific curriculum mapping

#### Translation Structure
```json
{
  "en": {
    "lesson_planning": "Lesson Planning",
    "training_modules": "Training Modules",
    "generate_plan": "Generate Lesson Plan"
  },
  "fr": {
    "lesson_planning": "Planification de Cours",
    "training_modules": "Modules de Formation",
    "generate_plan": "Générer un Plan de Cours"
  }
}
```

### 4.7 Community & Bookmarks (MVP-Light)

#### Requirements
* Bookmark lessons and modules; view a "Saved Resources" list.
* Simple highlights feed showing popular content (anonymized).
* Tagging and search within bookmarks.

#### Technical Specifications
- **Bookmark System**: User-specific saved resources
- **Popularity Algorithm**: View count, completion rate, user ratings
- **Search**: Full-text search with filters
- **Privacy**: Anonymized analytics, no personal data sharing

### 4.8 Analytics & Reporting (Admin/Leader)

#### Requirements
* Dashboard for administrators to view teacher usage: login frequency, modules completed.
* Exportable CSV reports for progress and engagement metrics.

#### Technical Specifications
- **Analytics Dashboard**: Real-time metrics and charts
- **Report Generation**: Scheduled reports, custom date ranges
- **Data Export**: CSV, Excel, PDF formats
- **Privacy Compliance**: GDPR-compliant data handling

---

## 5. Non-Functional Requirements

### 5.1 Performance
* **Page Load Time**: < 2 seconds on 3G connection
* **API Response Time**: < 500ms for 95% of requests
* **Database Queries**: < 100ms for standard operations
* **Offline Sync**: < 30 seconds for typical data sets

### 5.2 Scalability
* **User Capacity**: Support up to 10,000 active users in pilot
* **Concurrent Users**: Handle 1,000 simultaneous users
* **Data Growth**: Support 1TB+ of user-generated content
* **Geographic Distribution**: Multi-region deployment capability

### 5.3 Security
* **Authentication**: JWT tokens with secure storage
* **Data Encryption**: AES-256 for sensitive data
* **OWASP Compliance**: Address all OWASP Top 10 vulnerabilities
* **Audit Logging**: Comprehensive security event logging

### 5.4 Reliability
* **Uptime**: 99.5% availability target
* **Error Monitoring**: Real-time error tracking and alerting
* **Backup Strategy**: Daily automated backups with point-in-time recovery
* **Disaster Recovery**: RTO < 4 hours, RPO < 1 hour

### 5.5 Maintainability
* **Code Coverage**: 80% unit test coverage minimum
* **Documentation**: Comprehensive API and code documentation
* **Modular Architecture**: Clear separation of concerns
* **CI/CD Pipeline**: Automated testing and deployment

---

## 6. System Requirements

### 6.1 Backend Stack
* **Runtime**: Python 3.10+
* **Framework**: FastAPI 0.104+
* **Database**: PostgreSQL 13+
* **Cache**: Redis 7+
* **Message Queue**: Celery with Redis backend

### 6.2 Frontend Stack
* **Framework**: React 18+ or HTML/Pug
* **Styling**: Tailwind CSS
* **State Management**: React Context or Redux
* **Build Tool**: Vite or Webpack

### 6.3 AI Services
* **Primary AI**: OpenAI GPT-4 API
* **Fallback AI**: Local rule-based system
* **Prompt Management**: Version-controlled prompt templates
* **Cost Monitoring**: API usage tracking and optimization

### 6.4 DevOps
* **Containerization**: Docker and Docker Compose
* **CI/CD**: GitHub Actions
* **Monitoring**: Prometheus + Grafana
* **Logging**: Structured logging with ELK stack

---

## 7. Constraints & Assumptions

### 7.1 Technical Constraints
* **Pilot Region**: Nigeria (expandable to other African regions)
* **Device Support**: Smartphones with basic internet access
* **Bandwidth**: Optimized for 3G connections
* **Storage**: Limited local storage on user devices

### 7.2 Business Constraints
* **Beta Testing**: Limited to 50 teachers in pilot phase
* **AI Costs**: Monitor and optimize API usage costs
* **Compliance**: Local education regulations and data protection laws
* **Budget**: Development and operational cost constraints

### 7.3 Assumptions
* Users have basic smartphone literacy
* Internet connectivity is available (even if intermittent)
* Teachers are motivated to use digital tools
* Local curriculum standards are accessible

---

## 8. Acceptance Criteria

| Requirement Area       | Acceptance Criteria                                         | Test Cases |
| ---------------------- | ----------------------------------------------------------- | ---------- |
| Lesson Planning        | Outputs editable plan; exportable; AI rationale visible     | TC-001 to TC-010 (see Test Plan) |
| Training Modules       | Can mark complete; view reflective prompt; history persists | TC-011 to TC-020 (see Test Plan) |
| Offline Mode           | Content accessible offline; sync restores state             | TC-021 to TC-030 (see Test Plan) |
| AI Controls            | Accept/edit/reject works; overrides stored                  | TC-031 to TC-040 (see Test Plan) |
| Localization           | UI text and content change with language selector           | TC-041 to TC-050 (see Test Plan) |
| Bookmarks & Community  | Can bookmark; saved list persists; search/tag works         | TC-051 to TC-060 (see Test Plan) |
| Performance & Security | Meets response times; passes security audits                | TC-061 to TC-070 (see Test Plan) |

---

**See [Testing Plan](testing.md) for detailed test cases and strategy.**

**See [API Contracts](api-contracts.md) for endpoint specifications and example payloads.**

---

## 9. Risk Assessment

### 9.1 Technical Risks
* **AI API Reliability**: Mitigation - Fallback systems, cost monitoring
* **Offline Sync Complexity**: Mitigation - Thorough testing, conflict resolution
* **Performance on Low-end Devices**: Mitigation - Progressive enhancement, optimization

### 9.2 Business Risks
* **User Adoption**: Mitigation - User research, iterative development
* **Regulatory Compliance**: Mitigation - Legal review, privacy by design
* **Scalability Challenges**: Mitigation - Load testing, architecture review

---

## 10. Success Metrics

### 10.1 Technical Metrics
* **Performance**: 95% of requests under 500ms
* **Reliability**: 99.5% uptime
* **Security**: Zero critical vulnerabilities
* **Code Quality**: 80% test coverage

### 10.2 Business Metrics
* **User Engagement**: 70% weekly active users
* **Feature Adoption**: 80% lesson plan generation usage
* **User Satisfaction**: 4.5/5 average rating
* **Retention**: 60% monthly user retention

---

**Document Version**: 1.0  
**Last Updated**: July 1, 2025  
**Next Review**: August 3, 2025 

## Backend (Python)
- All sensitive credentials (database, admin, educator) must be set via environment variables in `.env`.
- The `bcrypt` library is required for secure password hashing (see `apps/backend/requirements.txt`).
- The database initialization script (`init_db.py`) uses `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `EDUCATOR_EMAIL`, and `EDUCATOR_PASSWORD` from the environment to create initial users. These are NOT used for production authentication.
- No hardcoded credentials are allowed in the codebase. 