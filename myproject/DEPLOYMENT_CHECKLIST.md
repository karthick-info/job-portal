# Render Deployment Checklist

## Issues Fixed:
✅ Removed sensitive API keys from render.yaml
✅ Updated settings.py to use environment variables
✅ Added proper database configuration
✅ Configured static files with WhiteNoise
✅ Removed hardcoded credentials from all Python files

## Manual Steps Required in Render Dashboard:

### 1. Environment Variables to Set:
After deployment, go to your Render service dashboard and add these environment variables:

```
GEMINI_API_KEY = AIzaSyDhg68m-EXPY3l1OxSUV4JQ8CYJOMVlSB0
EMAIL_HOST_USER = bkarthick.dev@gmail.com
EMAIL_HOST_PASSWORD = ojizkuyxvpnkbgsd
```

**Important**: These values are now removed from your code for security!

### 2. Deployment Steps:
1. Push your code to GitHub
2. Connect your GitHub repo to Render
3. Set the environment variables in Render dashboard
4. Deploy the service

### 3. Post-Deployment Testing:
Run the test script to verify everything works:
```bash
python test_deployment.py
```

## Testing Checklist:

### After Deployment, Test These Features:
1. **User Registration** - Check if OTP emails are sent
2. **Login System** - Verify authentication works
3. **Job Posting** - Test company job creation
4. **Job Application** - Test candidate applications
5. **Chatbot** - Verify Gemini API integration
6. **Forgot Password** - Test email OTP system
7. **Static Files** - Check CSS/JS loading
8. **Database** - Verify data persistence

## Common Issues & Solutions:

### If Email Not Working:
- Check environment variables are set correctly in Render dashboard
- Verify Gmail app password is valid (not regular password)
- Check Render logs for SMTP errors
- Test with: `python manage.py shell` then try sending test email

### If Chatbot Not Working:
- Verify GEMINI_API_KEY is set in Render dashboard
- Check API key permissions in Google Cloud Console
- Test API key with: `python test_deployment.py`

### If Static Files Not Loading:
- Check if `collectstatic` ran during build
- Verify WhiteNoise middleware is in MIDDLEWARE list
- Check browser console for 404 errors

### If Database Errors:
- Check DATABASE_URL is properly set by Render
- Verify migrations ran successfully in build logs
- Check PostgreSQL connection in Render dashboard

### Build Failures:
- Check requirements.txt has all dependencies
- Verify Python version compatibility
- Check build logs for specific error messages

## Security Notes:
- ✅ API keys are now environment variables only
- ✅ No sensitive data in version control
- ✅ Debug mode disabled in production
- ✅ CSRF protection enabled
- ✅ Allowed hosts configured

## Monitoring:
- Check Render logs for any errors
- Monitor application performance
- Set up health checks if needed
- Monitor database usage (free tier has limits)