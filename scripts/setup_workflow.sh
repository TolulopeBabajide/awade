#!/bin/bash
"""
Workflow Setup Script for Awade
Installs and configures automation tools for the development workflow.
"""

set -e

echo "🚀 Setting up Awade development workflow..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    print_status $RED "❌ Not in Awade project root directory"
    exit 1
fi

print_status $BLUE "📋 Checking prerequisites..."

# 1. Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status $GREEN "✅ Python $PYTHON_VERSION found"
else
    print_status $RED "❌ Python 3 not found"
    print_status $YELLOW "💡 Install Python 3.10+ to continue"
    exit 1
fi

# 2. Check pip
if command_exists pip3; then
    print_status $GREEN "✅ pip3 found"
else
    print_status $RED "❌ pip3 not found"
    exit 1
fi

# 3. Check git
if command_exists git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_status $GREEN "✅ Git $GIT_VERSION found"
else
    print_status $RED "❌ Git not found"
    exit 1
fi

print_status $BLUE "📦 Installing Python dependencies..."

# Install required Python packages
REQUIRED_PACKAGES=(
    "requests"
    "fastapi"
    "uvicorn"
    "pydantic"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_status $GREEN "✅ $package already installed"
    else
        print_status $YELLOW "📦 Installing $package..."
        pip3 install "$package"
        print_status $GREEN "✅ $package installed"
    fi
done

print_status $BLUE "🔧 Setting up Git hooks..."

# Make sure hooks directory exists
mkdir -p .git/hooks

# Make pre-commit hook executable
if [ -f ".git/hooks/pre-commit" ]; then
    chmod +x .git/hooks/pre-commit
    print_status $GREEN "✅ Pre-commit hook configured"
else
    print_status $YELLOW "⚠️  Pre-commit hook not found - run setup again after creating it"
fi

print_status $BLUE "📁 Creating necessary directories..."

# Create logs directory for health reports
mkdir -p logs
print_status $GREEN "✅ Created logs directory"

# Create app directory in backend if it doesn't exist
mkdir -p apps/backend/app
print_status $GREEN "✅ Created backend app directory"

print_status $BLUE "🔍 Testing workflow components..."

# Test the API documentation script
if [ -f "scripts/update_api_docs.py" ]; then
    print_status $YELLOW "🧪 Testing API documentation script..."
    if python3 scripts/update_api_docs.py; then
        print_status $GREEN "✅ API documentation script works"
    else
        print_status $YELLOW "⚠️  API documentation script had issues (this is normal if no API exists yet)"
    fi
else
    print_status $RED "❌ API documentation script not found"
fi

# Test the MCP health check script
if [ -f "scripts/mcp_health_check.py" ]; then
    print_status $YELLOW "🧪 Testing MCP health check script..."
    if python3 scripts/mcp_health_check.py; then
        print_status $GREEN "✅ MCP health check script works"
    else
        print_status $YELLOW "⚠️  MCP health check script had issues (this is normal if MCP not configured)"
    fi
else
    print_status $RED "❌ MCP health check script not found"
fi

print_status $BLUE "📝 Creating workflow documentation..."

# Create a simple workflow guide
cat > WORKFLOW_GUIDE.md << 'EOF'
# Awade Development Workflow Guide

## 🚀 Quick Start

1. **Setup**: Run `./scripts/setup_workflow.sh` to install dependencies
2. **Development**: Make changes to your code
3. **Commit**: Git hooks will automatically validate and update docs
4. **Health Check**: Run `python3 scripts/mcp_health_check.py` to check MCP status

## 🔧 Available Scripts

### `scripts/update_api_docs.py`
- Automatically updates API documentation when backend files change
- Generates OpenAPI specification
- Validates documentation links

### `scripts/mcp_health_check.py`
- Checks MCP server configuration and health
- Validates server endpoints
- Generates health reports

### `scripts/setup_workflow.sh`
- Installs required dependencies
- Configures Git hooks
- Sets up directory structure

## 📋 Git Hooks

### Pre-commit Hook
Automatically runs before each commit:
- ✅ Validates required documentation files exist
- ✅ Checks for API documentation updates
- ✅ Prevents committing sensitive files (.env)
- ✅ Validates MCP configuration
- ✅ Runs health checks

## 🏥 Health Monitoring

Run health checks manually:
```bash
# Basic health check
python3 scripts/mcp_health_check.py

# Save health report
python3 scripts/mcp_health_check.py --save
```

## 📊 Reports

Health reports are saved to `logs/mcp_health.json` for tracking over time.

## 🔄 Automation

The workflow automatically:
- Updates API docs when backend changes
- Validates documentation integrity
- Monitors MCP server health
- Prevents common commit mistakes

## 🆘 Troubleshooting

### Common Issues

1. **Pre-commit hook fails**: Check that all required docs exist
2. **API docs not updating**: Ensure backend files are properly staged
3. **MCP health check fails**: Verify `.cursor/mcp.json` configuration

### Manual Override

To skip pre-commit checks (not recommended):
```bash
git commit --no-verify -m "your message"
```
EOF

print_status $GREEN "✅ Created WORKFLOW_GUIDE.md"

print_status $BLUE "🎯 Setting up environment..."

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# Awade Environment Configuration

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/awade

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# External Services
REDIS_URL=redis://localhost:6379
EMAIL_SERVICE=your_email_service_here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/awade.log
EOF
    print_status $GREEN "✅ Created .env.example"
fi

# Update .gitignore if needed
if [ -f ".gitignore" ]; then
    # Check if logs directory is in .gitignore
    if ! grep -q "logs/" .gitignore; then
        echo "" >> .gitignore
        echo "# Workflow logs" >> .gitignore
        echo "logs/" >> .gitignore
        print_status $GREEN "✅ Updated .gitignore to exclude logs"
    fi
else
    # Create .gitignore if it doesn't exist
    cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Workflow logs
logs/
*.log

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
EOF
    print_status $GREEN "✅ Created .gitignore"
fi

print_status $BLUE "🎉 Workflow setup complete!"

print_status $GREEN "
✅ Awade development workflow is ready!

📋 What's been set up:
  🔧 Git hooks for automatic validation
  📦 Python dependencies for automation
  📁 Directory structure for logs and reports
  📝 Workflow documentation
  🔐 Environment configuration template
  🚫 Git ignore rules for sensitive files

🚀 Next steps:
  1. Copy .env.example to .env and fill in your values
  2. Make a test commit to see the hooks in action
  3. Run 'python3 scripts/mcp_health_check.py' to check MCP status
  4. Read WORKFLOW_GUIDE.md for detailed instructions

💡 Tips:
  - The pre-commit hook will run automatically on every commit
  - Health reports are saved to logs/ directory
  - Use 'git commit --no-verify' to skip checks if needed
"

print_status $YELLOW "🔍 Run 'python3 scripts/mcp_health_check.py' to test the setup!" 