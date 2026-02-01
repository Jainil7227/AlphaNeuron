# Deployment Guide - Neuro-Logistics Platform

## Overview

This guide covers deploying:
- **Frontend** → Netlify (free tier)
- **Backend** → Render (free tier, supports Python)

> **Note**: Netlify doesn't support Python backends. We'll use Render for the FastAPI backend.

---

## Part 1: Backend Deployment (Render)

### Step 1: Prepare Backend for Deployment

The backend needs these files (already created):
- `requirements.txt` - Python dependencies
- `Procfile` - Process configuration (create if not exists)

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub repository

### Step 3: Deploy Backend on Render

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `neurologistics-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `DEMO_MODE=true`
   - `SECRET_KEY=your-secret-key-here`
   - `GROK_API_KEY=your-grok-api-key`
5. Click **"Create Web Service"**

Your backend URL will be: `https://neurologistics-api.onrender.com`

---

## Part 2: Frontend Deployment (Netlify)

### Step 1: Update API URL

Update the frontend to use your Render backend URL.

Edit `frontend/.env.production`:
```
VITE_API_URL=https://neurologistics-api.onrender.com
```

### Step 2: Create Netlify Account

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub

### Step 3: Deploy Frontend on Netlify

**Option A: Via Netlify Dashboard**
1. Click **"Add new site"** → **"Import an existing project"**
2. Connect GitHub and select your repo
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Add Environment Variable:
   - `VITE_API_URL=https://neurologistics-api.onrender.com`
5. Click **"Deploy site"**

**Option B: Via Netlify CLI**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend
cd frontend

# Build the project
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

---

## Part 3: Configuration Files Needed

### Backend: `Procfile` (for Render)
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Backend: `render.yaml` (optional, for Blueprint)
```yaml
services:
  - type: web
    name: neurologistics-api
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DEMO_MODE
        value: "true"
      - key: SECRET_KEY
        generateValue: true
```

### Frontend: `netlify.toml`
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://neurologistics-api.onrender.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## Part 4: Post-Deployment Steps

### 1. Update CORS in Backend

Edit `backend/app/main.py` to allow your Netlify domain:
```python
origins = [
    "http://localhost:5173",
    "https://your-site.netlify.app",
    "https://your-custom-domain.com",
]
```

### 2. Test the Deployment

1. Open your Netlify URL
2. Login with demo credentials
3. Test the Cost Calculator
4. Verify AI agent is working

---

## Alternative: All-in-One Platforms

If you want simpler deployment, consider:

### Railway (Recommended)
- Supports both frontend and backend
- Free tier available
- Easy setup

### Vercel + Render
- Vercel for frontend (excellent for React)
- Render for backend

### Fly.io
- Supports Docker containers
- Can run both services

---

## Troubleshooting

### Backend not responding?
- Check Render logs for errors
- Verify environment variables are set
- Ensure DEMO_MODE=true if no database

### Frontend can't reach backend?
- Check VITE_API_URL is correct
- Verify CORS settings include Netlify domain
- Check netlify.toml redirects

### AI not working?
- Verify GROK_API_KEY is set in Render
- Check backend logs for API errors

---

## Quick Reference

| Service | Platform | URL Pattern |
|---------|----------|-------------|
| Frontend | Netlify | `https://your-site.netlify.app` |
| Backend | Render | `https://your-api.onrender.com` |
| API Docs | Render | `https://your-api.onrender.com/docs` |
