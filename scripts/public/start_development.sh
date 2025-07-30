#!/bin/bash

# Awade Development Startup Script
# This script starts all services and prepares the environment for the 3-day development sprint

set -e

echo "🚀 Starting Awade Development Environment for 3-Day Sprint..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    print_success "Node.js $(node --version) found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    print_success "npm $(npm --version) found"
}

# Setup environment
setup_environment() {
    print_header "Setting up Environment"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your actual values (especially DATABASE_URL and OPENAI_API_KEY)"
    else
        print_success ".env file exists"
    fi
    
    # Setup frontend dependencies
    print_status "Setting up frontend dependencies..."
    cd apps/frontend
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Frontend dependencies installed"
    else
        print_success "Frontend dependencies already installed"
    fi
    cd ../..
}

# Start backend services
start_backend_services() {
    print_header "Starting Backend Services"
    
    # Stop any existing containers
    print_status "Stopping any existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Start backend services
    print_status "Starting PostgreSQL, Redis, and Backend API..."
    docker-compose up -d postgres redis backend
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 15
    
    # Check if services are running
    print_status "Checking service status..."
    if docker-compose ps | grep -q "Up"; then
        print_success "Backend services are running!"
    else
        print_error "Failed to start services. Check the logs above."
        exit 1
    fi
}

# Initialize database with curriculum data
initialize_database() {
    print_header "Initializing Database"
    
    print_status "Running database migrations..."
    cd apps/backend
    python -c "
import sys
sys.path.append('..')
from database import create_tables
create_tables()
print('Database tables created successfully')
"
    cd ../..
    
    print_status "Adding curriculum data..."
    python scripts/add_curriculum_data.py
    
    print_success "Database initialized with curriculum data"
}

# Start frontend
start_frontend() {
    print_header "Starting Frontend"
    
    print_status "Starting frontend development server..."
    cd apps/frontend
    print_success "Frontend is starting..."
    echo ""
    echo "🌐 Frontend will be available at: http://localhost:3000 (or next available port)"
    echo "🔄 Hot reload is enabled - changes will automatically refresh"
    echo ""
    
    # Start the development server in background
    npm run dev &
    FRONTEND_PID=$!
    
    cd ../..
    
    # Wait a moment for frontend to start
    sleep 5
    
    print_success "Frontend started with PID: $FRONTEND_PID"
}

# Show development information
show_development_info() {
    print_header "Development Environment Ready!"
    
    echo ""
    echo "🎯 3-DAY DEVELOPMENT SPRINT PRIORITIES:"
    echo "=========================================="
    echo "1. ✅ Complete Lesson Plan Editing Interface"
    echo "2. ✅ Implement PDF Export Service"
    echo "3. ✅ Add Local Context Input Forms"
    echo "4. ✅ Enhance AI Context Processing"
    echo ""
    
    echo "🌐 Available Services:"
    echo "======================"
    echo "🔗 API Documentation: http://localhost:8000/docs"
    echo "🔗 API Base URL: http://localhost:8000"
    echo "🌐 Frontend: http://localhost:3000 (or next available port)"
    echo "🗄️  Database: localhost:5432"
    echo "🔴 Redis: localhost:6379"
    echo ""
    
    echo "📁 Key Files to Work On:"
    echo "========================"
    echo "📝 Lesson Plan Editing: apps/frontend/src/pages/EditLessonPlanPage.tsx"
    echo "📝 PDF Export: apps/backend/services/pdf_service.py"
    echo "📝 Context Forms: apps/frontend/src/pages/DashboardPage.tsx"
    echo "📝 AI Processing: packages/ai/gpt_service.py"
    echo ""
    
    echo "🛠️  Useful Commands:"
    echo "==================="
    echo "📊 View service logs: docker-compose logs -f"
    echo "🔄 Restart backend: docker-compose restart backend"
    echo "🗄️  Database shell: docker-compose exec postgres psql -U awade_user -d awade"
    echo "🧹 Clean up: docker-compose down"
    echo ""
    
    echo "📚 Documentation:"
    echo "================"
    echo "📖 API Contracts: contracts/api-contracts.json"
    echo "📖 Project Workflow: docs/internal/project-workflow.md"
    echo "📖 Database Schema: apps/backend/models.py"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    start_backend_services
    initialize_database
    start_frontend
    show_development_info
    
    print_success "🎉 Development environment is ready!"
    print_status "Press Ctrl+C to stop all services"
    
    # Keep the script running and show logs
    docker-compose logs -f
}

# Run main function
main 