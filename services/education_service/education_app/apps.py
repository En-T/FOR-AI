"""
Education App Configuration
"""
from django.apps import AppConfig


class EducationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'education_app'
    verbose_name = 'Education Service'