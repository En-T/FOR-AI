# School Management System - Backend Implementation

## Overview

Complete backend implementation for a multi-role school management system built with Django 4.x. The system supports three user roles: Superuser, Education Department, and School Administrator with comprehensive CRUD operations and business logic.

## Architecture

### Technology Stack
- **Framework**: Django 4.2+
- **Database**: SQLite (development-ready)
- **Forms**: django-crispy-forms with Bootstrap 4
- **Authentication**: Django built-in with custom User model
- **Logging**: File-based logging + Database audit trails
- **Template Engine**: Django Templates

### Project Structure

```
school_management/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── logs/                          # Log files directory
│   └── app.log                    # Application logs
├── school_management/             # Project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
└── schools/                      # Main application
    ├── __init__.py
    ├── apps.py                   # App configuration
    ├── admin.py                  # Django admin configuration
    ├── models.py                 # Database models (10 models)
    ├── views.py                  # Class-based views (43 views)
    ├── forms.py                  # Django forms
    ├── mixins.py                 # Permission mixins
    ├── urls.py                   # URL routing
    └── utils.py                  # Helper functions
```

## User Roles

### 1. Superuser (Администратор системы)
- Full system access
- System statistics dashboard
- User management for all roles
- Log file monitoring

### 2. Education Department (Отдел образования)
- Manage multiple schools
- School CRUD operations
- User management for school admins
- Global subject management
- Cross-school statistics

### 3. School Administrator (Администратор школы)
- Manage single school (owned school only)
- Class management (CRUD)
- Student management (CRUD)
- Teacher management (CRUD)
- Teacher assignments with subgroup logic
- Grade journal management
- Student distribution to subgroups
- School-specific statistics

## Database Models

### 1. User Model
- Custom user model with email as username
- Role-based permissions (superuser, education_dept, school_admin)
- Full name support with patronymic (отчество)

### 2. School
- School information (name, director, graduation class, location)
- Linked to education department admin
- Statistics calculation methods

### 3. Teacher
- Teacher personal information
- Linked to school
- Assignment tracking

### 4. Subject
- Global subjects for all schools
- Used across all classes

### 5. ClassGroup
- School classes (e.g., "5А", "10")
- Student count and average grade annotations

### 6. Student
- Student personal information
- Linked to class
- Grade tracking
- Average calculation methods

### 7. ClassSubjectGroup
- Teacher assignments to subjects in classes
- Supports subgroups (multiple teachers per subject)
- Level tracking (basic/advanced)

### 8. StudentSubjectGroup
- Links students to subject groups
- Handles student distribution across subgroups

### 9. Grade
- Quarterly grades (q1, q2, q3, q4, exam, year, final)
- Validates grades (1-10)
- Automatic average calculations

### 10. AuditLog
- Comprehensive action logging
- Actor, action, model, object_id, details
- IP address tracking
- Timestamp tracking

## Key Features

### 1. Teacher Assignment Logic
- **Single Teacher**: Creates one group with all students
- **Second Teacher**: Automatically creates second group, requires student distribution
- **Multiple Teachers**: Maintains subgroups with distribution management

### 2. Student Distribution System
- Transfer-box interface for moving students between groups
- Prevents duplicate assignments
- Handles all edge cases

### 3. Grade Management
- Table-based grade entry for entire class
- Quarterly, exam, yearly, and final grades
- Automatic average calculations
- Validation (1-10 range)

### 4. Statistics System
- Student averages by quarter
- Class average calculations
- School-wide statistics
- System-wide statistics for superuser

### 5. Security & Permissions
- Role-based access control
- School ownership verification
- Object-level permissions
- CSRF protection
- Secure password handling

## URL Structure

### Superuser URLs
```
/superuser/ - Dashboard
/superuser/users/ - User list
/superuser/users/add/ - Add user
/superuser/logs/ - View logs
```

### Education Department URLs
```
/education-dept/ - Dashboard
/education-dept/schools/ - School list
/education-dept/schools/add/ - Add school
/education-dept/schools/<id>/ - School detail
/education-dept/schools/<id>/update/ - Update school
/education-dept/schools/<id>/delete/ - Delete school
/education-dept/users/ - User list
/education-dept/users/add/ - Add user
/education-dept/users/<id>/ - User detail
/education-dept/users/<id>/update/ - Update user
/education-dept/users/<id>/change-password/ - Change password
/education-dept/users/<id>/delete/ - Delete user
/education-dept/subjects/ - Subject list
/education-dept/subjects/add/ - Add subject
/education-dept/subjects/<id>/delete/ - Delete subject
```

### School Admin URLs
```
/school-admin/ - Profile
/school-admin/profile/update/ - Update profile
/school-admin/change-password/ - Change password
/school-admin/classes/ - Class list
/school-admin/classes/add/ - Add class
/school-admin/classes/<id>/ - Class detail
/school-admin/classes/<id>/update/ - Update class
/school-admin/classes/<id>/delete/ - Delete class
/school-admin/classes/<id>/students/add/ - Add student to class
/school-admin/classes/<id>/assign-teacher/ - Assign teacher
/school-admin/classes/<id>/journal/ - Grade journal
/school-admin/classes/<id>/distribute/<subject_id>/ - Distribute students
/school-admin/students/ - Student list
/school-admin/students/add/ - Add student
/school-admin/students/<id>/ - Student detail
/school-admin/students/<id>/update/ - Update student
/school-admin/students/<id>/delete/ - Delete student
/school-admin/teachers/ - Teacher list
/school-admin/teachers/add/ - Add teacher
/school-admin/teachers/<id>/ - Teacher detail
/school-admin/teachers/<id>/update/ - Update teacher
/school-admin/teachers/<id>/delete/ - Delete teacher
/school-admin/teachers/<id>/assign/ - Assign teacher
/school-admin/assignments/<id>/delete/ - Delete assignment
```

## Helper Functions

### Statistics Functions
- `get_student_average_by_quarter()` - Student average for specific quarter
- `get_class_average()` - Class average across all students
- `get_school_average()` - School-wide average
- `calculate_statistics()` - Comprehensive school statistics
- `get_system_statistics()` - System-wide statistics for superuser

### Teacher Assignment Functions
- `get_class_subject_groups()` - Get subject assignments for class with subgroup info
- `get_teacher_assignments()` - Get all assignments for teacher

### Logging Function
- `log_action()` - Centralized logging to both file and database

### Log Parsing
- `parse_log_file()` - Parse and display log files with search

## Security Features

1. **Permission Mixins**
   - `SuperuserRequiredMixin`
   - `EducationDeptRequiredMixin`
   - `SchoolAdminRequiredMixin`
   - `SchoolOwnerRequiredMixin`
   - `ClassOwnerRequiredMixin`
   - `StudentOwnerRequiredMixin`
   - `TeacherOwnerRequiredMixin`

2. **Access Control**
   - School admins can only access their school
   - Education department can only access their schools
   - Superuser can access everything
   - Object-level permission checks

3. **Form Security**
   - CSRF protection enabled
   - Input validation
   - Secure password handling
   - Admin password change without old password requirement

## Database Configuration

SQLite database configured for development. For production, update `DATABASES` setting in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_management',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Logging Configuration

Logs are written to two destinations:
1. **File**: `logs/app.log` - Application-level logging
2. **Database**: `AuditLog` model - User action tracking

Log format: `{levelname} {asctime} {module} {message}`

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd school_management
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

## Testing

Run the built-in Django test suite:
```bash
python manage.py test
```

## API Documentation

All views accept standard HTTP requests:
- **GET**: Retrieve data, forms
- **POST**: Create objects, submit forms
- **PUT/PATCH**: Update objects (via POST with UpdateView)
- **DELETE**: Remove objects (via POST with DeleteView)

### Example: Creating a Student
```http
POST /school-admin/students/add/
Content-Type: application/x-www-form-urlencoded

class_group=1&first_name=Иван&last_name=Иванов&patronymic=Иванович
```

### Example: Grade Journal Submission
```http
POST /school-admin/classes/1/journal/
Content-Type: application/x-www-form-urlencoded

grade_1_1_q1=5&grade_1_1_q2=4&grade_1_1_q3=5&grade_2_1_q1=4...
```

## Performance Optimization

1. **Database Queries**
   - `select_related()` for ForeignKey relationships
   - `prefetch_related()` for ManyToMany relationships
   - `annotate()` for aggregations

2. **Caching Opportunities**
   - Statistics can be cached and invalidated on changes
   - Teacher assignments cached per class
   - Student averages cached per quarter

## Future Enhancements

1. **Performance**: Add Redis caching for statistics
2. **API**: Django REST Framework for mobile apps
3. **Frontend**: React/Vue integration
4. **Notifications**: Email notifications for important actions
5. **Reports**: PDF report generation for grades and statistics
6. **Import/Export**: Bulk data import from Excel/CSV
7. **Advanced Analytics**: Trend analysis, performance graphs

## Support

For issues and questions:
1. Check Django logs in `logs/app.log`
2. Review database logs in Admin panel (AuditLog)
3. Enable DEBUG mode in settings for detailed error pages

## License

This is a proprietary school management system backend implementation.

---

**Total Implementation**: 10 models, 43 views, 15 forms, 7 mixins, comprehensive utility functions, complete URL routing, permission system, and business logic for multi-role school management.