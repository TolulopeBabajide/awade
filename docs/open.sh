#!/bin/bash

# Awade Documentation Opener
# This script helps open public documentation safely

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}Awade Documentation Opener${NC}"
    echo ""
    echo "Usage: $0 <doc_type> [filename]"
    echo ""
    echo "Available documentation types:"
    echo "  user-guide      - User guides and tutorials"
    echo "  api            - API documentation"
    echo "  development    - Development guides"
    echo "  deployment     - Deployment guides"
    echo "  external       - External documentation"
    echo ""
    echo "Examples:"
    echo "  $0 user-guide"
    echo "  $0 api README.md"
    echo "  $0 development contributing.md"
    echo ""
    echo "Note: Private documentation is not accessible through this opener for security reasons."
}

# Check if doc type is provided
if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

DOC_TYPE=$1
FILENAME=$2

# Map doc types to directories
case $DOC_TYPE in
    "user-guide")
        DOC_PATH="public/user-guide"
        ;;
    "api")
        DOC_PATH="public/api"
        ;;
    "development")
        DOC_PATH="public/development"
        ;;
    "deployment")
        DOC_PATH="public/deployment"
        ;;
    "external")
        DOC_PATH="public/external"
        ;;
    *)
        echo -e "${RED}Error: Unknown documentation type '$DOC_TYPE'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac

# Check if directory exists
if [ ! -d "$DOC_PATH" ]; then
    echo -e "${RED}Error: Documentation directory '$DOC_PATH' not found${NC}"
    exit 1
fi

# If filename is provided, open specific file
if [ -n "$FILENAME" ]; then
    FILE_PATH="$DOC_PATH/$FILENAME"
    if [ ! -f "$FILE_PATH" ]; then
        echo -e "${RED}Error: File '$FILE_PATH' not found${NC}"
        echo ""
        echo "Available files in $DOC_PATH:"
        ls -la "$DOC_PATH" | grep "\.md$" | awk '{print "  - " $9}'
        exit 1
    fi
    
    echo -e "${GREEN}Opening: $FILE_PATH${NC}"
    
    # Try to open with default markdown viewer
    if command -v code &> /dev/null; then
        code "$FILE_PATH"
    elif command -v open &> /dev/null; then
        open "$FILE_PATH"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$FILE_PATH"
    else
        echo -e "${YELLOW}No suitable viewer found. Opening in text editor...${NC}"
        if command -v nano &> /dev/null; then
            nano "$FILE_PATH"
        elif command -v vim &> /dev/null; then
            vim "$FILE_PATH"
        else
            cat "$FILE_PATH"
        fi
    fi
else
    # List available files in the directory
    echo -e "${GREEN}Available documentation in $DOC_PATH:${NC}"
    echo ""
    
    if [ -f "$DOC_PATH/README.md" ]; then
        echo -e "${BLUE}📖 README.md${NC} - Overview and getting started"
    fi
    
    for file in "$DOC_PATH"/*.md; do
        if [ -f "$file" ] && [ "$(basename "$file")" != "README.md" ]; then
            filename=$(basename "$file")
            echo -e "${BLUE}📄 $filename${NC}"
        fi
    done
    
    echo ""
    echo "To open a specific file, use: $0 $DOC_TYPE <filename>"
    echo "Example: $0 $DOC_TYPE README.md"
fi 