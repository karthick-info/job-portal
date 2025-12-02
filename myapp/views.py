from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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
                JobApplication.objects.create(
                    job=job,
                    candidate=candidate,
                    cover_letter=cover_letter,
                    resume=resume,
                    status='pending'
                )
            
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
            application.status = new_status
            application.save()
        
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

            # Log OTP (in production, send via email)
            logger.info(f"OTP for {email}: {otp}")
            print(f"✅ OTP for {email}: {otp}")
            
            messages.success(request, f"Registration successful! Please check your email for OTP verification.")
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
        
        # Log OTP (in production, send via email)
        logger.info(f"New OTP for {email}: {new_otp}")
        print(f"✅ New OTP for {email}: {new_otp}")
        
        msg = f"✅ New OTP sent to {email}. Please check your email."
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
    API endpoint for the educational chatbot.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Configure Gemini API
            # Try to get key from settings, then environment, then hardcoded placeholder
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            
            if not api_key:
                 return JsonResponse({'error': 'Server configuration error: API Key missing'}, status=500)

            genai.configure(api_key=api_key)
            
            # System prompt to enforce educational scope
            system_instruction = """
            You are an AI tutor for engineering students on a job portal. 
            Your SOLE purpose is to help students learn and study engineering concepts.
            
            RULES:
            1. ONLY answer questions related to engineering, science, math, and coursework.
            2. If a user asks about job applications, resumes, account issues, or general life advice, POLITELY REFUSE and explain that you are only here to help with engineering studies.
            3. Provide clear, simple explanations for difficult concepts.
            4. If asked, generate practice questions for engineering topics.
            5. Do not provide code for entire assignments, but explain the logic or syntax.
            
            Example Refusal: "I apologize, but I am designed specifically to help with engineering studies and coursework. For job application support, please check the FAQ or Contact section."
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
            
            # Construct the full prompt
            full_prompt = f"{system_instruction}\n\nUser: {user_message}\nAI:"
            
            response = model.generate_content(full_prompt)
            
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)