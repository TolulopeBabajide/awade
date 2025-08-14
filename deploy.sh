#!/bin/bash

# 🚀 Awade Quick Deployment Script
# This script helps you prepare for deployment to Vercel + Render

echo "🚀 Awade Deployment Setup"
echo "=========================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git remote add origin <your-github-repo-url>"
    echo "   git push -u origin main"
    exit 1
fi

# Check if files exist
echo "📋 Checking deployment files..."
if [ -f "render.yaml" ]; then
    echo "✅ render.yaml found (Production)"
else
    echo "❌ render.yaml not found"
fi

if [ -f "render.test.yaml" ]; then
    echo "✅ render.test.yaml found (Test Environment)"
else
    echo "❌ render.test.yaml not found"
fi

if [ -f "vercel.json" ]; then
    echo "✅ vercel.json found (Production)"
else
    echo "❌ vercel.json not found"
fi

if [ -f "vercel.test.json" ]; then
    echo "✅ vercel.test.json found (Test Environment)"
else
    echo "❌ vercel.test.json not found"
fi

if [ -f "Dockerfile.prod" ]; then
    echo "✅ Dockerfile.prod found"
else
    echo "❌ Dockerfile.prod found"
fi

if [ -f "env.production.template" ]; then
    echo "✅ env.production.template found"
else
    echo "❌ env.production.template found"
fi

if [ -f "env.test.template" ]; then
    echo "✅ env.test.template found"
else
    echo "❌ env.test.template not found"
fi

echo ""

# Check git status
echo "📊 Git Status:"
git status --porcelain

echo ""

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Consider committing them:"
    echo "   git add ."
    echo "   git commit -m 'Prepare for deployment'"
    echo "   git push origin main"
else
    echo "✅ All changes are committed"
fi

echo ""

echo "🎯 Deployment Options:"
echo ""
echo "🧪 TEST ENVIRONMENT (Recommended for first deployment):"
echo "1. Deploy to Vercel (Test):"
echo "   - Go to vercel.com"
echo "   - Import your GitHub repo"
echo "   - Set root directory to 'apps/frontend'"
echo "   - Use build command: npm run build:test"
echo "   - Add VITE_API_URL environment variable"
echo ""
echo "2. Deploy to Render (Test):"
echo "   - Go to render.com"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repo"
echo "   - Use render.test.yaml configuration"
echo ""
echo "3. Create test PostgreSQL database on Render"
echo "4. Update environment variables"
echo "5. Test your deployment!"
echo ""
echo "🚀 PRODUCTION ENVIRONMENT:"
echo "1. Deploy to Vercel (Production):"
echo "   - Go to vercel.com"
echo "   - Import your GitHub repo"
echo "   - Set root directory to 'apps/frontend'"
echo "   - Use build command: npm run build"
echo "   - Add VITE_API_URL environment variable"
echo ""
echo "2. Deploy to Render (Production):"
echo "   - Go to render.com"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repo"
echo "   - Use render.yaml configuration"
echo ""
echo "3. Create production PostgreSQL database on Render"
echo "4. Update environment variables"
echo "5. Deploy to production!"
echo ""
echo "📖 See TEST_DEPLOYMENT_GUIDE.md for test environment setup"
echo "📖 See DEPLOYMENT_GUIDE.md for production setup"
echo ""
echo "🧪 Happy Testing and Deploying!"
