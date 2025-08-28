#!/bin/bash

# Test Environment Deployment Script for Awade
echo "🚀 Starting Awade Test Environment Deployment..."

# Set environment variables
export NODE_ENV=production
export VITE_API_BASE_URL=https://awade-backend-test.onrender.com
export VITE_BACKEND_URL=https://awade-backend-test.onrender.com
export VITE_ENVIRONMENT=testing

echo "🔧 Environment Variables Set:"
echo "  NODE_ENV: $NODE_ENV"
echo "  VITE_API_BASE_URL: $VITE_API_BASE_URL"
echo "  VITE_BACKEND_URL: $VITE_BACKEND_URL"
echo "  VITE_ENVIRONMENT: $VITE_ENVIRONMENT"

# Navigate to frontend directory
cd apps/frontend

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building for test environment..."
npm run build:test

echo "✅ Test build completed!"
echo "📁 Build output: apps/frontend/dist-test/"

# Check if build was successful
if [ -d "dist-test" ]; then
    echo "🎉 Test deployment build successful!"
    echo "📋 Next steps:"
    echo "  1. Deploy the dist-test folder to your test hosting platform"
    echo "  2. Ensure the backend at $VITE_BACKEND_URL is running"
    echo "  3. Test the API endpoints"
else
    echo "❌ Test build failed!"
    exit 1
fi
