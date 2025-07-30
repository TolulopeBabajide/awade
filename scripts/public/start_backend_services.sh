#!/bin/bash

# Script to start Awade Backend Services (Database + API) using Docker
# Frontend should be run locally with: npm run dev

set -e

echo "🚀 Starting Awade Backend Services with Docker..."

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

# Check if Docker is running
check_docker() {
    print_status "Checking Docker installation..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! docker-compose --version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to cleanup on exit
cleanup() {
    print_status "🧹 Cleaning up..."
    docker-compose down
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Check prerequisites
check_docker
check_docker_compose

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file with your actual values"
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Start backend services (postgres, backend, redis)
print_status "Starting backend services..."
docker-compose up -d postgres redis backend

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Check if services are running
print_status "Checking service status..."
if docker-compose ps | grep -q "Up"; then
    print_success "Backend services are running!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 API Documentation: http://localhost:8000/docs"
    echo "🔗 API Base URL: http://localhost:8000"
    echo "🗄️  Database: localhost:5432"
    echo "🔴 Redis: localhost:6379"
    echo ""
    echo "💡 To run the frontend locally:"
    echo "   cd apps/frontend && npm run dev"
    echo ""
    echo "⏹️  Press Ctrl+C to stop all services"
    
    # Keep the script running
    docker-compose logs -f
else
    print_error "Failed to start services. Check the logs above."
    exit 1
fi 