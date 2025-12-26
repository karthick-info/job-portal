from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import UserMaster, Candidate, Company, Job, JobApplication, SavedJob, JobAlert
from random import randint
from datetime import datetime, date
import json
import logging
from django.http import JsonResponse
import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

# Set up logging
logger = logging.getLogger(__name__)


# ============================================
# EMAIL TEMPLATES & HELPER FUNCTIONS
# ============================================

def get_email_base_style():
    """Common CSS styles for all email templates"""
    return '''
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 0 auto; background: #ffffff; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 28px; }
        .header p { margin: 10px 0 0; opacity: 0.9; }
        .content { padding: 30px; background: #ffffff; }
        .content h2 { color: #2c3e50; margin-top: 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #eee; }
        .btn { display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 15px 0; }
        .btn:hover { opacity: 0.9; }
        .info-box { background: #e8f4fd; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .warning-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .otp-box { background: #f8f9fa; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 10px; }
        .otp-code { font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 10px; margin: 10px 0; }
        .job-card { background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 15px 0; border: 1px solid #eee; }
        .job-title { color: #2c3e50; font-size: 18px; font-weight: bold; margin: 0 0 5px; }
        .job-company { color: #667eea; font-weight: 500; }
        .job-meta { color: #888; font-size: 14px; margin-top: 10px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; }
        .badge-primary { background: #667eea; color: white; }
        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: #333; }
        .divider { border: 0; border-top: 1px solid #eee; margin: 20px 0; }
        .social-links a { display: inline-block; margin: 0 10px; color: #667eea; text-decoration: none; }
    '''


def send_email(to_email, subject, html_content, plain_content):
    """Generic email sending function"""
    try:
        send_mail(
            subject=subject,
            message=plain_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        print(f"\n{'='*50}\n📧 EMAIL (Console Fallback)\nTo: {to_email}\nSubject: {subject}\n{'='*50}\n")
        return False


def send_otp_email(email, otp, name="User"):
    """Send OTP verification email"""
    subject = '🔐 Your OTP Verification Code - JobBoard'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 JobBoard</h1>
                <p>Email Verification</p>
            </div>
            <div class="content">
                <h2>Hello {name}! 👋</h2>
                <p>Thank you for registering with JobBoard. Please use the following OTP to verify your email address:</p>
                
                <div class="otp-box">
                    <p style="margin: 0; color: #666;">Your Verification Code</p>
                    <p class="otp-code">{otp}</p>
                </div>
                
                <div class="warning-box">
                    ⚠️ <strong>Important:</strong> This OTP is valid for 10 minutes. Do not share this code with anyone.
                </div>
                
                <p>If you didn't request this verification, please ignore this email.</p>
            </div>
            <div class="footer">
                <p><strong>JobBoard</strong> - Find Your Dream Job</p>
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hello {name}!\n\nYour OTP Verification Code: {otp}\n\nThis OTP is valid for 10 minutes.\n\nJobBoard Team'''
    
    return send_email(email, subject, html_message, plain_message)


def send_welcome_email(email, name, role):
    """Send welcome email after successful registration"""
    subject = '🎉 Welcome to JobBoard!'
    
    role_message = "start applying for your dream jobs" if role == "candidate" else "post jobs and find talented candidates"
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to JobBoard!</h1>
                <p>Your account is ready</p>
            </div>
            <div class="content">
                <h2>Hi {name}! 👋</h2>
                <p>Congratulations! Your account has been successfully verified. You can now {role_message}.</p>
                
                <div class="success-box">
                    ✅ <strong>Account Verified!</strong> You're all set to explore JobBoard.
                </div>
                
                <p style="text-align: center;">
                    <a href="#" class="btn">🚀 Get Started</a>
                </p>
                
                <hr class="divider">
                
                <h3>What's Next?</h3>
                <ul>
                    {"<li>Complete your profile</li><li>Upload your resume</li><li>Browse and apply for jobs</li>" if role == "candidate" else "<li>Complete your company profile</li><li>Post your first job</li><li>Review applications</li>"}
                </ul>
            </div>
            <div class="footer">
                <p>Need help? Contact us at support@jobboard.com</p>
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hi {name}!\n\nWelcome to JobBoard! Your account is now verified.\n\nYou can now {role_message}.\n\nJobBoard Team'''
    
    return send_email(email, subject, html_message, plain_message)


def send_application_received_email(candidate_email, candidate_name, job_title, company_name):
    """Send confirmation email to candidate after applying"""
    subject = f'✅ Application Submitted - {job_title}'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 Application Submitted</h1>
                <p>We've received your application</p>
            </div>
            <div class="content">
                <h2>Hi {candidate_name}! 👋</h2>
                <p>Great news! Your application has been successfully submitted.</p>
                
                <div class="job-card">
                    <p class="job-title">{job_title}</p>
                    <p class="job-company">🏢 {company_name}</p>
                    <p class="job-meta">
                        <span class="badge badge-success">Application Submitted</span>
                    </p>
                </div>
                
                <div class="info-box">
                    📋 <strong>What happens next?</strong><br>
                    The employer will review your application and contact you if your profile matches their requirements.
                </div>
                
                <p>You can track your application status in your dashboard.</p>
                
                <p style="text-align: center;">
                    <a href="#" class="btn">View My Applications</a>
                </p>
            </div>
            <div class="footer">
                <p>Good luck with your application! 🍀</p>
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hi {candidate_name}!\n\nYour application for "{job_title}" at {company_name} has been submitted.\n\nGood luck!\nJobBoard Team'''
    
    return send_email(candidate_email, subject, html_message, plain_message)


def send_new_application_notification(employer_email, employer_name, candidate_name, job_title, application_id):
    """Notify employer about new job application"""
    subject = f'📬 New Application - {job_title}'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📬 New Application</h1>
                <p>Someone applied to your job posting</p>
            </div>
            <div class="content">
                <h2>Hi {employer_name}! 👋</h2>
                <p>You have received a new application for your job posting.</p>
                
                <div class="job-card">
                    <p class="job-title">{job_title}</p>
                    <p class="job-company">👤 Applicant: <strong>{candidate_name}</strong></p>
                    <p class="job-meta">
                        <span class="badge badge-primary">New Application</span>
                    </p>
                </div>
                
                <p style="text-align: center;">
                    <a href="#" class="btn">Review Application</a>
                </p>
                
                <div class="info-box">
                    💡 <strong>Tip:</strong> Respond to applications quickly to attract top talent!
                </div>
            </div>
            <div class="footer">
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hi {employer_name}!\n\nNew application received for "{job_title}" from {candidate_name}.\n\nJobBoard Team'''
    
    return send_email(employer_email, subject, html_message, plain_message)


def send_application_status_email(candidate_email, candidate_name, job_title, company_name, status):
    """Notify candidate about application status change"""
    status_config = {
        'reviewed': {'emoji': '👀', 'color': '#17a2b8', 'message': 'Your application is being reviewed'},
        'shortlisted': {'emoji': '⭐', 'color': '#28a745', 'message': 'Congratulations! You have been shortlisted'},
        'interview': {'emoji': '📅', 'color': '#667eea', 'message': 'You have been selected for an interview'},
        'rejected': {'emoji': '😔', 'color': '#dc3545', 'message': 'Unfortunately, your application was not selected'},
        'hired': {'emoji': '🎉', 'color': '#28a745', 'message': 'Congratulations! You have been hired'},
    }
    
    config = status_config.get(status, {'emoji': '📋', 'color': '#6c757d', 'message': 'Your application status has been updated'})
    
    subject = f'{config["emoji"]} Application Update - {job_title}'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header" style="background: {config["color"]};">
                <h1>{config["emoji"]} Application Update</h1>
                <p>{status.replace("_", " ").title()}</p>
            </div>
            <div class="content">
                <h2>Hi {candidate_name}! 👋</h2>
                <p>{config["message"]} for the following position:</p>
                
                <div class="job-card">
                    <p class="job-title">{job_title}</p>
                    <p class="job-company">🏢 {company_name}</p>
                    <p class="job-meta">
                        <span class="badge" style="background: {config["color"]}; color: white;">{status.replace("_", " ").title()}</span>
                    </p>
                </div>
                
                {"<div class='success-box'>🎊 <strong>Next Steps:</strong> The employer will contact you soon with more details.</div>" if status in ['shortlisted', 'interview', 'hired'] else ""}
                
                <p style="text-align: center;">
                    <a href="#" class="btn">View Details</a>
                </p>
            </div>
            <div class="footer">
                <p>Keep exploring more opportunities on JobBoard!</p>
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hi {candidate_name}!\n\n{config["message"]} for "{job_title}" at {company_name}.\n\nStatus: {status.title()}\n\nJobBoard Team'''
    
    return send_email(candidate_email, subject, html_message, plain_message)


def send_password_reset_email(email, otp, name="User"):
    """Send password reset OTP email"""
    subject = '🔑 Password Reset Request - JobBoard'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head><style>{get_email_base_style()}</style></head>
    <body>
        <div class="container">
            <div class="header" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
                <h1>🔑 Password Reset</h1>
                <p>Reset your account password</p>
            </div>
            <div class="content">
                <h2>Hi {name}! 👋</h2>
                <p>We received a request to reset your password. Use the OTP below to reset your password:</p>
                
                <div class="otp-box">
                    <p style="margin: 0; color: #666;">Your Reset Code</p>
                    <p class="otp-code">{otp}</p>
                </div>
                
                <div class="warning-box">
                    ⚠️ <strong>Important:</strong> This OTP is valid for 10 minutes. If you didn't request this, please ignore this email.
                </div>
                
                <p>For security reasons, never share this code with anyone.</p>
            </div>
            <div class="footer">
                <p>If you didn't request a password reset, your account is safe.</p>
                <p>© 2025 JobBoard. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = f'''Hi {name}!\n\nYour Password Reset OTP: {otp}\n\nThis OTP is valid for 10 minutes.\n\nIf you didn't request this, please ignore.\n\nJobBoard Team'''
    
    return send_email(email, subject, html_message, plain_message)


# ============================================
# MAIN PAGES
# ============================================

def home(request):
    """Home page with featured and recent jobs"""
    featured_jobs = Job.objects.filter(is_active=True, is_featured=True)[:3]
    recent_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    total_jobs = Job.objects.filter(is_active=True).count()
    total_companies = Company.objects.count()
    
    context = {
        'featured_jobs': featured_jobs,
        'jobs': recent_jobs,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }
    return render(request, 'myapp/index.html', context)


def about(request):
    return render(request, 'myapp/about.html')


def contact(request):
    return render(request, 'myapp/contact.html')


def faq(request):
    return render(request, 'myapp/faq.html')


# ============================================
# JOB BROWSING & SEARCH
# ============================================

def browse_jobs(request):
    """Browse all jobs with filters"""
    jobs = Job.objects.filter(is_active=True)
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    experience = request.GET.get('experience', '')
    
    # Apply filters
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(skills_required__icontains=search_query)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if experience:
        jobs = jobs.filter(experience_required=experience)
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'location': location,
        'job_type': job_type,
        'experience': experience,
        'total_jobs': jobs.count(),
    }
    return render(request, 'myapp/job-listings.html', context)


def search_jobs(request):
    """Search jobs from home page"""
    title = request.GET.get('title', '')
    region = request.GET.get('region', '')
    job_type = request.GET.get('type', '')
    
    jobs = Job.objects.filter(is_active=True)
    
    if title:
        jobs = jobs.filter(
            Q(title__icontains=title) |
            Q(company_name__icontains=title) |
            Q(description__icontains=title)
        )
    
    if region:
        jobs = jobs.filter(location__icontains=region)
    
    if job_type:
        jobs = jobs.filter(job_type__icontains=job_type)
    
    context = {
        'jobs': jobs,
        'title': title,
        'region': region,
        'type': job_type,
        'total_jobs': jobs.count(),
    }
    return render(request, 'myapp/search-results.html', context)


def job_detail(request, job_id):
    """Job detail page"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Increment view count
    job.views_count += 1
    job.save()
    
    # Initialize user state variables
    has_applied = False
    has_saved = False
    is_owner = False
    user_role = None
    
    if request.session.get('email'):
        try:
            user = UserMaster.objects.get(email=request.session['email'])
            user_role = user.role
            
            if user.role == 'candidate':
                candidate = Candidate.objects.get(user_id=user)
                has_applied = JobApplication.objects.filter(job=job, candidate=candidate).exists()
                has_saved = SavedJob.objects.filter(job=job, candidate=candidate).exists()
            elif user.role == 'company':
                company = Company.objects.get(user_id=user)
                is_owner = (job.company == company)
        except (UserMaster.DoesNotExist, Candidate.DoesNotExist, Company.DoesNotExist):
            logger.warning(f"User profile not found for session email: {request.session.get('email')}")
            pass
    
    # Similar jobs
    similar_jobs = Job.objects.filter(
        is_active=True,
        job_type=job.job_type
    ).exclude(id=job.id)[:3]
    
    context = {
        'job': job,
        'similar_jobs': similar_jobs,
        'has_applied': has_applied,
        'has_saved': has_saved,
        'is_owner': is_owner,
        'user_role': user_role,
    }
    return render(request, 'myapp/job-single.html', context)


# ============================================
# JOB APPLICATION (CANDIDATE)
# ============================================

@require_http_methods(["GET", "POST"])
def apply_job(request, job_id):
    """Apply for a job"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to apply for jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a candidate
        if user.role != 'candidate':
            messages.error(request, 'Only candidates can apply for jobs')
            return redirect('job_detail', job_id=job_id)
        
        candidate = Candidate.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, candidate=candidate).exists():
            messages.warning(request, 'You have already applied for this job')
            return redirect('job_detail', job_id=job_id)
        
        if request.method == 'POST':
            cover_letter = request.POST.get('cover_letter', '').strip()
            resume = request.FILES.get('resume')
            
            # Basic validation
            if not cover_letter:
                messages.error(request, 'Please provide a cover letter')
                context = {'job': job}
                return render(request, 'myapp/apply-job.html', context)
            
            with transaction.atomic():
                application = JobApplication.objects.create(
                    job=job,
                    candidate=candidate,
                    cover_letter=cover_letter,
                    resume=resume,
                    status='pending'
                )
            
            # Send email to candidate confirming application
            send_application_received_email(
                candidate.email,
                candidate.first_name,
                job.title,
                job.company_name
            )
            
            # Send email to employer about new application
            if job.company:
                try:
                    employer = job.company
                    employer_user = employer.user_id
                    send_new_application_notification(
                        employer_user.email,
                        employer.firstname,
                        f"{candidate.first_name} {candidate.last_name}",
                        job.title,
                        application.id
                    )
                except Exception as e:
                    logger.error(f"Failed to notify employer: {str(e)}")
            
            messages.success(request, f'Application submitted successfully for {job.title}!')
            return redirect('my_applications')
        
        # GET request - show application form
        context = {
            'job': job,
            'candidate': candidate,
        }
        return render(request, 'myapp/apply-job.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in apply_job: {str(e)}')
        messages.error(request, 'An error occurred while processing your application.')
        return redirect('job_detail', job_id=job_id)


def save_job(request, job_id):
    """Save/bookmark a job"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to save jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a candidate
        if user.role != 'candidate':
            messages.error(request, 'Only candidates can save jobs')
            return redirect('job_detail', job_id=job_id)
        
        candidate = Candidate.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        saved_job, created = SavedJob.objects.get_or_create(candidate=candidate, job=job)
        
        if created:
            messages.success(request, 'Job saved successfully!')
        else:
            saved_job.delete()
            messages.info(request, 'Job removed from saved list')
        
        return redirect('job_detail', job_id=job_id)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in save_job: {str(e)}')
        messages.error(request, 'An error occurred while saving the job.')
        return redirect('job_detail', job_id=job_id)


def my_applications(request):
    """View candidate's applications"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to view your applications')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a candidate
        if user.role != 'candidate':
            messages.error(request, 'Only candidates can view applications')
            return redirect('home')
        
        candidate = Candidate.objects.get(user_id=user)
        applications = JobApplication.objects.filter(candidate=candidate).select_related('job', 'job__company')
        
        context = {'applications': applications}
        return render(request, 'myapp/my-applications.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in my_applications: {str(e)}')
        messages.error(request, 'An error occurred while loading your applications.')
        return redirect('home')


def saved_jobs_view(request):
    """View saved jobs"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to view saved jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a candidate
        if user.role != 'candidate':
            messages.error(request, 'Only candidates can view saved jobs')
            return redirect('home')
        
        candidate = Candidate.objects.get(user_id=user)
        saved_jobs = SavedJob.objects.filter(candidate=candidate).select_related('job', 'job__company')
        
        context = {'saved_jobs': saved_jobs}
        return render(request, 'myapp/saved-jobs.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in saved_jobs_view: {str(e)}')
        messages.error(request, 'An error occurred while loading saved jobs.')
        return redirect('home')


# ============================================
# JOB POSTING (EMPLOYER)
# ============================================

@require_http_methods(["GET", "POST"])
def post_job(request):
    """Post a new job (Employer only)"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to post jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        if user.role != 'company':
            messages.error(request, 'Only employers can post jobs')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        
        if request.method == 'POST':
            # Validate required fields
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            location = request.POST.get('location', '').strip()
            job_type = request.POST.get('job_type', '').strip()
            experience_required = request.POST.get('experience_required', '').strip()
            
            # Basic validation
            if not all([title, description, location, job_type]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'myapp/post_job.html')
            
            # Optional fields
            salary = request.POST.get('salary', '').strip()
            requirements = request.POST.get('requirements', '').strip()
            skills_required = request.POST.get('skills_required', '').strip()
            responsibilities = request.POST.get('responsibilities', '').strip()
            benefits = request.POST.get('benefits', '').strip()
            
            # Handle vacancies
            try:
                vacancies = int(request.POST.get('vacancies', 1))
                if vacancies < 1:
                    vacancies = 1
            except (ValueError, TypeError):
                vacancies = 1
            
            # Handle application deadline
            application_deadline = request.POST.get('application_deadline')
            if application_deadline:
                try:
                    deadline_date = datetime.strptime(application_deadline, '%Y-%m-%d').date()
                    if deadline_date < date.today():
                        messages.error(request, 'Application deadline cannot be in the past.')
                        return render(request, 'myapp/post_job.html')
                except ValueError:
                    application_deadline = None
            else:
                application_deadline = None
            
            with transaction.atomic():
                Job.objects.create(
                    company=company,
                    title=title,
                    company_name=company.company_name,
                    description=description,
                    location=location,
                    job_type=job_type,
                    experience_required=experience_required,
                    salary=salary,
                    requirements=requirements,
                    skills_required=skills_required,
                    responsibilities=responsibilities,
                    benefits=benefits,
                    vacancies=vacancies,
                    application_deadline=application_deadline,
                    is_active=True
                )
            
            messages.success(request, 'Job posted successfully!')
            return redirect('my_jobs')
        
        # GET request - show form
        context = {
            'job_types': Job.JOB_TYPE_CHOICES,
            'experience_choices': Job.EXPERIENCE_CHOICES,
        }
        return render(request, 'myapp/post_job.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in post_job: {str(e)}')
        messages.error(request, 'An error occurred while posting the job.')
        return redirect('home')


def my_jobs(request):
    """View employer's posted jobs"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to view your jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a company
        if user.role != 'company':
            messages.error(request, 'Only employers can view posted jobs')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        jobs = Job.objects.filter(company=company).order_by('-created_at')
        
        context = {'jobs': jobs}
        return render(request, 'myapp/my-jobs.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in my_jobs: {str(e)}')
        messages.error(request, 'An error occurred while loading your jobs.')
        return redirect('home')


@require_http_methods(["GET", "POST"])
def edit_job(request, job_id):
    """Edit a job posting"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to edit jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a company
        if user.role != 'company':
            messages.error(request, 'Only employers can edit jobs')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        if request.method == 'POST':
            # Validate required fields
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            location = request.POST.get('location', '').strip()
            job_type = request.POST.get('job_type', '').strip()
            experience_required = request.POST.get('experience_required', '').strip()
            
            # Basic validation
            if not all([title, description, location, job_type]):
                messages.error(request, 'Please fill in all required fields.')
                context = {
                    'job': job,
                    'job_types': Job.JOB_TYPE_CHOICES,
                    'experience_choices': Job.EXPERIENCE_CHOICES,
                }
                return render(request, 'myapp/edit-job.html', context)
            
            # Handle vacancies
            try:
                vacancies = int(request.POST.get('vacancies', 1))
                if vacancies < 1:
                    vacancies = 1
            except (ValueError, TypeError):
                vacancies = 1
            
            # Handle application deadline
            application_deadline = request.POST.get('application_deadline')
            if application_deadline:
                try:
                    deadline_date = datetime.strptime(application_deadline, '%Y-%m-%d').date()
                    if deadline_date < date.today():
                        messages.error(request, 'Application deadline cannot be in the past.')
                        context = {
                            'job': job,
                            'job_types': Job.JOB_TYPE_CHOICES,
                            'experience_choices': Job.EXPERIENCE_CHOICES,
                        }
                        return render(request, 'myapp/edit-job.html', context)
                except ValueError:
                    application_deadline = None
            else:
                application_deadline = None
            
            # Update job fields
            with transaction.atomic():
                job.title = title
                job.description = description
                job.location = location
                job.job_type = job_type
                job.experience_required = experience_required
                job.salary = request.POST.get('salary', '').strip()
                job.requirements = request.POST.get('requirements', '').strip()
                job.skills_required = request.POST.get('skills_required', '').strip()
                job.responsibilities = request.POST.get('responsibilities', '').strip()
                job.benefits = request.POST.get('benefits', '').strip()
                job.vacancies = vacancies
                job.application_deadline = application_deadline
                job.save()
            
            messages.success(request, 'Job updated successfully!')
            return redirect('my_jobs')
        
        # GET request - show form
        context = {
            'job': job,
            'job_types': Job.JOB_TYPE_CHOICES,
            'experience_choices': Job.EXPERIENCE_CHOICES,
        }
        return render(request, 'myapp/edit-job.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in edit_job: {str(e)}')
        messages.error(request, 'An error occurred while editing the job.')
        return redirect('my_jobs')


@require_http_methods(["POST"])
def delete_job(request, job_id):
    """Delete a job posting"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to delete jobs')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a company
        if user.role != 'company':
            messages.error(request, 'Only employers can delete jobs')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        job_title = job.title  # Store for success message
        
        with transaction.atomic():
            job.delete()
        
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect('my_jobs')
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in delete_job: {str(e)}')
        messages.error(request, 'An error occurred while deleting the job.')
        return redirect('my_jobs')


def job_applications(request, job_id):
    """View applications for a specific job (Employer)"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to view applications')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a company
        if user.role != 'company':
            messages.error(request, 'Only employers can view job applications')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, company=company)
        applications = JobApplication.objects.filter(job=job).select_related('candidate').order_by('-applied_at')
        
        context = {
            'job': job,
            'applications': applications,
            'status_choices': JobApplication.STATUS_CHOICES,
        }
        return render(request, 'myapp/job-applications.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in job_applications: {str(e)}')
        messages.error(request, 'An error occurred while loading applications.')
        return redirect('my_jobs')


@require_http_methods(["POST"])
def update_application_status(request, application_id):
    """Update application status"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to update application status')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Check if user is a company
        if user.role != 'company':
            messages.error(request, 'Only employers can update application status')
            return redirect('home')
        
        company = Company.objects.get(user_id=user)
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Verify that the job belongs to this company
        if application.job.company != company:
            messages.error(request, 'You can only update applications for your own jobs')
            return redirect('my_jobs')
        
        new_status = request.POST.get('status')
        
        # Validate status
        valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status selected')
            return redirect('job_applications', job_id=application.job.id)
        
        # Update status
        with transaction.atomic():
            old_status = application.status
            application.status = new_status
            application.save()
        
        # Send email notification to candidate about status change
        if old_status != new_status:
            try:
                candidate = application.candidate
                send_application_status_email(
                    candidate.email,
                    candidate.first_name,
                    application.job.title,
                    application.job.company_name,
                    new_status
                )
            except Exception as e:
                logger.error(f"Failed to send status update email: {str(e)}")
        
        messages.success(request, f'Application status updated to {new_status.title()}!')
        return redirect('job_applications', job_id=application.job.id)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in update_application_status: {str(e)}')
        messages.error(request, 'An error occurred while updating the application status.')
        return redirect('my_jobs')


# ============================================
# AUTHENTICATION
# ============================================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handles login and session setup"""
    if request.method == "POST":
        email_from_form = request.POST.get('email', '').strip().lower()
        password_from_form = request.POST.get('password', '')

        # Basic validation
        if not email_from_form or not password_from_form:
            msg = "❌ Please enter both email and password."
            return render(request, 'myapp/login.html', {'msg': msg})

        # Validate email format
        try:
            validate_email(email_from_form)
        except ValidationError:
            msg = "❌ Invalid email format."
            return render(request, 'myapp/login.html', {'msg': msg})

        try:
            # TODO: Use proper password hashing in the future
            user = UserMaster.objects.get(email=email_from_form, password=password_from_form)

            # Check if user is active
            if not user.is_active:
                msg = "❌ Your account has been deactivated. Please contact support."
                return render(request, 'myapp/login.html', {'msg': msg})

            if user.is_verified:
                # Set up session
                request.session['email'] = user.email
                request.session['role'] = user.role
                request.session['user_id'] = user.id

                # Get role-specific profile data
                if user.role == 'candidate':
                    try:
                        candidate = Candidate.objects.get(user_id=user)
                        request.session['firstname'] = candidate.first_name
                        request.session['lastname'] = candidate.last_name
                        request.session['profile_id'] = candidate.id
                    except Candidate.DoesNotExist:
                        logger.warning(f"Candidate profile not found for user {user.email}")
                        request.session['firstname'] = ''
                        request.session['lastname'] = ''
                        
                elif user.role == 'company':
                    try:
                        company = Company.objects.get(user_id=user)
                        request.session['firstname'] = company.firstname
                        request.session['lastname'] = company.lastname
                        request.session['company_name'] = company.company_name
                        request.session['profile_id'] = company.id
                    except Company.DoesNotExist:
                        logger.warning(f"Company profile not found for user {user.email}")
                        request.session['firstname'] = ''
                        request.session['lastname'] = ''

                messages.success(request, f'Welcome back, {request.session.get("firstname", "User")}!')
                
                # Redirect to next page if specified, otherwise home
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
            else:
                msg = "⚠️ Please verify your account using the OTP sent to your email."
                return render(request, 'myapp/login.html', {'msg': msg, 'email': email_from_form})

        except UserMaster.DoesNotExist:
            msg = "❌ Invalid email or password."
            return render(request, 'myapp/login.html', {'msg': msg})
        except Exception as e:
            logger.error(f"Error in login_view: {str(e)}")
            msg = "❌ An error occurred during login. Please try again."
            return render(request, 'myapp/login.html', {'msg': msg})

    return render(request, 'myapp/login.html')


def register(request):
    return render(request, 'myapp/register.html')


@require_http_methods(["GET", "POST"])
def RegisterUser(request):
    if request.method == "POST":
        # Get form data
        role = request.POST.get('role', '').lower().strip()
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        cpassword = request.POST.get('cpassword', '')

        # Validation
        errors = []
        
        # Check required fields
        if not all([role, fname, lname, email, password, cpassword]):
            errors.append("All fields are required")
        
        # Validate role
        if role not in ['candidate', 'company']:
            errors.append("Invalid role selected")
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            errors.append("Invalid email format")
        
        # Check password match
        if password != cpassword:
            errors.append("Passwords do not match")
        
        # Check password strength
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        # Check if user exists
        if UserMaster.objects.filter(email=email).exists():
            errors.append("User with this email already exists")
        
        # If there are errors, return to form
        if errors:
            return render(request, 'myapp/register.html', {
                'msg': ". ".join(errors),
                'form_data': request.POST
            })

        try:
            with transaction.atomic():
                # Generate OTP
                otp = randint(10000, 99999)
                
                # Create user with hashed password (for future security improvement)
                # Note: Currently storing plain text for compatibility
                newuser = UserMaster.objects.create(
                    role=role, 
                    otp=otp, 
                    email=email, 
                    password=password,  # TODO: Hash this password
                    is_active=True,
                    is_verified=False
                )

                # Create role-specific profile
                if role == "candidate":
                    Candidate.objects.create(
                        user_id=newuser,
                        first_name=fname,
                        last_name=lname,
                        email=email
                    )
                elif role == "company":
                    company_name = request.POST.get('company_name', f"{fname} {lname} Company").strip()
                    if not company_name:
                        company_name = f"{fname} {lname} Company"
                    
                    Company.objects.create(
                        user_id=newuser,
                        firstname=fname,
                        lastname=lname,
                        company_name=company_name,
                        state='',
                        city='',
                        contact='',
                        address=''
                    )

            # Send OTP via email
            email_sent = send_otp_email(email, otp, fname)
            
            if email_sent:
                messages.success(request, f"Registration successful! OTP sent to {email}")
            else:
                messages.warning(request, f"Registration successful! OTP: {otp} (Email service unavailable)")
                logger.info(f"OTP for {email}: {otp}")
            
            return render(request, 'myapp/otp.html', {"email": email})
            
        except Exception as e:
            logger.error(f"Error in RegisterUser: {str(e)}")
            return render(request, 'myapp/register.html', {
                'msg': "An error occurred during registration. Please try again.",
                'form_data': request.POST
            })

    return render(request, 'myapp/register.html')


def otp_page(request):
    email = request.session.get('email', '')
    return render(request, 'myapp/otp.html', {'email': email})


@require_http_methods(["GET", "POST"])
def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        otp_entered = request.POST.get('otp', '').strip()

        # Basic validation
        if not email or not otp_entered:
            msg = "❌ Please enter both email and OTP."
            return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})

        # Validate OTP format (should be 5 digits)
        if not otp_entered.isdigit() or len(otp_entered) != 5:
            msg = "❌ OTP must be a 5-digit number."
            return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})

        try:
            user = UserMaster.objects.get(email=email)
            
            # Check if already verified
            if user.is_verified:
                msg = "✅ Account already verified. You can login now."
                return render(request, 'myapp/login.html', {'msg': msg})
            
            if str(user.otp) == str(otp_entered):
                with transaction.atomic():
                    user.is_verified = True
                    user.otp = 0  # Clear OTP for security
                    user.save()
                
                # Send welcome email
                try:
                    name = "User"
                    if user.role == 'candidate':
                        candidate = Candidate.objects.get(user_id=user)
                        name = candidate.first_name
                    elif user.role == 'company':
                        company = Company.objects.get(user_id=user)
                        name = company.firstname
                    
                    send_welcome_email(email, name, user.role)
                except Exception as e:
                    logger.error(f"Failed to send welcome email: {str(e)}")
                
                logger.info(f"User {email} verified successfully")
                msg = "✅ OTP verified successfully! You can now login."
                return render(request, 'myapp/login.html', {'msg': msg})
            else:
                msg = "❌ Invalid OTP. Please try again."
                return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
                
        except UserMaster.DoesNotExist:
            msg = "⚠️ No account found for this email."
            return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
        except Exception as e:
            logger.error(f"Error in verify_otp: {str(e)}")
            msg = "❌ An error occurred during verification. Please try again."
            return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
    else:
        email = request.GET.get('email', '')
        return render(request, 'myapp/otp.html', {'email': email})


@require_http_methods(["GET", "POST"])
def resend_otp(request):
    email = request.GET.get('email', '').strip().lower()
    
    if not email:
        msg = "❌ Email address is required."
        return render(request, 'myapp/otp.html', {'msg': msg})
    
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        msg = "❌ Invalid email format."
        return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
    
    try:
        user = UserMaster.objects.get(email=email)
        
        # Check if already verified
        if user.is_verified:
            msg = "✅ Account already verified. You can login now."
            return render(request, 'myapp/login.html', {'msg': msg})
        
        # Generate new OTP
        new_otp = randint(10000, 99999)
        
        with transaction.atomic():
            user.otp = new_otp
            user.save()
        
        # Get user's name for email
        name = "User"
        try:
            if user.role == 'candidate':
                candidate = Candidate.objects.get(user_id=user)
                name = candidate.first_name
            elif user.role == 'company':
                company = Company.objects.get(user_id=user)
                name = company.firstname
        except:
            pass
        
        # Send OTP via email
        email_sent = send_otp_email(email, new_otp, name)
        
        if email_sent:
            msg = f"✅ New OTP sent to {email}. Please check your email."
        else:
            msg = f"✅ New OTP: {new_otp} (Email service unavailable)"
            logger.info(f"New OTP for {email}: {new_otp}")
        
        return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
        
    except UserMaster.DoesNotExist:
        msg = "❌ No account found for this email address."
        return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})
    except Exception as e:
        logger.error(f"Error in resend_otp: {str(e)}")
        msg = "❌ An error occurred while resending OTP. Please try again."
        return render(request, 'myapp/otp.html', {'msg': msg, 'email': email})


def user_logout(request):
    """Logs out the user and clears all session data."""
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


# ============================================
# FORGOT PASSWORD
# ============================================

@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Handle forgot password - send OTP to email"""
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            return render(request, 'myapp/forgot-password.html', {'msg': '❌ Please enter your email address.'})
        
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'myapp/forgot-password.html', {'msg': '❌ Invalid email format.'})
        
        try:
            user = UserMaster.objects.get(email=email)
            
            # Generate OTP for password reset
            otp = randint(10000, 99999)
            
            with transaction.atomic():
                user.otp = otp
                user.save()
            
            # Get user's name
            name = "User"
            try:
                if user.role == 'candidate':
                    candidate = Candidate.objects.get(user_id=user)
                    name = candidate.first_name
                elif user.role == 'company':
                    company = Company.objects.get(user_id=user)
                    name = company.firstname
            except:
                pass
            
            # Send password reset email
            email_sent = send_password_reset_email(email, otp, name)
            
            if email_sent:
                messages.success(request, f'Password reset OTP sent to {email}')
            else:
                messages.warning(request, f'OTP: {otp} (Email service unavailable)')
            
            return render(request, 'myapp/reset-password.html', {'email': email})
            
        except UserMaster.DoesNotExist:
            return render(request, 'myapp/forgot-password.html', {'msg': '❌ No account found with this email.'})
        except Exception as e:
            logger.error(f"Error in forgot_password: {str(e)}")
            return render(request, 'myapp/forgot-password.html', {'msg': '❌ An error occurred. Please try again.'})
    
    return render(request, 'myapp/forgot-password.html')


@require_http_methods(["GET", "POST"])
def reset_password(request):
    """Verify OTP and reset password"""
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        otp_entered = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([email, otp_entered, new_password, confirm_password]):
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ All fields are required.',
                'email': email
            })
        
        if not otp_entered.isdigit() or len(otp_entered) != 5:
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ OTP must be a 5-digit number.',
                'email': email
            })
        
        if new_password != confirm_password:
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ Passwords do not match.',
                'email': email
            })
        
        if len(new_password) < 6:
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ Password must be at least 6 characters.',
                'email': email
            })
        
        try:
            user = UserMaster.objects.get(email=email)
            
            if str(user.otp) == str(otp_entered):
                with transaction.atomic():
                    user.password = new_password  # TODO: Hash password in production
                    user.otp = 0  # Clear OTP
                    user.save()
                
                messages.success(request, '✅ Password reset successful! You can now login.')
                return redirect('login')
            else:
                return render(request, 'myapp/reset-password.html', {
                    'msg': '❌ Invalid OTP. Please try again.',
                    'email': email
                })
                
        except UserMaster.DoesNotExist:
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ No account found with this email.',
                'email': email
            })
        except Exception as e:
            logger.error(f"Error in reset_password: {str(e)}")
            return render(request, 'myapp/reset-password.html', {
                'msg': '❌ An error occurred. Please try again.',
                'email': email
            })
    
    email = request.GET.get('email', '')
    return render(request, 'myapp/reset-password.html', {'email': email})


@require_http_methods(["GET"])
def resend_reset_otp(request):
    """Resend password reset OTP"""
    email = request.GET.get('email', '').strip().lower()
    
    if not email:
        return redirect('forgot_password')
    
    try:
        user = UserMaster.objects.get(email=email)
        
        # Generate new OTP
        otp = randint(10000, 99999)
        
        with transaction.atomic():
            user.otp = otp
            user.save()
        
        # Get user's name
        name = "User"
        try:
            if user.role == 'candidate':
                candidate = Candidate.objects.get(user_id=user)
                name = candidate.first_name
            elif user.role == 'company':
                company = Company.objects.get(user_id=user)
                name = company.firstname
        except:
            pass
        
        # Send email
        email_sent = send_password_reset_email(email, otp, name)
        
        if email_sent:
            messages.success(request, f'New OTP sent to {email}')
        else:
            messages.warning(request, f'OTP: {otp} (Email service unavailable)')
        
        return render(request, 'myapp/reset-password.html', {'email': email})
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'No account found with this email.')
        return redirect('forgot_password')
    except Exception as e:
        logger.error(f"Error in resend_reset_otp: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('forgot_password')


def profile_view(request):
    """View user profile"""
    if not request.session.get('email'):
        messages.error(request, 'Please login to view your profile')
        return redirect('login')
    
    try:
        user = UserMaster.objects.get(email=request.session['email'])
        
        if user.role == 'candidate':
            candidate = Candidate.objects.get(user_id=user)
            context = {
                'user': user, 
                'profile': candidate, 
                'role': 'candidate'
            }
        elif user.role == 'company':
            company = Company.objects.get(user_id=user)
            context = {
                'user': user, 
                'profile': company, 
                'role': 'company'
            }
        else:
            context = {'user': user, 'role': 'unknown'}
        
        return render(request, 'myapp/profile.html', context)
        
    except UserMaster.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('login')
    except (Candidate.DoesNotExist, Company.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f'Error in profile_view: {str(e)}')
        messages.error(request, 'An error occurred while loading your profile.')
        return redirect('home')


# ============================================
# EDUCATIONAL CHATBOT
# ============================================

@csrf_exempt
def chat_api(request):
    """
    API endpoint for the educational chatbot - Engineering Tutor.
    Fast responses with code teaching capabilities.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Configure Gemini API
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            
            if not api_key:
                return JsonResponse({
                    'response': '⚠️ **API Key Required**\n\nTo use the Engineering Tutor, please:\n\n1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)\n2. Set it in your environment:\n```bash\nset GEMINI_API_KEY=your_key_here\n```\n3. Restart the server'
                })

            genai.configure(api_key=api_key)
            
            # Concise system prompt for faster responses
            system_prompt = """You are an Engineering Tutor. Help with coding and engineering questions.
- Write clean code with comments
- Use ```language for code blocks
- Be concise"""
            
            # Try multiple models in order of preference
            models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-2.0-flash-lite']
            
            prompt = f"{system_prompt}\n\nQ: {user_message}\n\nA:"
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.7,
                            'max_output_tokens': 800,
                        }
                    )
                    
                    if response and response.text:
                        return JsonResponse({'response': response.text})
                except Exception:
                    continue
            
            return JsonResponse({
                'response': '⚠️ **AI Service Unavailable**\n\nThe AI teacher is currently offline. This is usually due to an invalid API key or reaching the free tier limit. Please check settings.'
            })
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Chat API error: {error_msg}")
            
            if 'api key' in error_msg.lower() or '403' in error_msg or 'invalid' in error_msg.lower():
                return JsonResponse({
                    'response': '⚠️ **API Key Issue**\n\nThe provided Gemini API key seems to be invalid or expired. Please update your `GEMINI_API_KEY` in `settings.py` or environment variables.'
                })
            
            if '429' in error_msg or 'quota' in error_msg.lower():
                return JsonResponse({
                    'response': '⏳ **Rate Limit**\n\nPlease wait a minute and try again. The free tier has limited requests.'
                })
            
            # Return a informative message instead of 500 for other errors too
            return JsonResponse({
                'response': f'❌ **Error**: {error_msg}\n\nPlease try again later.'
            })
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)