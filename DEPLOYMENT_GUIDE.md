# Job Portal - Deployment Guide

## 🚀 Quick Deploy to Render/Railway

### Prerequisites
- GitHub account
- Code pushed to https://github.com/karthick-info/job-portal.git

### Option 1: Deploy to Render (Recommended - Free Tier Available)

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `https://github.com/karthick-info/job-portal.git`
   - Configure:
     - **Name**: job-portal
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command**: `gunicorn myproject.wsgi:application`
     - **Instance Type**: Free

3. **Environment Variables** (Add these in Render Dashboard):
   ```
   SECRET_KEY=your-super-secret-key-here-change-this
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   GEMINI_API_KEY=AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your site will be live at: `https://your-app-name.onrender.com`

### Option 2: Deploy to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select: `karthick-info/job-portal`

3. **Environment Variables**:
   ```
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
   GEMINI_API_KEY=AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0
   ```

4. **Deploy**
   - Railway will auto-detect Django and deploy
   - Your site will be live at the provided Railway domain

### Option 3: Deploy to PythonAnywhere

1. **Create Account**: https://www.pythonanywhere.com
2. **Upload Code**: Use Git or upload ZIP
3. **Create Web App**: Django → Python 3.12
4. **Configure**: Point to your wsgi  file
5. **Static Files**: Set path to `/staticfiles`

## 📋 Post-Deployment Steps

1. **Create Superuser** (via Render/Railway web terminal):
   ```bash
   python manage.py createsuperuser
   ```

2. **Add Sample Jobs**:
   ```bash
   python manage.py shell
   # Then run the job creation script
   ```

3. **Test Your Site**:
   - Home page works
   - Job listings display properly
   - Apply for jobs functionality
   - Admin panel accessible at `/admin`

## 🔧 Important Files Created

- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Tells hosting how to run app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `.gitignore` - Excludes sensitive files

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS settings
- [ ] Set up database backups

## 🌐 Your Repository

Push to: https://github.com/karthick-info/job-portal.git

##  Troubleshooting

**Static files not loading?**
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings

**Database errors?**
- Ensure migrations are run: `python manage.py migrate`
- Check DATABASE_URL environment variable

**500 errors?**
- Check application logs in hosting dashboard
- Verify all environment variables are set

## 📞 Support

- Render Docs: https://render.com/docs/deploy-django
- Railway Docs: https://docs.railway.app/deploy/django
- Django Deployment: https://docs.djangoproject.com/en/5.1/howto/deployment/

---

**Live URL**: Will be available after deployment
**Admin Panel**: `your-domain.com/admin`
**API Endpoint**: `your-domain.com/api/`
