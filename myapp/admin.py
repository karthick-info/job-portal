from django.contrib import admin
from .models import UserMaster, Company, Candidate, Job, JobApplication, SavedJob, JobAlert

@admin.register(UserMaster)
class UserMasterAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'is_active', 'is_verified', 'is_created']
    list_filter = ['role', 'is_active', 'is_verified']
    search_fields = ['email']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'firstname', 'lastname', 'city', 'state', 'contact']
    list_filter = ['state', 'city']
    search_fields = ['company_name', 'firstname', 'lastname']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'city', 'state', 'phone']
    list_filter = ['state', 'city', 'gender']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'job_type', 'experience_required', 'is_active', 'is_featured', 'created_at']
    list_filter = ['job_type', 'is_active', 'is_featured', 'experience_required', 'location']
    search_fields = ['title', 'company_name', 'description']
    list_editable = ['is_active', 'is_featured']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'job__title']
    list_editable = ['status']

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['candidate__first_name', 'job__title']

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'keywords', 'location', 'job_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'job_type']
    search_fields = ['candidate__first_name', 'keywords']