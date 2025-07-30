#!/bin/bash

# Script to run Awade Frontend in Docker

set -e

echo "🚀 Starting Awade Frontend in Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose -f docker-compose.dev.yml down
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Build and start the frontend
echo "📦 Building and starting frontend container..."
docker-compose -f docker-compose.dev.yml up --build frontend

echo "✅ Frontend is running at http://localhost:3000"
echo "🔄 Hot reload is enabled - changes will automatically refresh"
echo "⏹️  Press Ctrl+C to stop the frontend" 