# Contract Testing Guide - Ensuring API Consistency

> **Status**: ✅ Active

This guide explains how to use the contract testing system to ensure API consistency between frontend and backend in the Awade platform.

## 🎯 Overview

Contract testing validates that the API implementation matches the defined contracts, ensuring that frontend and backend remain in sync and preventing integration issues.

## 🔧 How Contract Testing Works

### **Contract Definition**
- **OpenAPI Specification**: Automatically generated from FastAPI backend
- **Contract Configuration**: Defined in `contracts/api-contracts.json`
- **Schema Validation**: JSON Schema validation for requests and responses
- **Sample Data Generation**: Automatic test data generation from schemas

### **Testing Process**
1. **Load OpenAPI Spec** - Read the current API specification
2. **Generate Tests** - Create test cases from API endpoints
3. **Validate Schemas** - Check request/response data against schemas
4. **Run Tests** - Execute API calls and validate responses
5. **Generate Reports** - Create detailed test reports

## 📋 Contract Testing Features

### **Automatic Test Generation**
- **Endpoint Discovery** - Automatically finds all API endpoints
- **Schema Extraction** - Extracts request and response schemas
- **Test Case Creation** - Generates comprehensive test cases
- **Sample Data** - Creates realistic test data from schemas

### **Comprehensive Validation**
- **Request Validation** - Validates request data against schemas
- **Response Validation** - Validates response data against schemas
- **Status Code Checking** - Verifies expected HTTP status codes
- **Error Handling** - Tests error scenarios and responses

### **Detailed Reporting**
- **Test Results** - Pass/fail status for each test
- **Error Details** - Specific validation errors and issues
- **Performance Metrics** - Response times and success rates
- **Trend Analysis** - Historical test result tracking

## 🚀 Running Contract Tests

### **Local Development**
```bash
# Basic contract testing
python scripts/contract_testing.py

# With custom base URL
python scripts/contract_testing.py --base-url http://localhost:8000

# Start server and run tests
python scripts/contract_testing.py --start-server --save

# Custom OpenAPI spec path
python scripts/contract_testing.py --spec-path apps/backend/app/openapi.json
```

### **CI/CD Integration**
Contract tests run automatically in the CI/CD pipeline:
- **Pre-commit**: Validates contracts before commits
- **Pull Requests**: Runs full contract test suite
- **Main Branch**: Ensures deployment readiness

### **Command Line Options**
```bash
--base-url URL          # API base URL (default: http://localhost:8000)
--spec-path PATH        # OpenAPI spec path (default: apps/backend/app/openapi.json)
--report-path PATH      # Test report output path (default: logs/contract_test_report.json)
--start-server          # Start backend server before testing
--save                  # Save detailed test report
```

## 📊 Contract Configuration

### **API Contracts File**
Located at `contracts/api-contracts.json`, this file defines:

```json
{
  "contracts": {
    "lesson_plans": {
      "create_lesson_plan": {
        "endpoint": "/api/lesson-plans",
        "method": "POST",
        "request_schema": { /* JSON Schema */ },
        "response_schema": { /* JSON Schema */ },
        "expected_status": 201
      }
    }
  },
  "test_configuration": {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3,
    "parallel_tests": false,
    "generate_samples": true,
    "validate_responses": true
  }
}
```

### **Schema Validation**
- **Request Schemas** - Validate incoming request data
- **Response Schemas** - Validate outgoing response data
- **Type Checking** - Ensure correct data types
- **Required Fields** - Verify mandatory fields are present
- **Format Validation** - Check email, date, UUID formats

## 🔍 Test Categories

### **Lesson Planning APIs**
- **Create Lesson Plan** - POST `/api/lesson-plans`
- **Get Lesson Plans** - GET `/api/lesson-plans`
- **Update Lesson Plan** - PUT `/api/lesson-plans/{id}`
- **Delete Lesson Plan** - DELETE `/api/lesson-plans/{id}`

### **Training Module APIs**
- **Note**: Training module endpoints removed from MVP scope
- **Update Progress** - POST `/api/user-progress`
- **Get Progress** - GET `/api/user-progress`

### **User Management APIs**
- **User Authentication** - POST `/api/auth/login`
- **User Registration** - POST `/api/auth/register`
- **User Profile** - GET `/api/users/profile`
- **Update Profile** - PUT `/api/users/profile`

### **Bookmark APIs**
- **Create Bookmark** - POST `/api/bookmarks`
- **Get Bookmarks** - GET `/api/bookmarks`
- **Delete Bookmark** - DELETE `/api/bookmarks/{id}`

## 📈 Test Reports

### **Report Structure**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "summary": {
    "total_tests": 15,
    "passed": 14,
    "failed": 1,
    "errors": 0,
    "skipped": 0
  },
  "results": [
    {
      "test_name": "POST /api/lesson-plans",
      "endpoint": "/api/lesson-plans",
      "method": "POST",
      "status": "passed",
      "errors": [],
      "warnings": [],
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### **Report Analysis**
- **Success Rate** - Percentage of passing tests
- **Failure Patterns** - Common failure types
- **Performance Trends** - Response time analysis
- **Coverage Metrics** - API endpoint coverage

## 🔧 Integration with Workflow

### **Pre-commit Hook**
Contract testing is integrated into the pre-commit hook:
- **Automatic Validation** - Runs on API changes
- **Quick Feedback** - Immediate validation results
- **Prevention** - Blocks commits with contract violations

### **CI/CD Pipeline**
Contract tests run in the CI/CD pipeline:
- **Automated Testing** - Runs on every PR and push
- **Artifact Generation** - Creates test reports
- **Deployment Gates** - Prevents deployment on failures

### **Development Workflow**
1. **Make API Changes** - Modify backend endpoints
2. **Update Contracts** - Update contract definitions if needed
3. **Run Tests** - Validate changes with contract tests
4. **Commit Changes** - Pre-commit hook validates contracts
5. **CI/CD Validation** - Full test suite runs in pipeline

## 🛠️ Troubleshooting

### **Common Issues**

#### **Schema Validation Failures**
```bash
# Check OpenAPI spec generation
python scripts/update_api_docs.py

# Validate JSON schema
python -m json.tool apps/backend/app/openapi.json
```

#### **Server Connection Issues**
```bash
# Check if server is running
curl http://localhost:8000/health

# Start server manually
cd apps/backend && uvicorn main:app --reload
```

#### **Test Data Generation Issues**
```bash
# Check schema definitions
python scripts/contract_testing.py --spec-path apps/backend/app/openapi.json

# Validate contract configuration
python -m json.tool contracts/api-contracts.json
```

### **Debugging Tips**
- **Verbose Output** - Use `--verbose` flag for detailed logs
- **Single Endpoint** - Test specific endpoints individually
- **Schema Inspection** - Review generated schemas manually
- **Network Debugging** - Check API responses with curl

## 📚 Best Practices

### **Contract Design**
- **Clear Schemas** - Define explicit request/response schemas
- **Validation Rules** - Include proper validation constraints
- **Error Handling** - Define error response schemas
- **Versioning** - Use semantic versioning for contracts

### **Testing Strategy**
- **Regular Testing** - Run tests frequently during development
- **Automated Validation** - Integrate into CI/CD pipeline
- **Comprehensive Coverage** - Test all API endpoints
- **Edge Cases** - Include boundary condition tests

### **Maintenance**
- **Keep Contracts Updated** - Update when APIs change
- **Review Test Results** - Analyze failure patterns
- **Performance Monitoring** - Track response times
- **Documentation** - Keep contract documentation current

## 🔗 Related Documentation

- **[API Contracts](api-contracts.md)** - Detailed API contract specifications
- **[Testing Guide](testing.md)** - General testing guidelines
- **[CI/CD Pipeline](../public/development/README.md)** - Pipeline configuration
- **[Backend Development](../public/development/README.md)** - Backend development guide

## 📞 Support

### **Getting Help**
- **Documentation** - Check this guide and related docs
- **Test Reports** - Review detailed test reports
- **Error Logs** - Check logs for specific error details
- **Community** - Ask questions in development discussions

### **Contributing**
- **Report Issues** - Create GitHub issues for problems
- **Suggest Improvements** - Propose enhancements to the system
- **Add Tests** - Contribute new contract test cases
- **Update Documentation** - Help improve this guide

---

*This guide will be updated as the contract testing system evolves.* 