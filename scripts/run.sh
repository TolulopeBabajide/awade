#!/bin/bash

# Awade Script Runner
# This script helps run public scripts safely

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}Awade Script Runner${NC}"
    echo ""
    echo "Usage: $0 <script_name> [arguments...]"
    echo ""
    echo "Available public scripts:"
    echo "  setup              - Initial project setup"
    echo "  start-dev          - Start complete development environment"
    echo "  start-frontend     - Start frontend development server"
    echo "  start-backend      - Start backend services"
    echo "  setup-workflow     - Setup development workflow"
    echo "  frontend-docker    - Run frontend with Docker"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 start-dev"
    echo "  $0 start-frontend"
    echo ""
    echo "Note: Private scripts are not available through this runner for security reasons."
}

# Check if script name is provided
if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

SCRIPT_NAME=$1
shift

# Map script names to actual files
case $SCRIPT_NAME in
    "setup")
        SCRIPT_PATH="public/setup.sh"
        ;;
    "start-dev")
        SCRIPT_PATH="public/start_development.sh"
        ;;
    "start-frontend")
        SCRIPT_PATH="public/start_frontend_local.sh"
        ;;
    "start-backend")
        SCRIPT_PATH="public/start_backend_services.sh"
        ;;
    "setup-workflow")
        SCRIPT_PATH="public/setup_workflow.sh"
        ;;
    "frontend-docker")
        SCRIPT_PATH="public/run_frontend_docker.sh"
        ;;
    *)
        echo -e "${RED}Error: Unknown script '$SCRIPT_NAME'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}Error: Script '$SCRIPT_PATH' not found${NC}"
    exit 1
fi

# Make script executable and run it
chmod +x "$SCRIPT_PATH"
echo -e "${GREEN}Running: $SCRIPT_PATH${NC}"
echo ""

# Execute the script with any additional arguments
exec "$SCRIPT_PATH" "$@" 