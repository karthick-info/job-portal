# Quick Render Deployment Guide

## 🚀 Deploy to Render (100% Free Tier)

### Step 1: Push to GitHub
```bash
cd "c:\Users\DELL\Desktop\job portal\myproject"
git push -u origin main
```

### Step 2: Sign Up on Render
1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account (karthick-info)

### Step 3: Create Web Service
1. Click "New +" button → "Web Service"
2. Click "Connect account" to link GitHub
3. Find and select: `karthick-info/job-portal`
4. Click "Connect"

### Step 4: Configure Your Service
Fill in these settings:

**Name**: `job-portal` (or any name you prefer)

**Region**: `Singapore` (or closest to you)

**Branch**: `main`

**Root Directory**: Leave empty

**Runtime**: `Python 3`

**Build Command**:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command**:
```
gunicorn myproject.wsgi:application
```

**Instance Type**: `Free`

### Step 5: Add Environment Variables
Click "Advanced" → "Add Environment Variable"

Add these one by one:

```
SECRET_KEY = django-insecure-change-this-to-something-random-and-secure
DEBUG = False
ALLOWED_HOSTS = .onrender.com
PYTHON_VERSION = 3.12.7
GEMINI_API_KEY = AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0
```

### Step 6: Deploy!
1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Your site will be live at: `https://job-portal.onrender.com` (or your chosen name)

### ⏱️ Important Notes:
- Free tier sleeps after 15 minutes of inactivity
- First load after sleep takes ~30 seconds
- Plenty for testing and portfolio projects!

### 🎉 After Deployment:
1. Visit your site URL
2. Create admin user via Render shell:
   - Go to your service → "Shell" tab
   - Run: `python manage.py createsuperuser`
3. Access admin at: `https://your-app.onrender.com/admin`

### 📱 Share Your Site:
- Main site: `https://your-app.onrender.com`
- Admin panel: `https://your-app.onrender.com/admin`
- Add to your resume/portfolio!
