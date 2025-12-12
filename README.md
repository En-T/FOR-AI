# Django Rewards System

A comprehensive Django-based rewards management system that allows you to create, manage, and track rewards and rewarded items.

## Features

- **Reward Management**: Create, edit, and delete rewards with customizable points
- **Rewarded Items Tracking**: Track users who claim rewards
- **Filtering & Search**: Advanced filtering capabilities for both rewards and rewarded items
- **Status Management**: Track reward claim status (Pending, Approved, Rejected, Completed)
- **Admin Interface**: Full Django admin integration for easy management
- **Responsive Design**: Mobile-friendly interface with clean, modern design
- **User-Friendly Forms**: Easy-to-use forms for adding and editing data

## Project Structure

```
rewards_project/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── .env.example
├── rewards_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── rewards/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── rewarded/
│   │       ├── index.html
│   │       ├── rewarded.html
│   │       ├── add_reward.html
│   │       ├── add_rewarded.html
│   │       ├── edit.html
│   │       ├── delete_reward.html
│   │       ├── delete_rewarded.html
│   │       └── selection.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── static/
    └── css/
        └── style.css
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd rewards_project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and set your configuration
   # Generate a SECRET_KEY using:
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Managing Rewards

1. **View All Rewards**: Navigate to the home page to see all rewards
2. **Add a Reward**: Click "Add Reward" in the navigation menu
3. **Edit a Reward**: Click the "Edit" button next to any reward
4. **Delete a Reward**: Click the "Delete" button and confirm deletion
5. **Filter Rewards**: Use the filter form to search by name, points, or status

### Managing Rewarded Items

1. **View Rewarded Items**: Click "Rewarded Items" in the navigation
2. **Add a Rewarded Item**: Click "Add Rewarded" and fill in the form
3. **Edit Status**: Click "Edit" to update the status or other details
4. **Delete Rewarded Item**: Click "Delete" and confirm

### Browse Available Rewards

1. Navigate to "Browse Rewards" to see all active rewards
2. Use filters to find specific rewards
3. Click "Claim Reward" to create a rewarded item

## Models

### Reward Model

- `name`: Name of the reward
- `description`: Detailed description
- `points_required`: Points needed to claim
- `is_active`: Active/Inactive status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Rewarded Model

- `reward`: Foreign key to Reward
- `user_name`: Name of the user claiming the reward
- `user_email`: Email address of the user
- `points_used`: Points spent on this reward
- `status`: Current status (Pending, Approved, Rejected, Completed)
- `notes`: Additional notes
- `requested_at`: When the reward was requested
- `processed_at`: When the request was processed

## API Endpoints

| URL | View | Description |
|-----|------|-------------|
| `/` | index | List all rewards |
| `/rewarded/` | rewarded_list | List all rewarded items |
| `/reward/add/` | add_reward | Add new reward |
| `/rewarded/add/` | add_rewarded | Add new rewarded item |
| `/reward/edit/<id>/` | edit_reward | Edit existing reward |
| `/rewarded/edit/<id>/` | edit_rewarded | Edit rewarded item |
| `/reward/delete/<id>/` | delete_reward | Delete reward |
| `/rewarded/delete/<id>/` | delete_rewarded | Delete rewarded item |
| `/selection/` | selection | Browse active rewards |
| `/admin/` | Django Admin | Admin interface |

## Configuration

### Database Configuration

By default, the project uses SQLite. To use PostgreSQL:

1. Update `.env` file:
   ```
   DATABASE_ENGINE=django.db.backends.postgresql
   DATABASE_NAME=your_db_name
   DATABASE_USER=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

2. Install PostgreSQL and create a database:
   ```bash
   createdb your_db_name
   ```

### Environment Variables

See `.env.example` for all available configuration options:
- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Debug mode (default: True)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- Database configuration options

## Testing

Run the test suite:

```bash
python manage.py test
```

Run specific tests:

```bash
python manage.py test rewards.tests.RewardModelTest
```

## Development

### Creating Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

For production:

```bash
python manage.py collectstatic
```

## Production Deployment

1. **Set environment variables:**
   - Set `DEBUG=False`
   - Set appropriate `ALLOWED_HOSTS`
   - Use a strong `SECRET_KEY`

2. **Use a production database** (PostgreSQL recommended)

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Use a production server** (Gunicorn, uWSGI)

5. **Set up a reverse proxy** (Nginx, Apache)

6. **Enable HTTPS**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Authors

- Development Team

## Acknowledgments

- Django framework
- django-filter for advanced filtering
- Bootstrap-inspired CSS design

---

**Version**: 1.0.0  
**Last Updated**: 2024
