# Database Schema - Awade Data Architecture

> **Status**: 🚧 Under Development

This guide documents the database schema and data architecture for the Awade platform.

## 🎯 Overview

The Awade database is designed to support teacher lesson planning, professional development tracking, and community features while ensuring data privacy and scalability.

## 🏗️ Database Architecture

### Technology Stack
- **Primary Database**: PostgreSQL
- **Caching Layer**: Redis
- **Search Engine**: Elasticsearch (planned)
- **File Storage**: Local filesystem with cloud backup
- **Backup Strategy**: Automated daily backups with point-in-time recovery

### Design Principles
- **Privacy First** - Teacher data protection as priority
- **Scalability** - Support for growing user base
- **Performance** - Optimized for common query patterns
- **Flexibility** - Adaptable to different curriculum standards
- **Compliance** - Meet data protection regulations

## 📊 Core Tables

### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    grade_level VARCHAR(50),
    subject VARCHAR(100),
    region VARCHAR(100),
    school VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'teacher'
);
```

### Lesson Plans
```sql
CREATE TABLE lesson_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    grade_level VARCHAR(20) NOT NULL,
    objectives TEXT[],
    activities TEXT[],
    materials TEXT[],
    assessment TEXT,
    rationale TEXT,
    language VARCHAR(10) DEFAULT 'en',
    duration INTEGER,
    is_offline BOOLEAN DEFAULT FALSE,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Training Modules
```sql
CREATE TABLE training_modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    duration INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    content JSONB,
    objectives TEXT[],
    steps TEXT[],
    is_offline BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Progress
```sql
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    module_id INTEGER REFERENCES training_modules(id),
    status VARCHAR(20) DEFAULT 'not_started',
    progress_percentage INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    reflection TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bookmarks
```sql
CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content_type VARCHAR(20) NOT NULL, -- 'lesson_plan' or 'training_module'
    content_id INTEGER NOT NULL,
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔗 Relationship Diagrams

### User-Centric Relationships
```
Users (1) -----> (Many) Lesson Plans
Users (1) -----> (Many) User Progress
Users (1) -----> (Many) Bookmarks
Users (1) -----> (Many) User Sessions
```

### Content Relationships
```
Training Modules (1) -----> (Many) User Progress
Lesson Plans (Many) -----> (Many) Bookmarks
Training Modules (Many) -----> (Many) Bookmarks
```

### Analytics Relationships
```
Users (1) -----> (Many) Analytics Events
Lesson Plans (1) -----> (Many) Analytics Events
Training Modules (1) -----> (Many) Analytics Events
```

## 📈 Analytics Tables

### Analytics Events
```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Sessions
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(255) UNIQUE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER,
    device_type VARCHAR(20),
    browser VARCHAR(50)
);
```

## 🔐 Security and Privacy

### Data Encryption
- **At Rest**: Database-level encryption
- **In Transit**: TLS/SSL encryption
- **Sensitive Fields**: Additional field-level encryption
- **Backup Encryption**: Encrypted backup storage

### Access Control
- **Row-Level Security**: User data isolation
- **Column-Level Security**: Sensitive field protection
- **Audit Logging**: Track all data access
- **Data Masking**: Anonymize data for analytics

### Privacy Features
- **Data Retention**: Configurable retention policies
- **Right to Deletion**: Complete user data removal
- **Data Export**: User data portability
- **Consent Management**: Track user consent

## 🔄 Data Migration

### Schema Versioning
- **Migration Scripts**: Version-controlled schema changes
- **Rollback Support**: Ability to revert changes
- **Data Validation**: Ensure data integrity during migration
- **Backup Strategy**: Pre-migration backups

### Import/Export
- **CSV Import**: Bulk data import capabilities
- **JSON Export**: API-based data export
- **Backup Format**: Standard database backup format
- **Data Validation**: Import data validation rules

## 📊 Performance Optimization

### Indexing Strategy
```sql
-- User queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_region ON users(region);
CREATE INDEX idx_users_school ON users(school);

-- Lesson plan queries
CREATE INDEX idx_lesson_plans_user_id ON lesson_plans(user_id);
CREATE INDEX idx_lesson_plans_subject ON lesson_plans(subject);
CREATE INDEX idx_lesson_plans_created_at ON lesson_plans(created_at);

-- Training module queries
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_module_id ON user_progress(module_id);
CREATE INDEX idx_user_progress_status ON user_progress(status);
```

### Query Optimization
- **Connection Pooling**: Efficient database connections
- **Query Caching**: Redis-based query caching
- **Read Replicas**: Separate read/write databases
- **Partitioning**: Large table partitioning strategies

## 🔧 Maintenance

### Backup Strategy
- **Daily Backups**: Automated daily database backups
- **Point-in-Time Recovery**: Transaction log backups
- **Offsite Storage**: Secure cloud backup storage
- **Recovery Testing**: Regular backup restoration tests

### Monitoring
- **Performance Metrics**: Query performance monitoring
- **Space Usage**: Database size and growth tracking
- **Connection Monitoring**: Active connection tracking
- **Error Logging**: Database error monitoring

### Maintenance Tasks
- **Vacuum**: Regular table cleanup
- **Analyze**: Statistics updates
- **Reindex**: Index maintenance
- **Archive**: Old data archiving

## 🚀 Scaling Considerations

### Horizontal Scaling
- **Read Replicas**: Distribute read load
- **Sharding**: Partition data across databases
- **Microservices**: Separate database per service
- **Caching Layer**: Reduce database load

### Vertical Scaling
- **Resource Allocation**: CPU and memory optimization
- **Storage Optimization**: Efficient storage usage
- **Connection Limits**: Optimize connection pools
- **Query Optimization**: Efficient query patterns

## 📞 Support and Documentation

### Schema Documentation
- **ER Diagrams**: Visual database relationships
- **API Documentation**: Database access patterns
- **Migration Guides**: Schema change procedures
- **Troubleshooting**: Common database issues

### Development Support
- **Local Setup**: Development database configuration
- **Testing**: Database testing strategies
- **Debugging**: Database debugging tools
- **Performance**: Query performance analysis

---

*This schema documentation will be updated as the database design evolves.* 