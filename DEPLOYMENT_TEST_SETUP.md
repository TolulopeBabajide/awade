# Awade Test Deployment Setup Guide

## 🎯 Overview
This guide covers the setup for the test environment deployment of Awade, with the backend on Render and frontend on Vercel.

## 🔧 Current Configuration Status

### ✅ Backend (Render)
- **URL**: https://awade-backend-test.onrender.com
- **Status**: ✅ Running and accessible
- **Health Check**: ✅ Working
- **CORS**: ✅ Configured for test frontend

### 🔄 Frontend (Vercel)
- **URL**: https://awade-test.vercel.app
- **Environment**: Set to "test"
- **Status**: Needs deployment with updated configuration

## 🚀 Deployment Steps

### 1. Environment Variables in Vercel
Ensure these environment variables are set in your Vercel project:

```bash
VITE_ENVIRONMENT=test
VITE_API_BASE_URL=https://awade-backend-test.onrender.com
VITE_BACKEND_URL=https://awade-backend-test.onrender.com
NODE_ENV=production
```

### 2. Build and Deploy
Run the following command to build for the test environment:

```bash
cd apps/frontend
npm run build:vercel
```

### 3. Deploy to Vercel
- Push the updated code to your repository
- Vercel will automatically build and deploy
- Or manually deploy the `dist/` folder

## 🧪 Verification Steps

### Backend Verification
```bash
# Health check
curl https://awade-backend-test.onrender.com/health

# Root endpoint
curl https://awade-backend-test.onrender.com/
```

### Frontend Verification
1. Open https://awade-test.vercel.app
2. Check browser console for environment logs
3. Verify API calls go to test backend
4. Test login/signup functionality

## 🔍 Troubleshooting

### Common Issues

#### 1. CORS Errors
- Ensure backend has correct `ALLOWED_ORIGINS` in Render
- Check that `https://awade-test.vercel.app` is included

#### 2. Environment Variables Not Loading
- Verify Vercel environment variables are set correctly
- Check that `VITE_ENVIRONMENT=test` is set
- Rebuild and redeploy after environment variable changes

#### 3. API Calls Going to Wrong Backend
- Check `VITE_API_BASE_URL` environment variable
- Verify the build output includes correct backend URL
- Clear browser cache and reload

### Debug Commands
```bash
# Test backend connectivity
curl -I https://awade-backend-test.onrender.com/health

# Check environment variables
node verify-deployment.js

# Build for test environment
npm run build:test
```

## 📋 Configuration Files

### Key Files Updated
- `apps/frontend/vite.config.ts` - Environment-aware configuration
- `apps/frontend/src/services/api.ts` - API service with environment detection
- `apps/frontend/vercel.json` - Vercel deployment configuration
- `apps/frontend/package.json` - Build scripts for different environments

### Environment Detection
The application now automatically detects the environment and:
- Sets the correct backend URL
- Configures CORS appropriately
- Logs environment information for debugging
- Provides fallback configurations

## ✅ Success Criteria
- [ ] Frontend deploys successfully to Vercel
- [ ] Environment variables load correctly
- [ ] API calls go to test backend
- [ ] No CORS errors in browser
- [ ] Login/signup functionality works
- [ ] Environment logs appear in browser console

## 🆘 Support
If you encounter issues:
1. Check the browser console for error messages
2. Verify environment variables in Vercel
3. Test backend connectivity
4. Check the deployment logs in Vercel
