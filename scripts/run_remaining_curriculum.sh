#!/bin/bash

# Run the remaining JSS1 Mathematics curriculum population script

echo "🚀 Running JSS1 Mathematics Curriculum - Remaining Topics Population"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "populate_remaining_jss1_mathematics.py" ]; then
    echo "❌ Error: This script must be run from the scripts directory"
    echo "Please run: cd scripts && ./run_remaining_curriculum.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: DATABASE_URL environment variable is not set"
    echo "   If using Docker, the script will use the default Docker database URL"
    echo "   If using a local database, please set DATABASE_URL"
fi

# Run the script
echo "📝 Running curriculum population script..."
python3 populate_remaining_jss1_mathematics.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! The remaining JSS1 Mathematics curriculum topics have been populated."
    echo ""
    echo "📊 What was created:"
    echo "   - 24 new topics (excluding Fractions which already existed)"
    echo "   - Learning objectives for each topic"
    echo "   - Content areas for each topic"
    echo ""
    echo "🔍 You can now view the complete curriculum through your API endpoints or database."
else
    echo "❌ Error: Curriculum population failed"
    exit 1
fi
