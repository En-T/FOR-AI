# Education Management System

A microservices-based platform for managing educational institutions.

## Services

### Authentication Service
Located in `services/auth_service/`

A Django-based authentication and authorization service providing user management with role-based access control.

**Features:**
- Custom User model with role-based authentication
- Two role types: `school_admin` and `education_department`
- Session-based authentication
- RESTful API endpoints for service integration
- Django admin interface for user management
- Comprehensive unit tests

**Quick Start:**
```bash
cd services/auth_service
./setup.sh
```

For detailed documentation, see:
- [Auth Service README](services/auth_service/README.md)
- [API Documentation](services/auth_service/API_DOCUMENTATION.md)

## Requirements

- Python 3.x
- pip
- virtualenv

## Getting Started

1. Clone the repository
2. Navigate to the desired service directory
3. Follow the service-specific setup instructions

## Architecture

This project follows a microservices architecture where each service is independent and self-contained. Services communicate with each other via RESTful APIs.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

## License

Internal project for educational institution management.
