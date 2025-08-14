#!/bin/bash

# Setup and Run JSS1 Mathematics Curriculum Population Script
# This script helps set up the environment and run the curriculum population

set -e

echo "🚀 Setting up and running JSS1 Mathematics Curriculum Population"
echo "================================================================"

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

# Check if we're in the right directory
if [ ! -f "populate_jss1_mathematics.py" ]; then
    print_error "This script must be run from the scripts directory"
    print_error "Please run: cd scripts && ./setup_and_run_curriculum.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    print_error "Please install Python 3.7+ and try again"
    exit 1
fi

print_status "Python version: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed or not in PATH"
    print_error "Please install pip3 and try again"
    exit 1
fi

print_status "pip version: $(pip3 --version)"

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_success "Dependencies installed successfully"
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip3 install sqlalchemy psycopg2-binary python-dotenv
    print_success "Basic dependencies installed"
fi

# Check if Docker is available and running
if command -v docker &> /dev/null && docker info &> /dev/null; then
    print_status "Docker is available and running"
    
    # Check if PostgreSQL container is running
    if docker ps | grep -q "awade-postgres"; then
        print_success "PostgreSQL container is already running"
    else
        print_status "Starting PostgreSQL container..."
        cd ..
        docker-compose up -d postgres
        cd scripts
        
        # Wait for PostgreSQL to be ready
        print_status "Waiting for PostgreSQL to be ready..."
        sleep 10
        
        # Check if it's healthy
        if docker ps | grep -q "awade-postgres"; then
            print_success "PostgreSQL container started successfully"
        else
            print_error "Failed to start PostgreSQL container"
            exit 1
        fi
    fi
    
    # Set default database URL for Docker
    export DATABASE_URL="postgresql://awade_user:awade_password@localhost:5432/awade"
    print_status "Using Docker database URL: $DATABASE_URL"
    
else
    print_warning "Docker not available or not running"
    print_warning "Please ensure you have a PostgreSQL database running and set DATABASE_URL environment variable"
    
    # Check if DATABASE_URL is set
    if [ -z "$DATABASE_URL" ]; then
        print_error "DATABASE_URL environment variable is not set"
        print_error "Please set it to your PostgreSQL connection string"
        print_error "Example: export DATABASE_URL='postgresql://username:password@localhost:5432/database_name'"
        exit 1
    fi
    
    print_success "Using DATABASE_URL: $DATABASE_URL"
fi

# Check if we can connect to the database
print_status "Testing database connection..."
if python3 -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
    print_success "Database connection test successful"
else
    print_error "Database connection test failed"
    print_error "Please check your database configuration and try again"
    exit 1
fi

# Run the curriculum population script
print_status "Running JSS1 Mathematics curriculum population script..."
if python3 populate_jss1_mathematics.py; then
    print_success "Curriculum population completed successfully!"
    echo ""
    echo "🎉 The JSS1 Mathematics curriculum has been populated in your database!"
    echo ""
    echo "📊 What was created:"
    echo "   - Nigeria country"
    echo "   - NERDC Curriculum"
    echo "   - JSS1 grade level"
    echo "   - Mathematics subject"
    echo "   - 25 topics with learning objectives and content areas"
    echo ""
    echo "🔍 You can now:"
    echo "   - View the data through your API endpoints"
    echo "   - Use pgAdmin at http://localhost:5050 (if using Docker)"
    echo "   - Query the database directly"
    echo ""
else
    print_error "Curriculum population failed"
    exit 1
fi

print_success "Setup and curriculum population complete!"
