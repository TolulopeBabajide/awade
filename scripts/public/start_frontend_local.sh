#!/bin/bash

# Script to start Awade Frontend locally
# Backend services should be running in Docker first

set -e

echo "🚀 Starting Awade Frontend locally..."

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

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
}

# Check if npm is installed
check_npm() {
    print_status "Checking npm installation..."
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
}

# Check if backend services are running
check_backend() {
    print_status "Checking if backend services are running..."
    
    # Check if port 8000 is in use (backend API)
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warning "Backend API is not running on port 8000"
        print_warning "Please start backend services first with: ./scripts/start_backend_services.sh"
        print_warning "Or run: docker-compose up -d postgres redis backend"
    else
        print_success "Backend API is running"
    fi
}

# Setup frontend dependencies
setup_frontend() {
    print_status "Setting up frontend dependencies..."
    
    cd apps/frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_status "Frontend dependencies already installed"
    fi
    
    cd ../..
}

# Start frontend development server
start_frontend() {
    print_status "Starting frontend development server..."
    
    cd apps/frontend
    
    print_success "Frontend is starting..."
    echo ""
    echo "🌐 Frontend will be available at: http://localhost:3000 (or next available port)"
    echo "🔄 Hot reload is enabled - changes will automatically refresh"
    echo "⏹️  Press Ctrl+C to stop the frontend"
    echo ""
    
    # Start the development server
    npm run dev
}

# Main execution
check_node
check_npm
check_backend
setup_frontend
start_frontend 