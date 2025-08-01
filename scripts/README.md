# Awade Scripts

This directory contains utility scripts for the Awade project, organized by visibility and purpose.

## 📁 Directory Structure

### `public/` - Public Scripts
These scripts are safe for public use and help with development setup and workflow.

**Available Scripts:**
- `start_development.sh` - Complete development environment setup
- `start_frontend_local.sh` - Frontend development server setup
- `start_backend_services.sh` - Backend services setup
- `setup_workflow.sh` - Development workflow configuration
- `setup.sh` - Initial project setup
- `run_frontend_docker.sh` - Docker-based frontend setup
- `requirements.txt` - Python dependencies for scripts

### `private/` - Private Scripts ⚠️
These scripts contain sensitive operations, development tools, or internal testing utilities. They should not be used in production environments.

**Private Scripts (Development/Testing Only):**
- `create_test_user.py` - Creates test users (contains hardcoded credentials)
- `create_admin_user.py` - Creates admin users (contains default credentials)
- `drop_all_except_users.py` - Dangerous database operation
- `create_new_schema.py` - Database schema creation (use alembic instead)
- `add_curriculum_data.py` - Development data seeding
- `contract_testing.py` - Internal API contract validation
- `doc_coverage.py` - Documentation coverage analysis
- `mcp_health_check.py` - Internal system monitoring
- `monitor_dashboard.py` - Internal monitoring tools
- `generate_coverage_dashboard.py` - Internal reporting tools
- `test_acceptance_criteria.py` - Internal testing utilities
- `test_curriculum_mapping.py` - Internal testing utilities
- `update_api_docs.py` - Internal documentation generation

## 🚨 Security Notice

**Never use private scripts in production environments!** These scripts may contain:
- Hardcoded credentials
- Dangerous database operations
- Development-only configurations
- Internal testing logic

## 🛠️ Usage

### For New Developers
```bash
# Set up the complete development environment
./scripts/public/setup.sh

# Start development services
./scripts/public/start_development.sh
```

### For Local Development
```bash
# Start frontend locally
./scripts/public/start_frontend_local.sh

# Start backend services
./scripts/public/start_backend_services.sh
```

## 🔒 Private Scripts Access

Private scripts are available for development and testing purposes only. If you need access to these scripts:

1. **For Development**: Use them in a development environment only
2. **For Testing**: Ensure you're working with test data only
3. **For Production**: Never use these scripts in production

## 📝 Contributing

When adding new scripts:
- **Public scripts**: Place in `public/` directory
- **Private scripts**: Place in `private/` directory
- **Security**: Never include hardcoded credentials
- **Documentation**: Always include usage instructions 