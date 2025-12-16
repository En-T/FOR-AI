# Authentication Service

A Django-based authentication and authorization service providing user management with role-based access control for school administration and education department personnel.

## Features

- Custom User model with role-based authentication
- Two role types: `school_admin` and `education_department`
- Username/password authentication
- Session-based authentication
- RESTful API endpoints for service integration
- Django admin interface for user management
- CSRF protection on all forms
- Comprehensive unit tests

## Tech Stack

- Django 4.2
- Django REST Framework 3.14+
- SQLite database
- Python 3.x

## Installation

1. Navigate to the service directory:
```bash
cd services/auth_service
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser account:
```bash
python manage.py createsuperuser
```

When prompted, enter:
- Username: (your desired admin username)
- Role: Choose either `school_admin` or `education_department`
- Password: (secure password)

6. Run the development server:
```bash
python manage.py runserver
```

The service will be available at `http://127.0.0.1:8000/`

## User Roles

The system supports two user roles:

### School Admin (`school_admin`)
- Intended for school administrators
- Manages school-level operations

### Education Department (`education_department`)
- Intended for education department officials
- Manages district or regional operations

## Web Interface

### Registration
- URL: `http://127.0.0.1:8000/accounts/register/`
- Users can self-register by providing:
  - Username
  - Role (school_admin or education_department)
  - Password (with confirmation)

### Login
- URL: `http://127.0.0.1:8000/accounts/login/`
- Existing users can log in with username and password

### Profile
- URL: `http://127.0.0.1:8000/accounts/profile/`
- Displays user information (requires authentication)

### Admin Panel
- URL: `http://127.0.0.1:8000/admin/`
- Access Django admin interface for user management (superuser only)

## API Endpoints

All API endpoints return JSON responses and support CSRF protection via session cookies.

### 1. Register User
**POST** `/accounts/api/register/`

Creates a new user account.

Request body:
```json
{
    "username": "johndoe",
    "password": "securepass123",
    "role": "school_admin"
}
```

Response (201 Created):
```json
{
    "message": "User created successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "role": "school_admin"
    }
}
```

### 2. Login
**POST** `/accounts/api/login/`

Authenticates a user and creates a session.

Request body:
```json
{
    "username": "johndoe",
    "password": "securepass123"
}
```

Response (200 OK):
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "johndoe",
        "role": "school_admin"
    }
}
```

### 3. Logout
**POST** `/accounts/api/logout/`

Logs out the current user (requires authentication).

Response (200 OK):
```json
{
    "message": "Logout successful"
}
```

### 4. Validate Session
**GET** `/accounts/api/validate-session/`

Validates the current session and returns user information if authenticated.

Response (200 OK) - Authenticated:
```json
{
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "johndoe",
        "role": "school_admin",
        "is_staff": false
    }
}
```

Response (200 OK) - Not Authenticated:
```json
{
    "authenticated": false
}
```

### 5. Current User
**GET** `/accounts/api/current-user/`

Returns detailed information about the currently authenticated user (requires authentication).

Response (200 OK):
```json
{
    "id": 1,
    "username": "johndoe",
    "role": "school_admin",
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

## Integration with Other Services

Other services can integrate with this authentication service to validate user sessions and authenticate requests.

### Session-Based Authentication

The auth service uses Django's session framework with cookie-based sessions. To integrate:

1. **Session Validation**: Other services should call the `/accounts/api/validate-session/` endpoint to validate user sessions. Include the session cookie in the request.

2. **Cookie Forwarding**: When a user makes a request to your service, forward the session cookie to the auth service for validation.

Example integration flow:
```
User Request → Your Service → Auth Service (validate-session) → Response
                     ↓
              Process based on user info
```

### Example Integration Code

Python example using requests:
```python
import requests

def validate_user_session(session_cookie):
    """Validate user session with auth service"""
    response = requests.get(
        'http://127.0.0.1:8000/accounts/api/validate-session/',
        cookies={'sessionid': session_cookie}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('authenticated'):
            return data.get('user')
    
    return None

def my_protected_view(request):
    """Example protected view in your service"""
    session_cookie = request.COOKIES.get('sessionid')
    user = validate_user_session(session_cookie)
    
    if not user:
        return {'error': 'Unauthorized'}, 401
    
    return {'message': f'Hello {user["username"]}'}
```

JavaScript example:
```javascript
async function validateSession() {
    const response = await fetch(
        'http://127.0.0.1:8000/accounts/api/validate-session/',
        {
            credentials: 'include'  // Include cookies
        }
    );
    
    const data = await response.json();
    return data.authenticated ? data.user : null;
}
```

### CSRF Protection

For POST requests to the auth service, you need to include a CSRF token:

1. Get the CSRF token from the cookie (Django sets `csrftoken` cookie)
2. Include it in the `X-CSRFToken` header

Example:
```javascript
async function login(username, password) {
    const csrfToken = getCookie('csrftoken');
    
    const response = await fetch(
        'http://127.0.0.1:8000/accounts/api/login/',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        }
    );
    
    return response.json();
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
```

## Running Tests

Run all unit tests:
```bash
python manage.py test accounts
```

Run specific test class:
```bash
python manage.py test accounts.tests.UserModelTestCase
```

Run with verbose output:
```bash
python manage.py test accounts --verbosity=2
```

## Database

The service uses SQLite by default. The database file (`db.sqlite3`) is created in the project root after running migrations.

For production, configure a more robust database in `auth_service/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_db',
        'USER': 'auth_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Security Considerations

1. **Secret Key**: Change the `SECRET_KEY` in settings.py for production
2. **Debug Mode**: Set `DEBUG = False` in production
3. **Allowed Hosts**: Configure `ALLOWED_HOSTS` in production
4. **HTTPS**: Use `SESSION_COOKIE_SECURE = True` when using HTTPS
5. **Password Validation**: Django's password validators are enabled by default

## Creating Initial Superuser Accounts

### Using Command Line
```bash
python manage.py createsuperuser
```

### Using Django Shell
```bash
python manage.py shell
```

```python
from accounts.models import User

# Create superuser
admin = User.objects.create_superuser(
    username='admin',
    password='admin123',
    role=User.EDUCATION_DEPARTMENT
)

# Create regular users
user1 = User.objects.create_user(
    username='school_admin1',
    password='pass123',
    role=User.SCHOOL_ADMIN
)

user2 = User.objects.create_user(
    username='dept_user1',
    password='pass123',
    role=User.EDUCATION_DEPARTMENT
)
```

### Using Admin Interface

1. Create a superuser using command line
2. Access admin panel at `http://127.0.0.1:8000/admin/`
3. Log in with superuser credentials
4. Navigate to "Users" section
5. Click "Add User" to create new users with appropriate roles

## Troubleshooting

### Migration Issues
If you encounter migration errors:
```bash
python manage.py makemigrations accounts
python manage.py migrate accounts
```

### Session Issues
Clear all sessions:
```bash
python manage.py clearsessions
```

### Database Reset
To reset the database (WARNING: deletes all data):
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Development

To extend the service:

1. **Add new user fields**: Modify `accounts/models.py`
2. **Add new endpoints**: Update `accounts/views.py` and `accounts/urls.py`
3. **Add new permissions**: Use Django's permission system
4. **Add new roles**: Update `ROLE_CHOICES` in User model

## License

This is an internal service for educational institution management.
