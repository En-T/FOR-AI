from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator, validate_email


class School(models.Model):
    """Model representing a school"""
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('administration', 'Administration'),
        ('education', 'Education'),
    ]
    
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='education',
        help_text='User role determining department access'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='School associated with the user (for admin users)'
    )
    email = models.EmailField(
        validators=[validate_email],
        unique=True,
        help_text='User email address (required and must be unique)'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin_user(self):
        """Check if user has administration role"""
        return self.role == 'administration'
    
    @property
    def is_education_user(self):
        """Check if user has education role"""
        return self.role == 'education'