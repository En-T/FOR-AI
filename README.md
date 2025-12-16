# Django Bootstrap (Django 4.x)

This repository contains a minimal Django 4.x project scaffold with a `core` app for shared utilities.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database migrations

```bash
python manage.py migrate
```

## Run the development server

```bash
python manage.py runserver
```

Open:
- Home: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health/ (returns `{ "status": "ok" }`)
- Admin: http://127.0.0.1:8000/admin/

Optional:

```bash
python manage.py createsuperuser
```

## Static / media

- Project templates live in `templates/`.
- Static assets live in `static/`.
- Uploaded media will be stored in `media/` (served by Django only when `DEBUG=1`).

To collect static files for production-like runs:

```bash
python manage.py collectstatic
```
