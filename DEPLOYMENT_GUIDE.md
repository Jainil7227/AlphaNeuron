# 🚀 Deployment Guide: Neuro-Logistics Platform

This guide will walk you through deploying your **Neuro-Logistics** application.
We will deploy the **Backend** to **Render** and the **Frontend** to **Netlify**.

---

## 🏗️ Part 1: Deploy Backend (Render)

We deploy the backend first because the frontend needs the backend URL.

1. **Push Code to GitHub**: Ensure your latest code is pushed to your GitHub repository.
2. **Go to Render**: Log in to [dashboard.render.com](https://dashboard.render.com/).
3. **New Web Service**: Click **New +** -> **Web Service**.
4. **Connect Repository**: Select your `Neuro-Logistics` repository.
5. **Configure Service**:
   - **Name**: `neurologistics-backend` (or similar)
   - **Region**: Closest to you (e.g., Singapore/Ohio)
   - **Root Directory**: `backend` (Important!)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables**:
   Scroll down to "Environment Variables" and add:
   - `GEMINI_API_KEY` : `your_gemini_api_key`
   - `PYTHON_VERSION` : `3.11.7` (Optional, good for stability)
7. **Deploy**: Click **Create Web Service**.

⏳ **Wait**: Render will build and deploy. Once "Live", copy the **backend URL** (e.g., `https://neurologistics-backend.onrender.com`).

---

## 🌐 Part 2: Deploy Frontend (Netlify)

Now we deploy the React frontend and connect it to your live backend.

1. **Go to Netlify**: Log in to [app.netlify.com](https://app.netlify.com/).
2. **Add New Site**: Click **Add new site** -> **Import from Git**.
3. **Connect Repository**: Choose GitHub and select your repository.
4. **Configure Build Settings**:
   - **Base directory**: Leave empty / root (Because we have a `netlify.toml` file in the root)
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
5. **Environment Variables**:
   Click **Advanced** (or go to Site Settings later) and add:
   - Key: `VITE_API_URL`
   - Value: `https://neurologistics.onrender.com` (Your live backend URL)
6. **Deploy**: Click **Deploy site**.

---

## ✅ Verification

1. Open your Netlify URL (e.g., `https://neuro-logistics.netlify.app`).
2. Open the **Browser Console** (F12).
3. Check the **Network Tab** as you use the app.
   - You should see requests going to `https://your-backend-url.onrender.com/api/...` instead of `localhost`.
4. Test the **AI Copilot** to ensure the backend connection works.

---

## 🛠️ Configuring Environment Variables After Deployment

If you didn't add the URL during creation (or need to change it):

1. Go to your **Netlify Dashboard** and select your site.
2. Click **Site configuration** in the left sidebar.
3. Select **Environment variables**.
4. Click **Add a variable** -> **Add single variable**.
   - Key: `VITE_API_URL`
   - Value: `https://neurologistics.onrender.com`
5. **IMPORTANT**: Go to the **Deploys** tab and click **Trigger deploy** -> **Clear cache and deploy site**. 
   *Environment variables are only baked in during the build process, so a new build is required.*
