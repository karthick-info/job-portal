# Django Job Portal

A comprehensive job portal application built with Django, designed to connect job seekers with employers.

## Features

- **User Roles**: Separate interfaces for Job Seekers and Employers.
- **Job Listings**: Browsable and searchable job postings.
- **Applications**: Users can apply for jobs directly through the portal.
- **Email Notifications**: Integrated email system for application updates and notifications.
- **Chatbot API**: Includes a chatbot interface.
- **Responsive Design**: Mobile-friendly UI with styled listings and dashboards.
- **Deployment Ready**: Configured for deployment on platforms like Render (includes `render.yaml`, `build.sh`, `Procfile`).

## Prerequisites

- Python 3.8+
- Django
- pip (Python package manager)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv myvenv
    # Windows
    .\myvenv\Scripts\activate
    # Unix/MacOS
    source myvenv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000/`.

## Project Structure

- `myapp/`: Contains the main application logic (views, models, templates).
- `myproject/`: Project settings and configurations.
- `static/`: Static assets (CSS, JS, images).
- `media/`: User-uploaded content.
- `templates/`: HTML templates.

## Deployment

The project is configured for deployment on Render.
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn myproject.wsgi --log-file -`

## License

MIT License
