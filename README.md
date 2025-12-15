# Student Performance Management System

A Django-based web application for managing student performance, tracking academic progress, and facilitating communication between educators and administrators.

## Project Structure

```
student_performance/
├── student_performance/     # Project settings and configuration
├── accounts/               # Authentication and user management
├── administration/         # Administration features
├── education/             # Education and academic features
├── templates/             # Project-level templates
├── static/               # Static assets (CSS, JS, images)
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## Technology Stack

- **Framework**: Django 6.0
- **Database**: SQLite (development)
- **Python**: 3.x
- **Environment**: python-dotenv for configuration management

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd student_performance
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the `.env.example` file to `.env` and update the values as needed:

```bash
cp .env.example .env
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set up an admin account with:
- Username
- Email address
- Password

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Features

### Apps

#### Accounts App
- User authentication
- Profile management
- Shared auth utilities for other apps

#### Administration App
- System administration tools
- User and role management
- System configuration

#### Education App
- Academic performance tracking
- Student data management
- Educational features

## Common Commands

### Database Operations

```bash
# Create migrations for changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Rollback migrations
python manage.py migrate [app_name] [migration_number]
```

### User Management

```bash
# Create a superuser
python manage.py createsuperuser

# Create a regular user (if custom command available)
python manage.py create_user [username] [email]
```

### Development

```bash
# Run the development server
python manage.py runserver

# Run tests
python manage.py test

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## Project Settings

Key settings are configured in `student_performance/settings.py`:

- **TIME_ZONE**: UTC (configurable via .env)
- **LANGUAGE_CODE**: en-us
- **STATIC_URL**: /static/
- **MEDIA_URL**: /media/
- **DATABASES**: SQLite by default

## Installed Apps

1. `accounts` - User authentication and profiles
2. `administration` - Admin features
3. `education` - Educational features
4. Django built-in apps (admin, auth, contenttypes, sessions, messages, staticfiles)

## URL Structure

- `/` - Home page
- `/accounts/` - Account-related URLs
- `/administration/` - Administration URLs
- `/education/` - Education-related URLs
- `/admin/` - Django admin panel

## Static and Media Files

- **Static files**: Stored in `/static/` directory (CSS, JS, images)
- **Media files**: User-uploaded files stored in `/media/` directory
- In development, Django serves these files automatically

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
python manage.py runserver 8001
```

### Database Issues

To reset the database:

```bash
# Remove the old database
rm db.sqlite3

# Run migrations to create a fresh database
python manage.py migrate
```

### Missing Dependencies

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Contributing

When adding new features:

1. Create appropriate models in the respective app
2. Generate and apply migrations
3. Create URL patterns in the app's `urls.py`
4. Create views in the app's `views.py`
5. Add templates in the app's `templates/` directory
6. Update documentation

## License

This project is part of an educational initiative.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
