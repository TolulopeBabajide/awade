# Development Guide

## 🚀 Getting Started

Welcome to the Awade development environment! This guide will help you set up and contribute to the AI-powered educator support platform.

## 📋 Prerequisites

### Required Software
- **Python 3.10+** - Backend development
- **Node.js 18+** - Frontend development (optional)
- **PostgreSQL 13+** - Database
- **Git** - Version control
- **Docker** - Containerization (recommended)

### Recommended Tools
- **Cursor** - AI-assisted development
- **VS Code** - Code editor
- **Postman** - API testing
- **pgAdmin** - Database management

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-username/awade.git
cd awade

# Run the setup script
./scripts/setup.sh
```

### Option 2: Manual Setup
```bash
# 1. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r apps/backend/requirements.txt

# 2. Set up environment variables
cp env.example .env
# Edit .env with your actual values

# 3. Set up frontend (optional)
cd apps/frontend
npm install
cd ../..

# 4. Start PostgreSQL (if not using Docker)
# Install and start PostgreSQL service
```

### Option 3: Docker Setup
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🏗️ Project Structure

```
awade/
├── apps/
│   ├── backend/           # FastAPI application
│   │   ├── main.py       # Application entry point
│   │   └── requirements.txt
│   └── frontend/         # React frontend
│       ├── package.json
│       └── src/
├── packages/
│   ├── ai/              # AI logic and prompts
│   │   ├── prompts.py   # Prompt templates
│   │   └── gpt_service.py
│   └── shared/          # Shared models
│       └── models.py    # Pydantic models
├── docs/                # Documentation
├── scripts/             # Automation scripts
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
export DATABASE_URL="postgres://user:pass@localhost:5432/awade"
```

### 2. Backend Development
```bash
# Start the backend server
cd apps/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

### 3. Frontend Development
```bash
# Start the frontend development server
cd apps/frontend
npm run dev

# Access the application
open http://localhost:3000
```

### 4. Database Management
```bash
# Using Docker
docker-compose exec postgres psql -U awade_user -d awade

# Using local PostgreSQL
psql -U awade_user -d awade
```

## 🧪 Testing

### Backend Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
cd apps/backend
pytest

# Run with coverage
pytest --cov=.
```

### Frontend Testing
```bash
# Run tests
cd apps/frontend
npm test

# Run with coverage
npm run test:coverage
```

### Integration Testing
```bash
# Test the complete stack
docker-compose up -d
./scripts/test-integration.sh
```

## 📝 Code Standards

### Python (Backend)
- **Formatter**: Black
- **Linter**: Flake8
- **Type Checking**: mypy
- **Docstrings**: Google style

```bash
# Format code
black apps/backend/ packages/

# Lint code
flake8 apps/backend/ packages/

# Type check
mypy apps/backend/ packages/
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

## 🔍 Debugging

### Backend Debugging
```bash
# Enable debug mode
export DEBUG=True

# Use Python debugger
import pdb; pdb.set_trace()

# Check logs
tail -f logs/awade.log
```

### Frontend Debugging
```bash
# Enable React DevTools
# Install browser extension

# Use browser dev tools
# Check console for errors
```

### Database Debugging
```bash
# Check database connection
python -c "from sqlalchemy import create_engine; print(create_engine('postgres://...').connect())"

# View database logs
docker-compose logs postgres
```

## 🚀 Deployment

### Development Deployment
```bash
# Build and run with Docker
docker-compose up --build

# Or deploy to development server
./scripts/deploy-dev.sh
```

### Production Deployment
```bash
# Set production environment
export ENVIRONMENT=production

# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
./scripts/deploy-prod.sh
```

## 📚 MCP Integration

The project includes MCP (Model Context Protocol) servers for AI-assisted development:

### Available MCP Servers
- **`openapi`** - API documentation
- **`docs`** - Project documentation
- **`code`** - Source code access
- **`db`** - Database schema
- **`env`** - Environment configuration

### Using MCP with Cursor
1. Install the MCP extension
2. Configure `mcp.json` in your workspace
3. Use AI assistants for development tasks

## 🤝 Contributing

### Before Contributing
1. Read the [Design Brief](../../awade_design_brief.md)
2. Review [Security Guidelines](../../SECURITY.md)
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

## 🆘 Troubleshooting

### Common Issues

#### Python Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### Docker Issues
```bash
# Clean up containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Check logs
docker-compose logs
```

## 📞 Getting Help

- **Documentation**: Check the [docs](../README.md) directory
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Security**: Follow [security guidelines](../../SECURITY.md)

## 🔗 Useful Links

- [API Documentation](../api/README.md)
- [Design Brief](../../awade_design_brief.md)
- [Security Guidelines](../../SECURITY.md)
- [Contributing Guidelines](contributing.md) 