# Django Microservices Architecture

This project implements a microservices architecture using Django, providing three distinct services for authentication, administration, and education functionality.

## 🏗️ Architecture Overview

The system consists of three independent Django microservices, each running in its own container with its own database:

### Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / API Gateway               │
│                     (nginx/caddy - optional)                │
└─────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┼───────────────┐
        │               │           │               │
    ┌───▼───┐      ┌───▼────┐   ┌───▼───┐      ┌───▼────┐
    │ Auth  │      │ Admin  │   │Educa- │      │ Redis  │
    │Service│      │ Service│   │ tion  │      │ Cache  │
    │ 8001  │      │  8002  │   │Service│      │ 6379   │
    │       │      │        │   │  8003 │      │        │
    │SQLite │      │ SQLite │   │ SQLite│      │        │
    └───────┘      └────────┘   └───────┘      └────────┘
```

### Service Responsibilities

#### 🔐 Auth Service (Port 8001)
**Purpose**: User authentication and authorization management

**Key Features**:
- User registration and login
- JWT token generation and validation
- User profile management
- Password hashing and validation
- Session management
- User verification

**Endpoints**:
- `POST /api/v1/register/` - User registration
- `POST /api/v1/login/` - User authentication
- `POST /api/v1/logout/` - User logout
- `GET /api/v1/profile/` - Get user profile
- `PUT /api/v1/profile/` - Update user profile
- `GET /api/v1/users/` - List all users (admin)
- `GET /health/` - Health check

#### 🛠️ Admin Service (Port 8002)
**Purpose**: System administration and monitoring

**Key Features**:
- Admin dashboard with system metrics
- Activity logging and audit trails
- System settings management
- User management interface
- Dashboard analytics
- Health monitoring across services

**Endpoints**:
- `GET /api/v1/dashboard/` - Admin dashboard metrics
- `GET /api/v1/logs/` - Admin activity logs
- `GET /api/v1/settings/` - System settings
- `POST /api/v1/settings/` - Create setting
- `PUT /api/v1/settings/{key}/` - Update setting
- `GET /api/v1/health-check/` - Detailed health check
- `GET /health/` - Health check

#### 🎓 Education Service (Port 8003)
**Purpose**: Educational content management and analytics

**Key Features**:
- Course and lesson management
- Student enrollment and progress tracking
- Assessment and quiz functionality
- Learning analytics and reporting
- Student progress monitoring
- Popular courses recommendation

**Endpoints**:
- `GET /api/v1/courses/` - List courses
- `GET /api/v1/courses/{id}/` - Course details
- `POST /api/v1/courses/create/` - Create course
- `GET /api/v1/courses/{id}/lessons/` - Course lessons
- `POST /api/v1/enroll/{course_id}/` - Enroll in course
- `GET /api/v1/progress/` - Student progress
- `GET /api/v1/analytics/` - Learning analytics
- `GET /health/` - Health check

### Shared Infrastructure

#### Redis Cache
- **Purpose**: Caching, session storage, and Celery broker
- **Port**: 6379
- **Usage**: 
  - Session management
  - Cache for frequently accessed data
  - Celery message broker
  - Rate limiting

#### Docker Network
- **Network**: `microservices_network`
- **Type**: Bridge network
- **Purpose**: Inter-service communication

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Create environment file
cp .env.example .env

# Optionally edit .env with your custom settings
```

### 2. Build and Run
```bash
# Build and start all services
docker compose up --build

# Run in detached mode
docker compose up --build -d

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f auth_service
```

### 3. Verify Services
```bash
# Check service health
curl http://localhost:8001/health/
curl http://localhost:8002/health/
curl http://localhost:8003/health/

# Check Redis
redis-cli -h localhost -p 6379 ping
```

### 4. Create Superuser
```bash
# Create admin user for Auth Service
docker compose exec auth_service python manage.py createsuperuser

# Create admin user for Admin Service
docker compose exec admin_service python manage.py createsuperuser

# Create admin user for Education Service
docker compose exec education_service python manage.py createsuperuser
```

## 📋 Database Operations

### Migrations
```bash
# Run migrations for all services
docker compose exec auth_service python manage.py makemigrations
docker compose exec auth_service python manage.py migrate

docker compose exec admin_service python manage.py makemigrations
docker compose exec admin_service python manage.py migrate

docker compose exec education_service python manage.py makemigrations
docker compose exec education_service python manage.py migrate

# Or run migrations on startup (already configured in docker-compose.yml)
```

### Database Access
```bash
# Access Auth Service database
docker compose exec auth_service python manage.py dbshell

# Access Admin Service database  
docker compose exec admin_service python manage.py dbshell

# Access Education Service database
docker compose exec education_service python manage.py dbshell

# Backup databases
docker compose exec auth_service sqlite3 auth_db.sqlite3 ".backup /app/backup_auth.db"
docker compose exec admin_service sqlite3 admin_db.sqlite3 ".backup /app/backup_admin.db"
docker compose exec education_service sqlite3 education_db.sqlite3 ".backup /app/backup_education.db"
```

## 🧪 Testing

### Running Tests
```bash
# Run tests for Auth Service
docker compose exec auth_service python manage.py test

# Run tests for Admin Service
docker compose exec admin_service python manage.py test

# Run tests for Education Service
docker compose exec education_service python manage.py test

# Run tests with coverage
docker compose exec auth_service python -m pytest --cov=auth_app
docker compose exec admin_service python -m pytest --cov=admin_app  
docker compose exec education_service python -m pytest --cov=education_app
```

### Test Endpoints
```bash
# Test Auth Service endpoints
curl -X POST http://localhost:8001/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# Test Admin Service dashboard
curl -H "Authorization: Bearer <token>" http://localhost:8002/api/v1/dashboard/

# Test Education Service courses
curl http://localhost:8003/api/v1/courses/
```

## 🛠️ Development Workflow

### Local Development
```bash
# Run individual service locally (without Docker)
cd services/auth_service
python manage.py runserver 8001

cd services/admin_service  
python manage.py runserver 8002

cd services/education_service
python manage.py runserver 8003
```

### Code Quality
```bash
# Format code (if black is configured)
docker compose exec auth_service black .
docker compose exec admin_service black .
docker compose exec education_service black .

# Lint code (if flake8 is configured)  
docker compose exec auth_service flake8 .
docker compose exec admin_service flake8 .
docker compose exec education_service flake8 .

# Check imports
docker compose exec auth_service isort --check-only .
docker compose exec admin_service isort --check-only .
docker compose exec education_service isort --check-only .
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | `dev-secret-key` | Django secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0` | Allowed hosts |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:8080` | CORS origins |

### Service-Specific Settings

#### Auth Service
- `JWT_SECRET_KEY`: Secret for JWT token generation
- `JWT_ALGORITHM`: Algorithm for JWT tokens (default: HS256)
- `JWT_EXPIRATION_DELTA`: Token expiration time in seconds

#### Admin Service  
- `ADMIN_EMAIL`: Default admin email
- `ADMIN_PASSWORD`: Default admin password

#### Education Service
- `EDUCATION_API_KEY`: API key for education features
- `ANALYTICS_CACHE_TIMEOUT`: Cache timeout for analytics data

## 📊 Monitoring and Logging

### Service Health Checks
Each service provides a `/health/` endpoint that returns:
```json
{
  "status": "healthy",
  "service": "auth_service",
  "version": "1.0.0"
}
```

### Admin Service Health Check
The admin service provides detailed health monitoring:
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/api/v1/health-check/
```

### Log Management
```bash
# View real-time logs
docker compose logs -f

# View logs for specific service
docker compose logs -f auth_service

# View logs with timestamps
docker compose logs -t -f auth_service

# Export logs
docker compose logs auth_service > auth_logs.txt
```

## 🔒 Security Considerations

### Production Deployment
1. **Change Default Secrets**: Update all `SECRET_KEY`, `JWT_SECRET_KEY` values
2. **Disable Debug Mode**: Set `DJANGO_DEBUG=False`
3. **Configure HTTPS**: Use SSL/TLS certificates
4. **Database Security**: Use PostgreSQL/MySQL instead of SQLite
5. **Redis Security**: Configure Redis authentication
6. **CORS Configuration**: Restrict allowed origins
7. **Rate Limiting**: Implement rate limiting for APIs
8. **Security Headers**: Add security headers to responses

### API Security
- JWT tokens for authentication
- CORS protection configured
- Django's built-in security middleware
- Password validation and hashing
- SQL injection protection through ORM

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Run production services
docker compose -f docker-compose.prod.yml up -d

# Scale services (if needed)
docker compose up --scale auth_service=3
```

### Environment-Specific Configurations
Create environment-specific Docker Compose files:
- `docker-compose.yml` - Development
- `docker-compose.staging.yml` - Staging
- `docker-compose.prod.yml` - Production

## 📚 API Documentation

### REST API Documentation
Each service uses Django REST Framework with Spectacular for API documentation:

- **Auth Service**: `http://localhost:8001/api/v1/schema/swagger-ui/`
- **Admin Service**: `http://localhost:8002/api/v1/schema/swagger-ui/`
- **Education Service**: `http://localhost:8003/api/v1/schema/swagger-ui/`

### Postman Collection
Import the Postman collection (when available) for testing all endpoints.

## 🤝 Contributing

1. Follow the established code structure
2. Create migrations for model changes
3. Write tests for new features
4. Update documentation
5. Follow PEP 8 style guidelines

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Change ports in docker-compose.yml or stop conflicting services
docker compose down
docker compose up --build
```

#### Database Issues
```bash
# Reset databases
docker compose exec auth_service rm auth_db.sqlite3
docker compose exec admin_service rm admin_db.sqlite3  
docker compose exec education_service rm education_db.sqlite3

# Restart services to recreate databases
docker compose restart
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x manage.py
```

#### Redis Connection Issues
```bash
# Check Redis status
docker compose exec redis redis-cli ping

# View Redis logs
docker compose logs redis
```

#### Service Not Responding
```bash
# Check service logs
docker compose logs auth_service

# Restart specific service
docker compose restart auth_service

# Rebuild and restart
docker compose up --build --force-recreate auth_service
```

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check existing documentation
- Review service logs for error details