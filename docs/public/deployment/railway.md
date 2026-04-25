# Railway Backend Deployment Guide

This guide covers how to deploy the Awade **Backend and Database** to [Railway](https://railway.app), while your Frontend remains on Vercel.

## 1. Setup PostgreSQL Database

1. Log in to your [Railway](https://railway.app) dashboard.
2. Click **+ New Project** -> **Provision PostgreSQL**.
3. Once provisioned, click on the PostgreSQL service.
4. Go to the **Variables** tab and note the `DATABASE_URL`.

## 2. Deploy Backend API

1. Click **+ New** -> **GitHub Repo** -> Select your Awade repository.
2. Go to **Settings**:
   - **Service Name**: `awade-backend`
   - **Root Directory**: `/` (root)
   - **Dockerfile Path**: `Dockerfile.prod`
3. Go to **Variables** and add:
   - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}` (Railway reference)
   - `SECRET_KEY`: (Generate a long random string)
   - `JWT_SECRET_KEY`: (Generate a long random string)
   - `OPENAI_API_KEY`: (Your OpenAI API Key)
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`
   - `ALLOWED_ORIGINS`: (Your Vercel Frontend URL, e.g., `https://awade-frontend.vercel.app`)

## 3. Connect Vercel Frontend

1. Log in to your [Vercel](https://vercel.com) dashboard.
2. Go to your Awade Frontend project -> **Settings** -> **Environment Variables**.
3. Update `VITE_API_URL` to point to your new Railway backend URL (found in Railway under **Settings** -> **Public Networking**).
4. Trigger a new deployment on Vercel to pick up the change.

## 4. Final Verification

1. In Railway, check the backend logs to ensure it connected to the DB and started on `$PORT`.
2. Visit your Vercel site and verify it can fetch data from the Railway API.

## Environment Variable Reference

### Railway Backend
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Flask/FastAPI secret key |
| `JWT_SECRET_KEY` | Key for signing JWT tokens |
| `OPENAI_API_KEY` | OpenAI API Key |
| `ENVIRONMENT` | Should be `production` |
| `ALLOWED_ORIGINS`| MUST include your Vercel URL for CORS |

### Vercel Frontend
| Variable | Description |
|----------|-------------|
| `VITE_API_URL`| Your Railway backend public URL |
| `VITE_GOOGLE_CLIENT_ID`| Google OAuth Client ID |
