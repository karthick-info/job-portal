# Dual-Role System Implementation in JobBoard

## Overview
The JobBoard application implements a **dual-role authentication system** where users can register and operate as either **Candidates** (job seekers) or **Companies** (employers). This document explains the complete architecture and implementation.

---

## 1. Database Architecture

### Core Model Structure

```
UserMaster (Authentication Layer)
    ├── Candidate (Profile Layer - Job Seekers)
    └── Company (Profile Layer - Employers)
```

### UserMaster Model (Authentication)
```python
class UserMaster(models.Model):
    email = models.EmailField(max_length=50)      # Primary identifier
    password = models.CharField(max_length=50)     # Authentication credential
    otp = models.IntegerField()                    # Email verification
    role = models.CharField(max_length=50)         # 'candidate' or 'company'
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_created = models.DateTimeField(auto_now_add=True)
    is_updated = models.DateTimeField(auto_now=True)
```

**Key Design Decision:** 
- Single authentication table for both roles
- `role` field determines user type
- Email-based login (no username required)

### Candidate Model (Job Seeker Profile)
```python
class Candidate(models.Model):
    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='app/img/candidate')
```

**Candidate-Specific Features:**
- Personal profile information
- Job applications tracking
- Saved jobs functionality
- Resume/CV upload

### Company Model (Employer Profile)
```python
class Company(models.Model):
    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    company_name = models.CharField(max_length=150)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    logo_pic = models.ImageField(upload_to='app/img/company')
```

**Company-Specific Features:**
- Company profile information
- Job posting capabilities
- Application management
- Candidate review system

---

## 2. Registration Flow

### Step-by-Step Process

```
User Registration
    ↓
1. User selects role (Candidate/Company)
    ↓
2. Fills registration form
    ↓
3. System creates UserMaster record
    ↓
4. System creates role-specific profile (Candidate OR Company)
    ↓
5. OTP sent for email verification
    ↓
6. User verifies OTP
    ↓
7. Account activated
```

### Registration Code Implementation

```python
def RegisterUser(request):
    if request.method == "POST":
        # Get form data
        role = request.POST.get('role', '').lower().strip()  # 'candidate' or 'company'
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        # Validation
        if role not in ['candidate', 'company']:
            return error("Invalid role selected")
        
        # Create UserMaster (authentication record)
        otp = randint(10000, 99999)
        newuser = UserMaster.objects.create(
            role=role,           # Store the role
            otp=otp,
            email=email,
            password=password,
            is_active=True,
            is_verified=False
        )
        
        # Create role-specific profile
        if role == "candidate":
            Candidate.objects.create(
                user_id=newuser,      # Link to UserMaster
                first_name=fname,
                last_name=lname,
                email=email
            )
        elif role == "company":
            company_name = request.POST.get('company_name', f"{fname} {lname} Company")
            Company.objects.create(
                user_id=newuser,      # Link to UserMaster
                firstname=fname,
                lastname=lname,
                company_name=company_name
            )
        
        # Send OTP for verification
        return redirect('otp_verification')
```

**Key Points:**
- **Atomic Operation**: Both UserMaster and profile created in transaction
- **Foreign Key Relationship**: Profile links to UserMaster via `user_id`
- **Role Validation**: Ensures only valid roles are accepted
- **Email Verification**: OTP sent before account activation

---

## 3. Login & Session Management

### Login Flow

```
User Login
    ↓
1. User enters email & password
    ↓
2. System queries UserMaster table
    ↓
3. Validates credentials
    ↓
4. Checks is_verified status
    ↓
5. Retrieves role from UserMaster
    ↓
6. Fetches role-specific profile (Candidate OR Company)
    ↓
7. Stores data in session
    ↓
8. Redirects to appropriate dashboard
```

### Login Code Implementation

```python
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        try:
            # Query UserMaster for authentication
            user = UserMaster.objects.get(email=email, password=password)
            
            # Check verification status
            if not user.is_verified:
                return error("Please verify your account using OTP")
            
            # Set up session with role information
            request.session['email'] = user.email
            request.session['role'] = user.role        # Store role in session
            request.session['user_id'] = user.id
            
            # Fetch role-specific profile data
            if user.role == 'candidate':
                candidate = Candidate.objects.get(user_id=user)
                request.session['firstname'] = candidate.first_name
                request.session['lastname'] = candidate.last_name
                request.session['profile_id'] = candidate.id
                
            elif user.role == 'company':
                company = Company.objects.get(user_id=user)
                request.session['firstname'] = company.firstname
                request.session['lastname'] = company.lastname
                request.session['company_name'] = company.company_name
                request.session['profile_id'] = company.id
            
            return redirect('home')
            
        except UserMaster.DoesNotExist:
            return error("Invalid email or password")
```

**Session Data Structure:**
```python
# For Candidates:
session = {
    'email': 'candidate@example.com',
    'role': 'candidate',
    'user_id': 1,
    'profile_id': 1,
    'firstname': 'John',
    'lastname': 'Doe'
}

# For Companies:
session = {
    'email': 'company@example.com',
    'role': 'company',
    'user_id': 2,
    'profile_id': 1,
    'firstname': 'Jane',
    'lastname': 'Smith',
    'company_name': 'Tech Corp'
}
```

---

## 4. Role-Based Authorization

### Authorization Strategy

```
Request Received
    ↓
1. Check if user is logged in (session exists)
    ↓
2. Check user's role from session
    ↓
3. Validate role matches required permission
    ↓
4. Allow or deny access
```

### Authorization Code Examples

#### Candidate-Only View
```python
def apply_job(request, job_id):
    # Step 1: Check authentication
    if not request.session.get('email'):
        messages.error(request, 'Please login to apply for jobs')
        return redirect('login')
    
    try:
        # Step 2: Get user and verify role
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Step 3: Role-based authorization
        if user.role != 'candidate':
            messages.error(request, 'Only candidates can apply for jobs')
            return redirect('job_detail', job_id=job_id)
        
        # Step 4: Get candidate profile
        candidate = Candidate.objects.get(user_id=user)
        
        # Proceed with candidate-specific logic
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, candidate=candidate).exists():
            messages.warning(request, 'You have already applied for this job')
            return redirect('job_detail', job_id=job_id)
        
        # Process application...
        
    except UserMaster.DoesNotExist:
        return redirect('login')
```

#### Company-Only View
```python
def post_job(request):
    # Step 1: Check authentication
    if not request.session.get('email'):
        messages.error(request, 'Please login to post jobs')
        return redirect('login')
    
    try:
        # Step 2: Get user and verify role
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Step 3: Role-based authorization
        if user.role != 'company':
            messages.error(request, 'Only employers can post jobs')
            return redirect('home')
        
        # Step 4: Get company profile
        company = Company.objects.get(user_id=user)
        
        # Proceed with company-specific logic
        if request.method == 'POST':
            Job.objects.create(
                company=company,
                title=request.POST.get('title'),
                # ... other fields
            )
            return redirect('my_jobs')
        
    except UserMaster.DoesNotExist:
        return redirect('login')
```

---

## 5. Template-Based Role Differentiation

### Navigation Menu (base1.html)

```html
<!-- Candidate-specific menu -->
{% if request.session.role == 'candidate' %}
<li class="has-children">
    <a href="#">My Jobs</a>
    <ul class="dropdown">
        <li><a href="{% url 'my_applications' %}">My Applications</a></li>
        <li><a href="{% url 'saved_jobs' %}">Saved Jobs</a></li>
    </ul>
</li>
{% endif %}

<!-- Company-specific menu -->
{% if request.session.role == 'company' %}
<li class="has-children">
    <a href="#">Employer</a>
    <ul class="dropdown">
        <li><a href="{% url 'post_job' %}">Post a Job</a></li>
        <li><a href="{% url 'my_jobs' %}">My Posted Jobs</a></li>
    </ul>
</li>
{% endif %}

<!-- User dropdown with role-specific options -->
{% if request.session.firstname %}
<li class="username-dropdown">
    <button class="username-btn">
        👤 {{ request.session.firstname }} {{ request.session.lastname }} ▼
    </button>
    <div class="dropdown-content">
        <a href="{% url 'profile' %}">Profile</a>
        
        {% if request.session.role == 'candidate' %}
        <a href="{% url 'my_applications' %}">My Applications</a>
        <a href="{% url 'saved_jobs' %}">Saved Jobs</a>
        {% elif request.session.role == 'company' %}
        <a href="{% url 'my_jobs' %}">My Jobs</a>
        <a href="{% url 'post_job' %}">Post Job</a>
        {% endif %}
        
        <a href="{% url 'logout' %}">Logout</a>
    </div>
</li>
{% endif %}
```

### Job Detail Page Actions (job-single.html)

```html
<!-- Apply/Save buttons - Role-based rendering -->
<div class="col-6">
    {% if request.session.email %}
        {% if request.session.role == 'candidate' %}
            <!-- Candidate sees Apply button -->
            {% if has_applied %}
                <button class="btn btn-success" disabled>
                    <span class="icon-check"></span>Applied
                </button>
            {% else %}
                <a href="{% url 'apply_job' job.id %}" class="btn btn-primary">
                    <span class="icon-paper-plane"></span>Apply Now
                </a>
            {% endif %}
            
        {% elif request.session.role == 'company' %}
            <!-- Company sees different options -->
            {% if is_owner %}
                <a href="{% url 'job_applications' job.id %}" class="btn btn-info">
                    <span class="icon-users"></span>View Applications
                </a>
            {% else %}
                <button class="btn btn-secondary" disabled>
                    <span class="icon-lock"></span>Employers Only
                </button>
            {% endif %}
        {% endif %}
    {% else %}
        <!-- Not logged in - show login prompt -->
        <a href="{% url 'login' %}?next={% url 'apply_job' job.id %}" class="btn btn-primary">
            <span class="icon-paper-plane"></span>Apply Now
        </a>
    {% endif %}
</div>
```

---

## 6. Feature Access Matrix

| Feature | Candidate | Company | Not Logged In |
|---------|-----------|---------|---------------|
| Browse Jobs | ✅ Yes | ✅ Yes | ✅ Yes |
| View Job Details | ✅ Yes | ✅ Yes | ✅ Yes |
| Apply for Jobs | ✅ Yes | ❌ No | ❌ Redirect to Login |
| Save Jobs | ✅ Yes | ❌ No | ❌ Redirect to Login |
| View Applications | ✅ Yes (Own) | ❌ No | ❌ Redirect to Login |
| Post Jobs | ❌ No | ✅ Yes | ❌ Redirect to Login |
| Edit Jobs | ❌ No | ✅ Yes (Own) | ❌ Redirect to Login |
| Delete Jobs | ❌ No | ✅ Yes (Own) | ❌ Redirect to Login |
| View Job Applications | ❌ No | ✅ Yes (Own Jobs) | ❌ Redirect to Login |
| Update Application Status | ❌ No | ✅ Yes (Own Jobs) | ❌ Redirect to Login |

---

## 7. Security Considerations

### Multi-Layer Protection

```
Frontend (Template)
    ↓ Hide unauthorized UI elements
Backend (View)
    ↓ Check session authentication
    ↓ Verify role authorization
    ↓ Validate ownership (for edit/delete)
Database
    ↓ Foreign key constraints
    ↓ Unique constraints
```

### Example: Job Deletion Security

```python
def delete_job(request, job_id):
    # Layer 1: Authentication check
    if not request.session.get('email'):
        return redirect('login')
    
    try:
        # Layer 2: Get user and role
        user = UserMaster.objects.get(email=request.session['email'])
        
        # Layer 3: Role authorization
        if user.role != 'company':
            messages.error(request, 'Only employers can delete jobs')
            return redirect('home')
        
        # Layer 4: Ownership verification
        company = Company.objects.get(user_id=user)
        job = get_object_or_404(Job, id=job_id, company=company)
        
        # Only if all checks pass
        job.delete()
        return redirect('my_jobs')
        
    except (UserMaster.DoesNotExist, Company.DoesNotExist):
        return redirect('login')
```

---

## 8. Advantages of This Dual-Role System

### 1. **Single Authentication System**
- One login mechanism for both roles
- Simplified user management
- Easier to maintain and debug

### 2. **Clear Role Separation**
- Distinct profile models for different needs
- Role-specific features and permissions
- No feature overlap or confusion

### 3. **Scalability**
- Easy to add new roles (e.g., admin, moderator)
- Can extend with role hierarchy
- Simple to add role-specific features

### 4. **Security**
- Role stored in database, not just session
- Multi-layer authorization checks
- Ownership verification for sensitive operations

### 5. **User Experience**
- Role-appropriate navigation and features
- Personalized dashboards
- Clear visual distinction between roles

---

## 9. Potential Improvements

### For Production Environment:

1. **Password Hashing**
```python
from django.contrib.auth.hashers import make_password, check_password

# During registration
password_hash = make_password(password)
user = UserMaster.objects.create(password=password_hash, ...)

# During login
if check_password(password_from_form, user.password):
    # Login successful
```

2. **Role Switching** (if needed)
```python
def switch_role(request):
    user = UserMaster.objects.get(email=request.session['email'])
    
    # Check if user has both profiles
    has_candidate = Candidate.objects.filter(user_id=user).exists()
    has_company = Company.objects.filter(user_id=user).exists()
    
    if has_candidate and has_company:
        # Toggle role
        new_role = 'company' if user.role == 'candidate' else 'candidate'
        request.session['role'] = new_role
        # Update session data accordingly
```

3. **Permission-Based System** (for more roles)
```python
class Permission(models.Model):
    name = models.CharField(max_length=50)
    
class Role(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission)
    
class UserMaster(models.Model):
    roles = models.ManyToManyField(Role)
```

---

## 10. Interview Talking Points

### **"How do you handle dual roles in your application?"**

**Answer:**
"I implemented a dual-role system using a three-layer architecture:

1. **Authentication Layer (UserMaster)**: Single table for all users with a `role` field that stores either 'candidate' or 'company'. This handles login, verification, and basic user management.

2. **Profile Layer (Candidate/Company)**: Separate tables for role-specific data, linked to UserMaster via foreign keys. This allows different fields and relationships for each role.

3. **Authorization Layer (Views)**: Every protected view checks both authentication (is user logged in?) and authorization (does user have the right role?). This ensures security at the backend level.

The system uses session-based authentication where the role is stored in the session after login, allowing templates to conditionally render role-appropriate UI elements. For example, candidates see 'Apply' buttons while employers see 'View Applications' buttons on the same job page.

This architecture provides clear separation of concerns, makes the code maintainable, and can easily scale to support additional roles like admins or moderators in the future."

---

## Summary

The dual-role system in JobBoard is implemented through:
- **Database Design**: UserMaster + role-specific profiles
- **Session Management**: Role stored and checked in every request
- **Authorization**: Multi-layer checks (frontend + backend)
- **UI Differentiation**: Template conditionals based on role
- **Security**: Ownership verification and role validation

This creates a secure, maintainable, and user-friendly system that clearly separates candidate and employer functionalities while sharing a common authentication mechanism.
