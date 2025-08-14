# 🗄️ Database Testing and Migration Guide

## 🎯 **Overview**

This guide covers how to test and migrate database tables for your Awade test environment. It includes comprehensive testing, schema validation, and migration procedures.

---

## 🚀 **Quick Start**

### **1. Test Database Connection**
```bash
cd apps/backend
python test_database.py --test-connection
```

### **2. Run Full Database Test Suite**
```bash
cd apps/backend
python test_database.py --full-test
```

### **3. Migrate Database Schema**
```bash
cd apps/backend
python migrate_database.py migrate
```

---

## 🧪 **Database Testing Scripts**

### **test_database.py - Comprehensive Testing**

This script provides comprehensive database testing:

#### **Available Commands:**
```bash
# Test database connection only
python test_database.py --test-connection

# Create database tables
python test_database.py --create-tables

# Validate database schema
python test_database.py --validate-schema

# Test basic operations (CRUD)
python test_database.py --test-operations

# Clean up test data
python test_database.py --cleanup

# Run all tests
python test_database.py --full-test
```

#### **What Each Test Does:**

1. **Connection Test** - Verifies database connectivity
2. **Table Creation** - Creates all tables from models
3. **Schema Validation** - Shows table structure and relationships
4. **Basic Operations** - Tests CRUD operations with test data
5. **Cleanup** - Removes test data safely

---

## 🔄 **Database Migration Scripts**

### **migrate_database.py - Schema Management**

This script handles database schema updates:

#### **Available Commands:**
```bash
# Show current migration status
python migrate_database.py status

# Run migrations (create/update tables)
python migrate_database.py migrate

# Reset database (drop all tables and recreate)
python migrate_database.py reset
```

#### **Migration Process:**
1. **Status Check** - See what tables exist
2. **Migration** - Create/update tables based on models
3. **Verification** - Confirm tables were created correctly

---

## 🎯 **Step-by-Step Testing Process**

### **Step 1: Environment Setup**
```bash
# 1. Set your test environment variables
cp env.test.template .env.test

# 2. Edit .env.test with your test database details
nano .env.test

# 3. Load test environment
source .env.test
```

### **Step 2: Test Database Connection**
```bash
cd apps/backend
python test_database.py --test-connection
```

**Expected Output:**
```
🔌 Testing database connection...
✅ Database connected successfully!
📊 Database version: PostgreSQL 15.x
```

### **Step 3: Create Database Tables**
```bash
python test_database.py --create-tables
```

**Expected Output:**
```
🏗️  Creating database tables...
✅ All tables created successfully!
```

### **Step 4: Validate Schema**
```bash
python test_database.py --validate-schema
```

**Expected Output:**
```
🔍 Validating database schema...
✅ Found 12 tables:
  📋 countries (3 columns)
    - country_id: INTEGER NOT NULL
    - country_name: VARCHAR(100) NOT NULL
    - iso_code: VARCHAR(2) NULL
  📊 Indexes: 1
    - ix_countries_country_name: ['country_name']
```

### **Step 5: Test Basic Operations**
```bash
python test_database.py --test-operations
```

**Expected Output:**
```
🧪 Testing basic database operations...
  📝 Testing country creation...
    ✅ Created country: Test Country (ID: 1)
  📚 Testing curriculum creation...
    ✅ Created curriculum: Test Curriculum (ID: 1)
  🔍 Testing query operations...
    ✅ Found 1 countries
    ✅ Found 1 curricula
  🔗 Testing relationship queries...
    ✅ Country has 1 curricula
  ✅ All basic operations passed!
```

### **Step 6: Clean Up Test Data**
```bash
python test_database.py --cleanup
```

**Expected Output:**
```
🧹 Cleaning up test data...
✅ Cleaned up 2 test records
```

---

## 🔍 **Schema Validation Details**

### **What Gets Validated:**

1. **Table Existence** - All expected tables are present
2. **Column Structure** - Column types, constraints, and relationships
3. **Indexes** - Primary keys, foreign keys, and performance indexes
4. **Relationships** - Foreign key constraints and referential integrity

### **Expected Tables:**
- `countries` - Country information
- `curricula` - Curriculum records
- `subjects` - Academic subjects
- `grade_levels` - Educational grade levels
- `curriculum_structures` - Curriculum organization
- `topics` - Specific topics within subjects
- `learning_objectives` - Learning goals
- `topic_contents` - Topic content areas
- `users` - User accounts
- `lesson_plans` - Lesson plan records
- `lesson_resources` - AI-generated resources
- `contexts` - Local context information

---

## 🚨 **Troubleshooting Common Issues**

### **Issue 1: Connection Failed**
```bash
❌ Database connection failed: connection to server failed
```

**Solutions:**
1. Check `DATABASE_URL` in your `.env.test` file
2. Verify database server is running
3. Check firewall and network settings
4. Verify database credentials

### **Issue 2: Tables Not Created**
```bash
❌ Failed to create tables: relation "users" already exists
```

**Solutions:**
1. Check if tables already exist: `python migrate_database.py status`
2. Reset database if needed: `python migrate_database.py reset`
3. Check for schema conflicts

### **Issue 3: Import Errors**
```bash
❌ ModuleNotFoundError: No module named 'models'
```

**Solutions:**
1. Ensure you're in the `apps/backend` directory
2. Check Python path: `python -c "import sys; print(sys.path)"`
3. Verify all required packages are installed

---

## 🔒 **Security Considerations**

### **Test Environment Security:**
- ✅ **Separate Database** - No production data risk
- ✅ **Test Credentials** - Different from production
- ✅ **Debug Mode** - Full error details for testing
- ✅ **Isolated Testing** - No impact on production

### **Production Migration:**
- ⚠️ **Backup First** - Always backup before migration
- ⚠️ **Test Locally** - Test migrations in test environment first
- ⚠️ **Rollback Plan** - Have a plan to revert changes
- ⚠️ **Maintenance Window** - Schedule migrations during low traffic

---

## 📊 **Monitoring and Maintenance**

### **Regular Testing Schedule:**
1. **Daily** - Connection tests
2. **Weekly** - Schema validation
3. **Monthly** - Full test suite
4. **Before Deployments** - Complete validation

### **Performance Monitoring:**
```bash
# Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public';

# Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes;
```

---

## 🎉 **Success Indicators**

### **✅ Database is Ready When:**
1. **Connection Test** - Passes
2. **Table Creation** - All tables created
3. **Schema Validation** - All expected tables present
4. **Basic Operations** - CRUD operations work
5. **Cleanup** - Test data removed successfully

### **📋 Final Checklist:**
- [ ] Database connection successful
- [ ] All tables created
- [ ] Schema validation passed
- [ ] Basic operations working
- [ ] Test data cleaned up
- [ ] Ready for application testing

---

## 🚀 **Next Steps After Database Setup**

1. **Test API Endpoints** - Verify backend functionality
2. **Test Frontend Integration** - Check frontend-backend communication
3. **Load Test Data** - Add sample curriculum data
4. **User Acceptance Testing** - Test with stakeholders
5. **Performance Testing** - Test with realistic data volumes

---

## 📞 **Getting Help**

### **Common Commands Reference:**
```bash
# Quick health check
python test_database.py --test-connection

# Full validation
python test_database.py --full-test

# Migration status
python migrate_database.py status

# Run migrations
python migrate_database.py migrate
```

### **Debug Mode:**
Set `DEBUG=true` in your `.env.test` file to see detailed SQL queries and error information.

**Happy Database Testing! 🗄️**
