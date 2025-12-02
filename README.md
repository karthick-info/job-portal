# JobBoard - Find Your Dream Job

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/karthick-info/job-portal)

JobBoard is a comprehensive job portal application built with Django. It connects job seekers with employers, allowing companies to post job openings and candidates to apply for them.

## 🚀 **How to Host This Website**

**Click the "Deploy to Render" button above!** 👆

It will automatically:
1. Connect to your GitHub repository
2. Set up the Python server
3. Configure the database
4. Launch your website for free!

---

## Features

### For Candidates
- **Browse Jobs**: Search and filter jobs by title, location, type, and experience.
- **Apply for Jobs**: Submit applications with a cover letter and resume/CV.
- **Track Applications**: View the status of applied jobs (Pending, Reviewed, Interview, etc.).
- **Save Jobs**: Bookmark jobs to view or apply later.
- **Profile Management**: Update personal information and profile picture.

### For Employers (Companies)
- **Post Jobs**: Create detailed job listings with requirements, salary, and benefits.
- **Manage Jobs**: Edit or delete job postings.
- **View Applications**: Review candidates who have applied to your jobs.
- **Manage Applications**: Update application status (e.g., Shortlist, Reject, Hire) and view candidate CVs.
- **Company Profile**: Manage company details and logo.

### General Features
- **User Authentication**: Secure login and registration for both candidates and companies.
- **OTP Verification**: Email-based OTP verification for account security.
- **Responsive Design**: Modern, mobile-friendly interface.

## Tech Stack

- **Backend**: Python, Django
- **Database**: MySQL (configured in settings.py) or SQLite (default)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Styling**: Custom CSS with responsive design

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd myproject
   ```

2. **Install Dependencies**
   Ensure you have Python installed. Install the required packages:
   ```bash
   pip install django mysqlclient
   ```

3. **Database Setup**
   The project is configured to use MySQL. Update the `DATABASES` setting in `myproject/settings.py` with your database credentials.
   
   If you want to use SQLite for development, you can modify `settings.py` to use `django.db.backends.sqlite3`.

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000`.

## Usage

1. **Register**: Create an account as a Candidate or Company.
2. **Verify Email**: Enter the OTP sent to your email (simulated in console for development).
3. **Login**: Use your credentials to log in.
4. **Start Exploring**:
   - **Candidates**: Go to "Browse Jobs" to find opportunities.
   - **Companies**: Go to "Post a Job" to start hiring.

## Project Structure

- `manage.py`: Django's command-line utility.
- `myproject/`: Project configuration settings.
- `myapp/`: Main application containing models, views, and templates.
  - `models.py`: Database schema for Users, Jobs, Applications, etc.
  - `views.py`: Business logic and request handling.
  - `templates/`: HTML templates for the UI.
  - `static/`: CSS, JavaScript, and image files.
- `media/`: Directory for user-uploaded files (Resumes, Profile Pics).

## License

This project is open-source and available for educational purposes.
