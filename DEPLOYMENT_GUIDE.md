# 🚀 Awade Deployment Guide: Vercel + Render.com

## 🎯 **Architecture Overview**
- **Frontend**: React app deployed on Vercel (FREE)
- **Backend**: FastAPI deployed on Render.com (FREE)
- **Database**: PostgreSQL on Render.com (FREE)

## 📋 **Prerequisites**
- GitHub account with your Awade repository
- OpenAI API key
- Google OAuth client ID (optional)

---

## 🎨 **Step 1: Deploy Frontend to Vercel**

### **1.1 Connect to Vercel**
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click "New Project"
3. Import your Awade repository

### **1.2 Configure Build Settings**
- **Framework Preset**: Vite
- **Root Directory**: `apps/frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### **1.3 Environment Variables**
Add these in Vercel dashboard:
```bash
VITE_API_URL=https://awade-backend.onrender.com
```

### **1.4 Deploy**
- Click "Deploy"
- Wait for build to complete
- Note your Vercel URL (e.g., `https://awade.vercel.app`)

---

## 🐍 **Step 2: Deploy Backend to Render.com**

### **2.1 Connect to Render**
1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your Awade repository

### **2.2 Configure Backend Service**
- **Name**: `awade-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty (root)
- **Build Command**: `pip install -r apps/backend/requirements.txt`
- **Start Command**: `uvicorn apps.backend.main:app --host 0.0.0.0 --port $PORT`

### **2.3 Environment Variables**
Add these in Render dashboard:
```bash
PYTHON_VERSION=3.11.0
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
OPENAI_API_KEY=your-openai-api-key
DEBUG=false
ENVIRONMENT=production
JWT_EXPIRES_MINUTES=60
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### **2.4 Deploy Backend**
- Click "Create Web Service"
- Wait for build and deployment
- Note your Render URL (e.g., `https://awade-backend.onrender.com`)

---

## 🗄️ **Step 3: Setup Database on Render**

### **3.1 Create PostgreSQL Database**
1. In Render dashboard, click "New +" → "PostgreSQL"
2. **Name**: `awade-db`
3. **Database**: `awade`
4. **User**: `awade_user`
5. **Region**: Same as backend
6. Click "Create Database"

### **3.2 Connect Database to Backend**
1. Go back to your backend service
2. Add environment variable:
   ```bash
   DATABASE_URL=postgresql://awade_user:password@host:5432/awade
   ```
   (Copy the connection string from your database dashboard)

### **3.3 Initialize Database**
1. Go to your backend service logs
2. The service should automatically create tables
3. Or manually trigger by visiting: `https://your-backend.onrender.com/health`

---

## 🔄 **Step 4: Update Frontend API URL**

### **4.1 Update Vercel Environment**
1. Go to your Vercel project dashboard
2. Settings → Environment Variables
3. Update `VITE_API_URL` with your Render backend URL

### **4.2 Redeploy Frontend**
1. Go to Deployments tab
2. Click "Redeploy" on latest deployment
3. Or push a new commit to trigger auto-deploy

---

## ✅ **Step 5: Test Your Deployment**

### **5.1 Health Check**
```bash
# Test backend
curl https://your-backend.onrender.com/health

# Test frontend
curl https://your-app.vercel.app
```

### **5.2 Test API Endpoints**
```bash
# Test API docs
curl https://your-backend.onrender.com/docs

# Test authentication
curl https://your-backend.onrender.com/api/auth/login
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Backend Won't Start**
- Check Render logs for errors
- Verify environment variables
- Ensure requirements.txt is correct

#### **Database Connection Failed**
- Verify DATABASE_URL format
- Check database is running
- Ensure database user permissions

#### **Frontend Can't Connect to Backend**
- Verify VITE_API_URL in Vercel
- Check CORS settings in backend
- Ensure backend is running

#### **Build Failures**
- Check package.json scripts
- Verify Node.js version
- Check for missing dependencies

### **Useful Commands**
```bash
# Check backend logs
# Go to Render dashboard → Backend service → Logs

# Check frontend logs
# Go to Vercel dashboard → Project → Deployments → View Function Logs

# Test database connection
curl https://your-backend.onrender.com/health
```

---

## 🚀 **Auto-Deploy Setup**

### **GitHub Actions (Optional)**
1. Create `.github/workflows/deploy.yml`
2. Configure automatic deployment on push to main
3. Update environment variables automatically

### **Manual Deployment**
```bash
# Push changes to trigger auto-deploy
git add .
git commit -m "update for production"
git push origin main
```

---

## 📊 **Monitoring Your Deployment**

### **Vercel Dashboard**
- Build status
- Performance metrics
- Function logs
- Analytics

### **Render Dashboard**
- Service health
- Resource usage
- Database metrics
- Logs

### **Health Checks**
```bash
# Backend health
https://your-backend.onrender.com/health

# Frontend status
https://your-app.vercel.app
```

---

## 🎉 **You're Live!**

Your Awade application is now:
- ✅ **Frontend**: Accessible at `https://your-app.vercel.app`
- ✅ **Backend**: Running at `https://your-backend.onrender.com`
- ✅ **Database**: PostgreSQL running on Render
- ✅ **100% FREE** and **remotely accessible**

### **Next Steps**
1. Test all functionality
2. Set up custom domain (optional)
3. Configure monitoring
4. Set up backups
5. Share with your team!

---

## 📞 **Need Help?**

- **Vercel Issues**: Check [Vercel Documentation](https://vercel.com/docs)
- **Render Issues**: Check [Render Documentation](https://render.com/docs)
- **Awade Issues**: Check our [Development Guide](../docs/public/development/README.md)

**Happy Deploying! 🚀**
