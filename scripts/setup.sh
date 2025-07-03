#!/bin/bash

# Awade Development Setup Script
# This script sets up the development environment for the Awade project

set -e

echo "🚀 Setting up Awade development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.10+ first."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_warning "Node.js is not installed. Frontend development will not be available."
    fi
}

# Check if PostgreSQL is installed
check_postgres() {
    print_status "Checking PostgreSQL installation..."
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found"
    else
        print_warning "PostgreSQL is not installed. You'll need to install it for database functionality."
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    source venv/bin/activate
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r apps/backend/requirements.txt
    print_success "Python dependencies installed"
}

# Setup frontend
setup_frontend() {
    if command -v node &> /dev/null; then
        print_status "Setting up frontend..."
        cd apps/frontend
        npm install
        print_success "Frontend dependencies installed"
        cd ../..
    else
        print_warning "Skipping frontend setup - Node.js not available"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p cache
    mkdir -p apps/backend/app
    print_success "Directories created"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your actual configuration values"
    else
        print_status "Environment file already exists"
    fi
}

# Generate OpenAPI spec
generate_openapi() {
    print_status "Generating OpenAPI specification..."
    cd apps/backend
    python -c "
import sys
sys.path.append('.')
from main import app
import json
openapi_spec = app.openapi()
with open('app/openapi.json', 'w') as f:
    json.dump(openapi_spec, f, indent=2)
"
    cd ../..
    print_success "OpenAPI specification generated"
}

# Main setup function
main() {
    print_status "Starting Awade development setup..."
    
    check_python
    check_node
    check_postgres
    create_directories
    setup_python_env
    setup_frontend
    setup_env
    generate_openapi
    
    print_success "🎉 Awade development environment setup complete!"
    echo ""
    print_status "Next steps:"
    echo "  1. Edit .env file with your configuration"
    echo "  2. Start the backend: cd apps/backend && uvicorn main:app --reload"
    echo "  3. Start the frontend: cd apps/frontend && npm run dev"
    echo ""
    print_status "For more information, see README.md"
}

# Run main function
main "$@" 