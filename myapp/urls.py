from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Job browsing and search
    path('jobs/', views.browse_jobs, name='browse_jobs'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('search/', views.search_jobs, name='search_jobs'),
    
    # Job application (Candidate)
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/save/', views.save_job, name='save_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    
    # Job posting (Employer)
    path('post-job/', views.post_job, name='post_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('register-user/', views.RegisterUser, name='RegisterUser'),
    path('otp/', views.otp_page, name='otp_page'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-reset-otp/', views.resend_reset_otp, name='resend_reset_otp'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Chatbot
    path('api/chat/', views.chat_api, name='chat_api'),
]
