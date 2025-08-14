# Curriculum Population Scripts

This directory contains scripts for populating the Awade platform with curriculum data.

## Current Status

**✅ Already Exists in Database:**
- Nigeria country (country_id = 1)
- NERDC Curriculum (curricula_id = 1) 
- JSS1 grade level (grade_level_id = 1)
- Mathematics subject (subject_id = 1)
- Curriculum structure linking them (curriculum_structure_id = 1)
- Fractions topic (topic_id = 1) with learning objectives and content areas

## JSS1 Mathematics Curriculum Population

### Option 1: Populate Remaining Topics (Recommended)

Since the foundational data already exists, use `populate_remaining_jss1_mathematics.py` to add the remaining 24 topics:

```bash
cd scripts
python3 populate_remaining_jss1_mathematics.py
```

Or use the shell script:
```bash
cd scripts
chmod +x run_remaining_curriculum.sh
./run_remaining_curriculum.sh
```

### Option 2: Full Population (If Starting Fresh)

If you need to start completely fresh, use `populate_jss1_mathematics.py`:

```bash
cd scripts
python3 populate_jss1_mathematics.py
```

## What Will Be Created

The remaining topics script will create **24 new topics** organized into 5 themes:

### Theme 1: Number and Numeration (5 new topics)
- Whole Numbers
- LCM (Lowest Common Multiple)  
- HCF (Highest Common Factor)
- Counting in Base 2
- Conversion of Base 10 Numerals to Binary Numbers
- *Fractions (already exists)*

### Theme 2: Basic Operations (7 new topics)
- Addition and Subtraction
- Addition and Subtraction of Fractions
- Multiplication and Division of Fractions
- Estimation
- Approximation
- Addition of Numbers in Base 2 Numerals
- Subtraction of Numbers in Base 2 Numerals
- Multiplication of Numbers in Base 2 Numerals

### Theme 3: Algebra Processes (3 new topics)
- Use of Symbols
- Simplification of Algebraic Expressions
- Simple Equations

### Theme 4: Mensuration and Geometry (4 new topics)
- Plane Shapes
- Three Dimensional Figures
- Construction
- Angles

### Theme 5: Everyday Statistics (3 new topics)
- Need for Statistics
- Data Collection
- Data Presentation

## Prerequisites

1. PostgreSQL database running
2. Python 3.7+ with required dependencies
3. Existing database with the foundational entities

## Setup

1. **Install dependencies:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

2. **Database connection:**
   - If using Docker: The script will use the default Docker database URL
   - If using local database: Set `DATABASE_URL` environment variable
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
   ```

3. **Ensure database is running:**
   ```bash
   # If using Docker
   docker-compose up -d postgres
   
   # Or start PostgreSQL manually
   ```

## Usage

### Quick Start (Recommended)
```bash
cd scripts
python3 populate_remaining_jss1_mathematics.py
```

### With Shell Script
```bash
cd scripts
chmod +x run_remaining_curriculum.sh
./run_remaining_curriculum.sh
```

## Expected Output

The script will:
- Verify existing entities (Nigeria, NERDC, JSS1, Mathematics)
- Check existing topics (will find Fractions)
- Create 24 new topics with learning objectives and content areas
- Provide a summary of what was created
- Verify the final data structure

## Database Schema

The script works with the existing database tables:
- `countries` - Country information (Nigeria exists)
- `curricula` - Curriculum records (NERDC exists)
- `grade_levels` - Educational grade levels (JSS1 exists)
- `subjects` - Academic subjects (Mathematics exists)
- `curriculum_structures` - Links curricula, grade levels, and subjects (exists)
- `topics` - Individual topics within a curriculum structure (Fractions exists)
- `learning_objectives` - Performance objectives for each topic
- `topic_contents` - Content areas for each topic

## Relationships

The existing data structure shows these relationships:
- **Nigeria** (country_id=1) → **NERDC Curriculum** (curricula_id=1, country_id=1)
- **NERDC Curriculum** + **JSS1** + **Mathematics** → **Curriculum Structure** (curriculum_structure_id=1)
- **Curriculum Structure** → **Topics** (including existing Fractions topic)
- **Topics** → **Learning Objectives** and **Topic Contents**

## Troubleshooting

1. **Database connection issues**: Check your database is running and accessible
2. **Import errors**: Ensure you're running from the correct directory and dependencies are installed
3. **Entity not found errors**: Verify the foundational data exists (Nigeria, NERDC, JSS1, Mathematics)
4. **Permission errors**: Ensure your database user has INSERT and SELECT permissions

## Notes

- The script is idempotent - it won't create duplicate data if run multiple times
- It checks for existing data before creating new records
- All data is committed in a single transaction for consistency
- The script provides detailed logging and verification
- It works with the existing database structure and relationships 