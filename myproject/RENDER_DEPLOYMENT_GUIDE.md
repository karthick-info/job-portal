# 🚀 Render Deployment Guide

## 📋 **Step-by-Step Deployment Process**

### 1. **Automatic Deployment (Recommended)**

Since your code is connected to GitHub, Render should automatically deploy when you push changes.

#### Check Deployment Status:
1. Go to your Render dashboard: https://dashboard.render.com
2. Find your job portal service
3. Check if a new deployment is already in progress
4. Look for the latest commit hash: `0f611eb`

### 2. **Manual Deployment (If Needed)**

If automatic deployment didn't trigger:

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your job portal service

2. **Trigger Manual Deploy**
   - Click "Manual Deploy" button
   - Select "Deploy latest commit"
   - Confirm deployment

### 3. **Set Environment Variables** ⚠️ **CRITICAL**

Before the deployment works properly, you MUST set these environment variables:

#### In Render Dashboard:
1. Go to your service → **Environment** tab
2. Add these variables:

```
GEMINI_API_KEY = AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0
EMAIL_HOST_USER = bkarthick.dev@gmail.com  
EMAIL_HOST_PASSWORD = ojizkuyxvpnkbgsd
```

#### How to Add Variables:
1. Click **"Add Environment Variable"**
2. Enter **Key** and **Value**
3. Click **"Save Changes"**
4. Repeat for all 3 variables

### 4. **Monitor Deployment**

#### Check Build Logs:
1. Go to **"Logs"** tab in your service
2. Watch for these success indicators:
   ```
   ✅ Installing dependencies...
   ✅ Collecting static files...
   ✅ Running migrations...
   ✅ Starting gunicorn...
   ✅ Your service is live at https://your-app.onrender.com
   ```

#### Common Build Steps:
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput  
python manage.py migrate
gunicorn myproject.wsgi:application
```

### 5. **Test Deployment**

Once deployed, test these features:

#### ✅ **Registration Test:**
1. Go to your live site: `https://your-app.onrender.com/register/`
2. Fill out registration form
3. Submit and check for OTP email
4. Verify no Internal Server Error

#### ✅ **Email Test:**
1. Register with a real email address
2. Check inbox AND spam folder
3. Verify OTP email arrives
4. Complete verification process

#### ✅ **Other Features:**
- Login system
- Job posting (for companies)
- Job applications (for candidates)
- Chatbot functionality

### 6. **Troubleshooting**

#### If Deployment Fails:

**Check Build Logs for:**
- Missing dependencies
- Database migration errors
- Static file collection issues
- Environment variable problems

**Common Issues & Solutions:**

1. **Build Timeout:**
   - Render free tier has build time limits
   - Check if build is taking too long

2. **Environment Variables Missing:**
   - Verify all 3 variables are set correctly
   - Check for typos in variable names

3. **Database Issues:**
   - Render automatically creates PostgreSQL database
   - Migrations should run automatically

4. **Static Files:**
   - WhiteNoise handles static files
   - Should collect automatically during build

### 7. **Deployment Checklist**

- [ ] Code pushed to GitHub (✅ Done)
- [ ] Render service connected to GitHub repo
- [ ] Environment variables set in Render dashboard
- [ ] Deployment triggered (automatic or manual)
- [ ] Build logs show success
- [ ] Site is accessible at live URL
- [ ] Registration works without errors
- [ ] Email OTP delivery functional
- [ ] All features tested

### 8. **Expected Timeline**

- **Build Time:** 3-5 minutes
- **Total Deployment:** 5-10 minutes
- **First Deploy:** May take longer (10-15 minutes)

### 9. **Live URL**

Your app will be available at:
```
https://your-service-name.onrender.com
```

### 🆘 **Need Help?**

If you encounter issues:

1. **Check Render Logs:** Look for specific error messages
2. **Verify Environment Variables:** Ensure all 3 are set correctly
3. **Check GitHub Connection:** Confirm Render is connected to your repo
4. **Review Build Process:** Watch the build logs for failures

---

## 🎯 **Quick Action Items:**

1. **Go to Render Dashboard** → Find your service
2. **Set Environment Variables** (3 variables listed above)
3. **Trigger Deployment** (if not automatic)
4. **Monitor Build Logs**
5. **Test Live Site**

Your updated code with all the fixes is ready to deploy! 🚀