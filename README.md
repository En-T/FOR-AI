# School Management System - Role-Based Authentication

This Django application implements a comprehensive role-based authentication system for a school management system with Administration and Education departments.

## Features

### ✅ Custom User Model
- Extends Django's `AbstractUser` 
- Role-based access control with `administration` and `education` roles
- Foreign key relationship to `School` model (for admin users)
- Unique email validation
- Custom properties for role checking (`is_admin_user`, `is_education_user`)

### ✅ Django Settings Configuration
- Custom user model configured (`AUTH_USER_MODEL = 'accounts.User'`)
- Email and password validators in place
- Login/logout URL configurations
- Media files handling
- Template directories configured

### ✅ Registration and Login System
- **Registration Form**: Captures username, email, password, role selection, and school (for admins)
- **Login Form**: Custom authentication with role-based redirects
- **Role Selection**: Dynamic form showing/hiding school field based on role
- **Password Reset**: Complete password reset workflow with templates

### ✅ Role-Based Access Control
- **URL Namespaces**: `/administration/` and `/education/`
- **Access Decorators**: `@admin_required` and `@education_required`
- **Automatic Redirects**: Unauthorized users redirected with flash messages
- **Flash Messages**: User-friendly error messages for access denied

### ✅ Department Dashboards
- **Administration Dashboard**: Admin-specific features and statistics
- **Education Dashboard**: Education-specific features and resources
- **Role-Specific Navigation**: Dynamic navigation based on user role
- **Access Control Notices**: Clear messaging about access restrictions

### ✅ Bootstrap Templates
- Modern, responsive design using Bootstrap 5
- Role-specific navigation and content
- Professional UI with icons and color coding
- User-friendly forms with validation feedback

### ✅ Comprehensive Testing
- User model testing (creation, roles, properties)
- Role-based access control testing
- Registration flow testing (both roles)
- Login flow testing with role redirects
- Template rendering testing (role-specific nav)
- Logout functionality testing
- Home page testing

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd project

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 3. Create Sample Data
```bash
# Create sample schools and users for testing
python manage.py create_sample_data
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Home**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/login/
- **Register**: http://127.0.0.1:8000/register/
- **Admin Dashboard**: http://127.0.0.1:8000/administration/
- **Education Dashboard**: http://127.0.0.1:8000/education/

## Test User Credentials

After running `create_sample_data`, you can use these credentials:

### Administration Users
- **Username**: `admin1` | **Password**: `admin123`
- **Username**: `admin2` | **Password**: `admin123`

### Education Users  
- **Username**: `teacher1` | **Password**: `teacher123`
- **Username**: `teacher2` | **Password**: `teacher123`
- **Username**: `teacher3` | **Password**: `teacher123`

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run specific test classes
python manage.py test accounts.tests.UserModelTest
python manage.py test accounts.tests.RoleBasedAccessTest
python manage.py test accounts.tests.RegistrationFlowTest
python manage.py test accounts.tests.LoginFlowTest
python manage.py test accounts.tests.TemplateRenderingTest
python manage.py test accounts.tests.LogoutTest
python manage.py test accounts.tests.HomePageTest
```

## Project Structure

```
project/
├── accounts/
│   ├── migrations/
│   ├── management/commands/
│   ├── templates/
│   │   ├── accounts/
│   │   ├── administration/
│   │   ├── education/
│   │   └── base/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── administration_urls.py
│   ├── education_urls.py
│   └── views.py
├── school_management/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
└── manage.py
```

## Key Implementation Details

### Custom User Model
The `User` model extends `AbstractUser` and adds:
- `role` field with choices: `administration` or `education`
- `school` foreign key (optional for education users, required for admin users)
- `email` field with unique constraint and validation

### Access Control Decorators
- `@admin_required`: Restricts access to administration role users
- `@education_required`: Restricts access to education role users
- Both decorators provide appropriate redirects and flash messages

### Role-Based Redirects
- **Login Redirect**: Users are redirected to their role-specific dashboard after login
- **Access Control**: Users attempting to access wrong department areas are redirected
- **Navigation**: Dynamic navigation shows only role-appropriate options

### Form Validation
- **Registration Form**: Validates role-school relationship (admin users need school)
- **Email Uniqueness**: Prevents duplicate email registration
- **Password Validation**: Uses Django's built-in password validators

### Security Features
- CSRF protection on all forms
- Session-based authentication
- Role-based access control
- Secure password handling
- Email validation

## Database Models

### User Model
- Extends `AbstractUser`
- Fields: `username`, `email`, `first_name`, `last_name`, `role`, `school`
- Properties: `is_admin_user`, `is_education_user`

### School Model  
- Simple school information model
- Fields: `name`, `address`, `created_at`
- Used for admin user school associations

## URL Patterns

- `/` - Home page (redirects authenticated users to their dashboard)
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/administration/` - Admin dashboard (admin role required)
- `/education/` - Education dashboard (education role required)
- `/admin/` - Django admin panel

## Technologies Used

- **Django 6.0** - Web framework
- **SQLite** - Database
- **Bootstrap 5** - Frontend framework
- **Bootstrap Icons** - Icon library
- **Python 3.12** - Programming language

## Development Notes

- This implementation follows Django best practices
- All code includes proper error handling and validation
- Templates are responsive and mobile-friendly
- Comprehensive test coverage for all major flows
- Ready for production deployment with proper settings

## Future Enhancements

- Add more granular permissions within departments
- Implement password strength indicators
- Add two-factor authentication
- Include audit logging for user actions
- Add user profile management
- Implement department-specific features