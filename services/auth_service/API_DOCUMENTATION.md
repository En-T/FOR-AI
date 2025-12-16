# Authentication Service API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
The API uses session-based authentication. After logging in, a session cookie (`sessionid`) is set, which should be included in subsequent requests.

## CSRF Protection
All POST endpoints require CSRF token protection. Include the CSRF token from the `csrftoken` cookie in the `X-CSRFToken` header.

---

## Endpoints

### 1. User Registration (API)

**Endpoint:** `POST /accounts/api/register/`

**Description:** Creates a new user account.

**Authentication Required:** No

**Request Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string",
    "role": "school_admin" | "education_department"
}
```

**Success Response (201 Created):**
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

**Error Responses:**

400 Bad Request - Missing fields:
```json
{
    "error": "Username, password, and role are required"
}
```

400 Bad Request - Invalid role:
```json
{
    "error": "Invalid role. Must be school_admin or education_department"
}
```

400 Bad Request - Duplicate username:
```json
{
    "error": "Username already exists"
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/register/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d '{
    "username": "johndoe",
    "password": "securepass123",
    "role": "school_admin"
  }'
```

---

### 2. User Login (API)

**Endpoint:** `POST /accounts/api/login/`

**Description:** Authenticates a user and creates a session.

**Authentication Required:** No

**Request Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Success Response (200 OK):**
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

**Note:** A `sessionid` cookie is set in the response.

**Error Responses:**

400 Bad Request - Missing fields:
```json
{
    "error": "Username and password are required"
}
```

401 Unauthorized - Invalid credentials:
```json
{
    "error": "Invalid credentials"
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -c cookies.txt \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

---

### 3. User Logout (API)

**Endpoint:** `POST /accounts/api/logout/`

**Description:** Logs out the current user and destroys the session.

**Authentication Required:** Yes

**Request Headers:**
```
X-CSRFToken: <csrf_token>
Cookie: sessionid=<session_id>
```

**Success Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

**Error Response:**

403 Forbidden - Not authenticated:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/logout/ \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -b cookies.txt
```

---

### 4. Validate Session

**Endpoint:** `GET /accounts/api/validate-session/`

**Description:** Validates the current session and returns user information if authenticated. This endpoint is particularly useful for other services to validate user sessions.

**Authentication Required:** No (but returns different responses based on authentication status)

**Request Headers:**
```
Cookie: sessionid=<session_id>
```

**Success Response (200 OK) - Authenticated:**
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

**Success Response (200 OK) - Not Authenticated:**
```json
{
    "authenticated": false
}
```

**cURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/accounts/api/validate-session/ \
  -b cookies.txt
```

**Use Case:**
This endpoint is ideal for microservices architecture where other services need to validate user sessions:

```python
# Example: Validating session in another service
import requests

def is_user_authenticated(session_cookie):
    response = requests.get(
        'http://127.0.0.1:8000/accounts/api/validate-session/',
        cookies={'sessionid': session_cookie}
    )
    data = response.json()
    return data.get('authenticated', False), data.get('user')
```

---

### 5. Get Current User

**Endpoint:** `GET /accounts/api/current-user/`

**Description:** Returns detailed information about the currently authenticated user.

**Authentication Required:** Yes

**Request Headers:**
```
Cookie: sessionid=<session_id>
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "role": "school_admin",
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

**Error Response:**

403 Forbidden - Not authenticated:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**cURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/accounts/api/current-user/ \
  -b cookies.txt
```

---

## Web Interface Endpoints

These endpoints return HTML pages for browser-based interactions.

### 6. Registration Form

**Endpoint:** `GET /accounts/register/`

**Description:** Displays the registration form.

**Response:** HTML page with registration form

### 7. Registration Submission

**Endpoint:** `POST /accounts/register/`

**Description:** Submits registration form data.

**Form Fields:**
- `username`: Text input
- `role`: Select dropdown (school_admin or education_department)
- `password1`: Password input
- `password2`: Password confirmation input
- `csrfmiddlewaretoken`: CSRF token (auto-included)

**Success:** Redirects to profile page

---

### 8. Login Form

**Endpoint:** `GET /accounts/login/`

**Description:** Displays the login form.

**Response:** HTML page with login form

### 9. Login Submission

**Endpoint:** `POST /accounts/login/`

**Description:** Submits login form data.

**Form Fields:**
- `username`: Text input
- `password`: Password input
- `csrfmiddlewaretoken`: CSRF token (auto-included)

**Success:** Redirects to profile page

---

### 10. User Profile

**Endpoint:** `GET /accounts/profile/`

**Description:** Displays user profile information.

**Authentication Required:** Yes

**Response:** HTML page with user details

---

### 11. Logout

**Endpoint:** `GET /accounts/logout/`

**Description:** Logs out the user and redirects to login page.

**Authentication Required:** Yes

**Success:** Redirects to login page

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 302 | Redirect (for form submissions) |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (not authenticated) |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse.

---

## Cross-Origin Resource Sharing (CORS)

CORS is not configured by default. If you need to access the API from a different domain, configure CORS in Django settings:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

---

## Integration Examples

### JavaScript/TypeScript Frontend

```javascript
class AuthService {
    constructor(baseURL = 'http://127.0.0.1:8000') {
        this.baseURL = baseURL;
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    async register(username, password, role) {
        const csrfToken = this.getCookie('csrftoken');
        
        const response = await fetch(`${this.baseURL}/accounts/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({ username, password, role })
        });
        
        return response.json();
    }

    async login(username, password) {
        const csrfToken = this.getCookie('csrftoken');
        
        const response = await fetch(`${this.baseURL}/accounts/api/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        return response.json();
    }

    async logout() {
        const csrfToken = this.getCookie('csrftoken');
        
        const response = await fetch(`${this.baseURL}/accounts/api/logout/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'include'
        });
        
        return response.json();
    }

    async validateSession() {
        const response = await fetch(`${this.baseURL}/accounts/api/validate-session/`, {
            credentials: 'include'
        });
        
        return response.json();
    }

    async getCurrentUser() {
        const response = await fetch(`${this.baseURL}/accounts/api/current-user/`, {
            credentials: 'include'
        });
        
        return response.json();
    }
}

// Usage
const authService = new AuthService();

// Register
await authService.register('johndoe', 'securepass123', 'school_admin');

// Login
await authService.login('johndoe', 'securepass123');

// Validate session
const session = await authService.validateSession();
if (session.authenticated) {
    console.log('User is logged in:', session.user);
}

// Get current user
const user = await authService.getCurrentUser();

// Logout
await authService.logout();
```

### Python Backend Service

```python
import requests
from functools import wraps
from flask import request, jsonify

AUTH_SERVICE_URL = 'http://127.0.0.1:8000'

def validate_session(session_cookie):
    """Validate session with auth service"""
    try:
        response = requests.get(
            f'{AUTH_SERVICE_URL}/accounts/api/validate-session/',
            cookies={'sessionid': session_cookie},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                return data.get('user')
        
        return None
    except requests.RequestException:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get('sessionid')
        
        if not session_cookie:
            return jsonify({'error': 'No session cookie'}), 401
        
        user = validate_session(session_cookie)
        
        if not user:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Add user to request context
        request.user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if request.user.get('role') != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

# Usage in Flask routes
@app.route('/api/protected')
@require_auth
def protected_route():
    return jsonify({
        'message': f'Hello {request.user["username"]}',
        'role': request.user['role']
    })

@app.route('/api/admin-only')
@require_role('school_admin')
def admin_only_route():
    return jsonify({
        'message': 'Admin access granted',
        'user': request.user
    })
```

---

## Error Handling Best Practices

When integrating with this service, implement proper error handling:

```javascript
async function loginUser(username, password) {
    try {
        const response = await fetch('http://127.0.0.1:8000/accounts/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle different error scenarios
            if (response.status === 401) {
                throw new Error('Invalid username or password');
            } else if (response.status === 400) {
                throw new Error(data.error || 'Invalid request');
            } else {
                throw new Error('Login failed');
            }
        }

        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}
```

---

## Security Best Practices

1. **Always use HTTPS in production** - Set `SESSION_COOKIE_SECURE = True` in settings
2. **Rotate session keys regularly** - Use Django's session management
3. **Implement rate limiting** - Prevent brute force attacks
4. **Validate all inputs** - The API validates inputs but additional client-side validation helps
5. **Use strong passwords** - Enforce password policies
6. **Monitor authentication attempts** - Log and monitor failed login attempts
7. **Set appropriate session timeouts** - Configure `SESSION_COOKIE_AGE` in settings

---

## Testing the API

Use the provided test suite:

```bash
# Run all tests
python manage.py test accounts

# Run specific test class
python manage.py test accounts.tests.APILoginTestCase

# Run with coverage
coverage run --source='.' manage.py test accounts
coverage report
```

Or test manually with tools like:
- cURL (command line)
- Postman (GUI)
- HTTPie (command line)
- Your application's HTTP client

---

## Support

For issues or questions about the authentication service, refer to the main README.md file or contact the development team.
