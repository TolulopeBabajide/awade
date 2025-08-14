# 🧪 Awade Test Environment Deployment Guide

## 🎯 **Test Environment Overview**
- **Frontend**: React app deployed on Vercel (TEST)
- **Backend**: FastAPI deployed on Render.com (TEST)
- **Database**: PostgreSQL on Render.com (TEST)
- **Purpose**: Safe testing before production deployment

---

## 🚀 **Step 1: Deploy Frontend to Vercel (Test)**

### **1.1 Create Test Project**
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click "New Project"
3. Import your Awade repository
4. **Project Name**: `awade-test` (or your preferred test name)

### **1.2 Configure Test Build Settings**
- **Framework Preset**: Vite
- **Root Directory**: `apps/frontend`
- **Build Command**: `npm run build:test`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### **1.3 Test Environment Variables**
Add these in Vercel dashboard:
```bash
VITE_API_URL=https://awade-backend-test.onrender.com
VITE_ENVIRONMENT=test
```

### **1.4 Deploy Test Frontend**
- Click "Deploy"
- Wait for build to complete
- Note your test Vercel URL (e.g., `https://awade-test.vercel.app`)

---

## 🐍 **Step 2: Deploy Backend to Render.com (Test)**

### **2.1 Create Test Backend Service**
1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your Awade repository

### **2.2 Configure Test Backend Service**
- **Name**: `awade-backend-test`
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `develop` (or your test branch)
- **Root Directory**: Leave empty (root)
- **Build Command**: `pip install -r apps/backend/requirements.txt`
- **Start Command**: `uvicorn apps.backend.main:app --host 0.0.0.0 --port $PORT`

### **2.3 Test Environment Variables**
Add these in Render dashboard:
```bash
PYTHON_VERSION=3.11.0
SECRET_KEY=your-test-secret-key-here
JWT_SECRET_KEY=your-test-jwt-secret-key-here
OPENAI_API_KEY=your-openai-api-key
DEBUG=true
ENVIRONMENT=testing
JWT_EXPIRES_MINUTES=60
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
ALLOWED_ORIGINS=https://awade-test.vercel.app,http://localhost:3000
```

### **2.4 Deploy Test Backend**
- Click "Create Web Service"
- Wait for build and deployment
- Note your test Render URL (e.g., `https://awade-backend-test.onrender.com`)

---

## 🗄️ **Step 3: Setup Test Database on Render**

### **3.1 Create Test PostgreSQL Database**
1. In Render dashboard, click "New +" → "PostgreSQL"
2. **Name**: `awade-test-db`
3. **Database**: `awade_test`
4. **User**: `awade_test_user`
5. **Region**: Same as backend
6. Click "Create Database"

### **3.2 Connect Test Database to Backend**
1. Go back to your test backend service
2. Add environment variable:
   ```bash
   DATABASE_URL=postgresql://awade_test_user:password@host:5432/awade_test
   ```
   (Copy the connection string from your test database dashboard)

---

## 🔄 **Step 4: Update Test Frontend API URL**

### **4.1 Update Vercel Test Environment**
1. Go to your Vercel test project dashboard
2. Settings → Environment Variables
3. Update `VITE_API_URL` with your test Render backend URL

### **4.2 Redeploy Test Frontend**
1. Go to Deployments tab
2. Click "Redeploy" on latest deployment
3. Or push a new commit to trigger auto-deploy

---

## ✅ **Step 5: Test Your Test Environment**

### **5.1 Health Check**
```bash
# Test test backend
curl https://awade-backend-test.onrender.com/health

# Test test frontend
curl https://awade-test.vercel.app
```

### **5.2 Test API Endpoints**
```bash
# Test API docs
curl https://awade-backend-test.onrender.com/docs

# Test authentication
curl https://awade-backend-test.onrender.com/api/auth/login
```

---

## 🔧 **Test Environment Benefits**

### **✅ Safe Testing**
- **Separate Database** - No risk to production data
- **Debug Mode Enabled** - Full error details for testing
- **Test Users** - Safe to create test accounts
- **API Testing** - Test all endpoints without production impact

### **✅ Development Workflow**
- **Feature Testing** - Test new features safely
- **Integration Testing** - Test frontend-backend integration
- **Performance Testing** - Test with real deployment
- **User Acceptance Testing** - Share with stakeholders safely

---

## 🚀 **Deploy to Test Environment**

### **Option 1: Use Test Configuration Files**
```bash
# Deploy backend with test config
render deploy --config render.test.yaml

# Deploy frontend with test config
vercel --prod --config vercel.test.json
```

### **Option 2: Manual Deployment**
Follow the step-by-step guide above for manual deployment.

---

## 🎯 **Test Environment URLs**

After deployment, you'll have:
- **Frontend**: `https://awade-test.vercel.app`
- **Backend**: `https://awade-backend-test.onrender.com`
- **API Docs**: `https://awade-backend-test.onrender.com/docs`

---

## 🔒 **Test Environment Security**

### **✅ Safe for Testing**
- **Debug Mode**: Full error details for developers
- **Test Database**: Isolated from production
- **Test Users**: Safe to create and delete
- **Test API Keys**: Can use test OpenAI keys

### **⚠️ Not for Production**
- **Debug Enabled**: Exposes internal details
- **Test Credentials**: Not secure for real users
- **Test Database**: May contain test data

---

## 🎉 **You're Ready for Test Deployment!**

Your test environment is now configured for:
- ✅ **Safe Testing** - No production impact
- ✅ **Full Debugging** - Complete error information
- ✅ **Integration Testing** - Real deployment testing
- ✅ **User Testing** - Safe stakeholder testing

**Happy Testing! 🧪**
