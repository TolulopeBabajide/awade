# Development Guide

## 🚀 Getting Started

Welcome to the Awade development environment! This guide will help you set up and contribute to the AI-powered educator support platform for African teachers.

## 📋 Prerequisites

### Required Software
- **Python 3.10+** - Backend development
- **Node.js 18+** - Frontend development
- **PostgreSQL 13+** - Database
- **Git** - Version control
- **Docker & Docker Compose** - Containerization (recommended)

### Recommended Tools
- **Cursor** - AI-assisted development with MCP integration
- **VS Code** - Code editor with Python/TypeScript extensions
- **Postman** - API testing and documentation
- **pgAdmin** - Database management
- **DBeaver** - Universal database tool

## 🛠️ Quick Setup

### Option 1: Docker Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/TolulopeBabajide/awade.git
cd awade

# Copy environment file
cp env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Local Development Setup
```bash
# 1. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r apps/backend/requirements.txt

# 2. Set up environment variables
cp env.example .env
# Edit .env with your actual values

# 3. Set up frontend
cd apps/frontend
npm install
cd ../..

# 4. Start PostgreSQL (if not using Docker)
# Install and start PostgreSQL service
```

### Option 3: Hybrid Setup (Backend Local, Frontend Docker)
```bash
# Start only database and frontend with Docker
docker-compose up postgres frontend -d

# Run backend locally
cd apps/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🏗️ Project Structure

```
awade/
├── apps/
│   ├── backend/           # FastAPI application
│   │   ├── main.py       # Application entry point
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── routers/      # API route handlers
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── requirements.txt
│   └── frontend/         # React frontend
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── pages/       # Page components
│       │   ├── services/    # API services
│       │   └── types/       # TypeScript types
│       └── package.json
├── packages/
│   ├── ai/              # AI logic and prompts
│   │   ├── prompts.py   # Prompt templates
│   │   └── gpt_service.py
│   └── shared/          # Shared models
│       └── models.py    # Pydantic models
├── docs/                # Documentation
│   ├── public/         # Public documentation
│   └── private/        # Internal documentation
├── scripts/             # Automation scripts
│   ├── public/         # Public scripts
│   └── private/        # Internal scripts
├── docker-compose.yml   # Development environment
└── README.md
```

## 🔧 Development Workflow

### 1. Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export OPENAI_API_KEY="your_api_key"
export DATABASE_URL="postgresql://awade_user:password@localhost:5432/awade"
export SECRET_KEY="your_secret_key"
export JWT_ALGORITHM="HS256"
```

### 2. Backend Development

#### Import Structure
The backend uses a **flat import structure** for compatibility with both script execution and module imports. This ensures the backend can be run from any directory and works with contract testing.

**Key Points:**
- All imports use flat paths (e.g., `from models import ...`, `from database import ...`)
- Python path is automatically adjusted in `main.py` and router files
- Services and utilities use relative imports within their packages
- This structure works for both development and production environments

**Import Examples:**
```python
# ✅ Correct - Flat imports (used in main.py and routers)
from models import LessonPlan, User
from database import get_db
from services.curriculum_service import CurriculumService

# ✅ Correct - Relative imports (used within packages)
from ..models import CurriculumMap
from ..database import get_db

# ❌ Avoid - Absolute imports that break in script mode
from apps.backend.models import LessonPlan
```

#### Starting the Backend
```bash
# Start the backend server
cd apps/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or from project root (imports will work correctly)
cd /path/to/awade
uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

#### Database Initialization
```bash
# Initialize database with tables and seed data
cd apps/backend
python init_db.py

# Or using Docker
docker-compose exec backend python init_db.py
```

#### Contract Testing
The flat import structure enables contract testing to work properly:
```bash
# Run contract tests (will start backend automatically)
python scripts/private/contract_testing.py --base-url http://localhost:8000 --start-server --save

# Run with Docker
python scripts/private/contract_testing.py --base-url http://localhost:8000 --start-containers --save
```

### 3. Frontend Development
```bash
# Start the frontend development server
cd apps/frontend
npm run dev

# Or using Docker
docker-compose up frontend

# Access the application
open http://localhost:3000
```

### 4. Database Management
```bash
# Using Docker
docker-compose exec postgres psql -U awade_user -d awade

# Using local PostgreSQL
psql -U awade_user -d awade

# Create test user
python scripts/private/create_test_user.py
```

## 🧪 Testing

### Backend Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
cd apps/backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_curriculum_mapping.py -v
```

### Frontend Testing
```bash
# Run tests
cd apps/frontend
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch
```

### Integration Testing
```bash
# Test the complete stack
docker-compose up -d
python scripts/private/contract_testing.py --start-containers --save

# Test curriculum mapping
python scripts/private/test_curriculum_mapping.py
```

### Documentation Testing
```bash
# Check documentation coverage
python scripts/private/doc_coverage.py --save

# Generate coverage dashboard
python scripts/private/generate_coverage_dashboard.py
```

## 📝 Code Standards

### Python (Backend)
- **Formatter**: Black
- **Linter**: Flake8
- **Type Checking**: mypy
- **Docstrings**: Google style
- **Import Sorting**: isort

```bash
# Format code
black apps/backend/ packages/

# Sort imports
isort apps/backend/ packages/

# Lint code
flake8 apps/backend/ packages/

# Type check
mypy apps/backend/ packages/

# Run all checks
./scripts/private/lint_backend.sh
```

### JavaScript/TypeScript (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Checking**: TypeScript

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check

# Fix linting issues
npm run lint:fix
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new lesson planning feature"

# Push and create PR
git push origin feature/your-feature-name
```

### Pre-commit Hooks
The project includes pre-commit hooks that automatically:
- Check documentation coverage
- Validate markdown syntax
- Verify environment files
- Run MCP health checks
- Validate API contracts

## 🔍 Debugging

### Backend Debugging
```bash
# Enable debug mode
export DEBUG=True

# Use Python debugger
import pdb; pdb.set_trace()

# Check logs
tail -f logs/awade.log

# Debug with Docker
docker-compose logs backend -f
```

### Frontend Debugging
```bash
# Enable React DevTools
# Install browser extension

# Use browser dev tools
# Check console for errors

# Debug with Docker
docker-compose logs frontend -f
```

### Database Debugging
```bash
# Check database connection
python -c "from sqlalchemy import create_engine; print(create_engine('postgresql://...').connect())"

# View database logs
docker-compose logs postgres

# Check database schema
docker-compose exec postgres psql -U awade_user -d awade -c "\dt"
```

### API Debugging
```bash
# Test API endpoints
curl http://localhost:8000/health

# Check OpenAPI spec
curl http://localhost:8000/openapi.json

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@awade.com", "password": "testpass123"}'
```

## 🚀 Deployment

### Development Deployment
```bash
# Build and run with Docker
docker-compose up --build

# Or deploy to development server
./scripts/public/deploy-dev.sh
```

### Production Deployment
```bash
# Set production environment
export ENVIRONMENT=production

# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
./scripts/public/deploy-prod.sh
```

### Health Checks
```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check database
docker-compose exec postgres pg_isready -U awade_user
```

## 📚 MCP Integration

The project includes MCP (Model Context Protocol) servers for AI-assisted development:

### Available MCP Servers
- **`openapi`** - API documentation and schema
- **`docs`** - Project documentation access
- **`code`** - Source code analysis and generation
- **`db`** - Database schema and queries
- **`env`** - Environment configuration management
- **`internal`** - Internal documentation
- **`external`** - External documentation
- **`design`** - Design brief and specifications

### Using MCP with Cursor
1. Install the MCP extension in Cursor
2. Configure `mcp.json` in your workspace
3. Use AI assistants for development tasks
4. Access project context through MCP servers

### MCP Health Check
```bash
# Check MCP server status
python scripts/private/mcp_health_check.py

# View MCP configuration
cat mcp.json
```

## 🐘 Database Management

### Initial Setup
```bash
# 1. Set environment variables in your `.env` file:
ADMIN_EMAIL=admin@awade.org
ADMIN_PASSWORD=secure_password
EDUCATOR_EMAIL=teacher@awade.org
EDUCATOR_PASSWORD=secure_password

# 2. Initialize database
python apps/backend/init_db.py

# 3. Create test user (optional)
python scripts/private/create_test_user.py
```

### Database Migrations
```bash
# Run migrations
cd apps/backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Check migration status
alembic current
```

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U awade_user awade > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U awade_user awade < backup_file.sql
```

## 🤝 Contributing

### Before Contributing
1. Read the [Design Brief](../../../awade_design_brief.md)
2. Review [Security Guidelines](../../../SECURITY.md)
3. Check existing issues and PRs
4. Join the development discussions

### Contribution Process
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] API contracts are maintained
- [ ] Documentation coverage is maintained

### Documentation Standards
- [ ] All new functions have docstrings
- [ ] API endpoints are documented
- [ ] Configuration changes are documented
- [ ] User-facing changes have user guide updates

## 🆘 Troubleshooting

### Common Issues

#### Backend Import Issues

**Problem**: `ModuleNotFoundError: No module named 'apps'`
```bash
# Error when running from backend directory
cd apps/backend
python main.py  # ❌ Fails
```

**Solution**: The backend uses flat imports for compatibility. Use one of these approaches:
```bash
# Option 1: Run from backend directory (recommended)
cd apps/backend
uvicorn main:app --reload

# Option 2: Run from project root
cd /path/to/awade
uvicorn apps.backend.main:app --reload

# Option 3: Use the contract testing script
python scripts/private/contract_testing.py --start-server
```

#### Contract Testing Issues

**Problem**: Contract tests fail with import errors
```bash
python scripts/private/contract_testing.py --start-server  # ❌ Fails
```

**Solution**: 
1. Ensure you're running from the project root directory
2. Check that all backend imports use flat structure
3. Verify the backend can start manually first:
   ```bash
   cd apps/backend
   uvicorn main:app --reload  # Should work
   ```

#### Docker Issues
```bash
# Clean up containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Check logs
docker-compose logs

# Reset database
docker-compose down -v
docker-compose up postgres -d
python apps/backend/init_db.py
```

#### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify connection string
echo $DATABASE_URL

# Test connection
docker-compose exec postgres psql -U awade_user -d awade -c "SELECT 1;"
```

#### Frontend Build Issues
```bash
# Clear node modules
cd apps/frontend
rm -rf node_modules package-lock.json
npm install

# Rebuild with Docker
docker-compose build frontend --no-cache
```

## 📞 Getting Help

- **Documentation**: Check the [docs](../../README.md) directory
- **API Documentation**: [API Guide](../api/README.md)
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Security**: Follow [security guidelines](../../../SECURITY.md)

## 🔗 Useful Links

- [API Documentation](../api/README.md)
- [Frontend Development](frontend.md)
- [Contributing Guidelines](contributing.md)
- [Design Brief](../../../awade_design_brief.md)
- [Security Guidelines](../../../SECURITY.md)
- [Deployment Guide](../deployment/README.md)

---

*This development guide is maintained by the Awade development team. For questions or suggestions, please create an issue or pull request.*

*Last updated: January 2024* 