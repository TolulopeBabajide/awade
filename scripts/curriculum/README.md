# Curriculum Data Scripts for Awade Platform

This directory contains scripts for populating the Awade platform with comprehensive curriculum data.

## 📁 Scripts Overview

### 1. `curriculum_seeder.py` - Main Curriculum Seeder
**Purpose**: Populates the database with complete curriculum framework including countries, curricula, grade levels, subjects, and basic topics.

**Features**:
- Seeds 10 African countries with regions
- Creates comprehensive grade level structure (Pre-Primary to SSS 3)
- Adds 21 core subjects across different educational levels
- Establishes curriculum structures for Nigeria and Ghana
- Includes sample topics with learning objectives and content areas

### 2. `add_topics.py` - Topic Addition Script
**Purpose**: Adds detailed topics to existing curriculum structures with comprehensive learning objectives and content areas.

**Features**:
- Mathematics topics (Numbers, Operations, Fractions, Money)
- Science topics (Energy, Matter, Living Things)
- English Language topics (Parts of Speech, Reading Comprehension)
- Duplicate prevention and error handling

## 🚀 Quick Start

### Prerequisites
1. **Database Setup**: Ensure your PostgreSQL database is running
2. **Environment Variables**: Set up your `.env` file with database credentials
3. **Backend Dependencies**: Install backend requirements

### Step 1: Seed Basic Curriculum Framework
```bash
# Navigate to the curriculum scripts directory
cd scripts/curriculum

# Seed all curriculum data (recommended for first-time setup)
python curriculum_seeder.py --reset

# Or seed without resetting existing data
python curriculum_seeder.py
```

### Step 2: Add Detailed Topics
```bash
# Add comprehensive topics for all subjects
python add_topics.py

# Filter by specific grade level
python add_topics.py --grade "Primary 5"

# Filter by specific subject
python add_topics.py --subject "Mathematics"
```

## 📊 Data Structure

### Countries & Regions
- **West Africa**: Nigeria, Ghana, Senegal
- **East Africa**: Kenya, Uganda, Tanzania, Ethiopia, Rwanda
- **Southern Africa**: South Africa
- **North Africa**: Morocco

### Grade Levels
```
Pre-Primary → Primary 1-6 → JSS 1-3 → SSS 1-3
```

### Core Subjects
- **Primary**: Mathematics, English Language, Basic Science, Social Studies
- **Junior Secondary**: + Agricultural Science, Home Economics
- **Senior Secondary**: + Biology, Chemistry, Physics, Economics, Government, Geography

### Curriculum Frameworks
1. **Nigeria National Curriculum**
   - Primary School (P1-P6)
   - Junior Secondary School (JSS 1-3)
   - Senior Secondary School (SSS 1-3)

2. **Ghana National Curriculum**
   - Primary School (P1-P6)
   - Junior High School (JSS 1-3)

## 🔧 Usage Examples

### Complete Database Reset and Seed
```bash
python curriculum_seeder.py --reset
```
This will:
- Drop all existing curriculum tables
- Recreate the database schema
- Seed all countries, curricula, and basic structures

### Country-Specific Seeding
```bash
# Seed only Nigeria curriculum
python curriculum_seeder.py --country Nigeria

# Seed only Ghana curriculum
python curriculum_seeder.py --country Ghana
```

### Topic Addition with Filtering
```bash
# Add topics for Primary 5 Mathematics only
python add_topics.py --grade "Primary 5" --subject "Mathematics"

# Add all Mathematics topics across all grades
python add_topics.py --subject "Mathematics"
```

## 📝 Sample Topics Included

### Mathematics
- **Primary 1**: Numbers 1-100, Addition and Subtraction
- **Primary 2**: Multiplication Tables, Money
- **Primary 3**: Fractions

### Basic Science
- **Primary 4**: Energy, Matter
- **Primary 5**: Living and Non-living Things

### English Language
- **Primary 3**: Parts of Speech
- **Primary 4**: Reading Comprehension

## 🛠️ Customization

### Adding New Countries
Edit `curriculum_seeder.py` and add to the `countries_data` list:
```python
countries_data = [
    # ... existing countries ...
    {"name": "New Country", "iso_code": "NC", "region": "Region Name"},
]
```

### Adding New Subjects
Edit `curriculum_seeder.py` and add to the `subjects_data` list:
```python
subjects_data = [
    # ... existing subjects ...
    "New Subject Name",
]
```

### Adding New Topics
Edit `add_topics.py` and add to the appropriate subject method:
```python
def add_new_subject_topics(self):
    new_topics = [
        {
            "grade": "Grade Level",
            "subject": "Subject Name",
            "topics": [
                {
                    "title": "Topic Title",
                    "objectives": ["Objective 1", "Objective 2"],
                    "content_areas": ["Content 1", "Content 2"]
                }
            ]
        }
    ]
    self._add_topics_batch(new_topics)
```

## 🔍 Verification

### Check Seeded Data
After running the scripts, verify the data in your database:

```sql
-- Check countries
SELECT * FROM countries;

-- Check curriculum structures
SELECT 
    c.curricula_title,
    gl.name as grade_level,
    s.name as subject
FROM curriculum_structures cs
JOIN curricula c ON cs.curricula_id = c.curricula_id
JOIN grade_levels gl ON cs.grade_level_id = gl.grade_level_id
JOIN subjects s ON cs.subject_id = s.subject_id;

-- Check topics
SELECT 
    t.topic_title,
    gl.name as grade_level,
    s.name as subject
FROM topics t
JOIN curriculum_structures cs ON t.curriculum_structure_id = cs.curriculum_structure_id
JOIN grade_levels gl ON cs.grade_level_id = gl.grade_level_id
JOIN subjects s ON cs.subject_id = s.subject_id;
```

## ⚠️ Important Notes

1. **Backup**: Always backup your database before running reset operations
2. **Dependencies**: Ensure all backend models and database connections are properly configured
3. **Permissions**: Verify database user has CREATE, INSERT, and DROP permissions
4. **Environment**: Run scripts from the correct directory with proper Python path setup

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the `scripts/curriculum` directory
   - Check that the backend path is correctly added to Python path

2. **Database Connection Errors**
   - Verify `.env` file configuration
   - Check database server status
   - Confirm database credentials

3. **Permission Errors**
   - Ensure database user has necessary permissions
   - Check if tables exist and can be modified

### Error Messages
- **"No curriculum structure found"**: Run `curriculum_seeder.py` first
- **"Table doesn't exist"**: Check database schema and run migrations
- **"Duplicate entry"**: Data already exists, use `--reset` flag if needed

## 📞 Support

For issues or questions:
1. Check the error messages and troubleshooting section
2. Verify your database setup and environment configuration
3. Review the script logs for specific error details
4. Ensure all prerequisites are met

## 🔄 Updates and Maintenance

These scripts are designed to be:
- **Idempotent**: Safe to run multiple times
- **Extensible**: Easy to add new countries, subjects, or topics
- **Maintainable**: Clear structure and error handling
- **Documented**: Comprehensive usage examples and customization guides
