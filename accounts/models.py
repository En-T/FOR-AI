from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    SCHOOL_ADMIN = 'school_admin', 'School Administrator'
    EDUCATION_DEPT = 'education_dept', 'Education Department'


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.SCHOOL_ADMIN,
        verbose_name='User Role'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_school_admin(self):
        return self.role == UserRole.SCHOOL_ADMIN

    @property
    def is_education_dept(self):
        return self.role == UserRole.EDUCATION_DEPT