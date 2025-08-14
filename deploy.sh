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
    echo "✅ render.yaml found"
else
    echo "❌ render.yaml not found"
fi

if [ -f "vercel.json" ]; then
    echo "✅ vercel.json found"
else
    echo "❌ vercel.json not found"
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

echo "🎯 Next Steps:"
echo "1. Push your code to GitHub:"
echo "   git push origin main"
echo ""
echo "2. Deploy to Vercel:"
echo "   - Go to vercel.com"
echo "   - Import your GitHub repo"
echo "   - Set root directory to 'apps/frontend'"
echo "   - Add VITE_API_URL environment variable"
echo ""
echo "3. Deploy to Render:"
echo "   - Go to render.com"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repo"
echo "   - Use the settings from render.yaml"
echo ""
echo "4. Create PostgreSQL database on Render"
echo "5. Update environment variables"
echo "6. Test your deployment!"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "�� Happy Deploying!"
