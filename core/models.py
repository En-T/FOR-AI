from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = 'SUPERUSER', 'Superuser'
        DIRECTOR_OF_EDUCATION = 'DIRECTOR_OF_EDUCATION', 'Director of Education'
        SCHOOL_ADMINISTRATOR = 'SCHOOL_ADMINISTRATOR', 'School Administrator'

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.SCHOOL_ADMINISTRATOR,
        verbose_name='Роль'
    )
    school = models.ForeignKey(
        'main.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Школа'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()
        return self.username


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        LOGIN = 'LOGIN', 'Login'
        VIEW = 'VIEW', 'View'

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name='Действие'
    )
    model = models.CharField(
        max_length=100,
        verbose_name='Модель'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID объекта'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время'
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Детали'
    )

    class Meta:
        verbose_name = 'Лог аудита'
        verbose_name_plural = 'Логи аудита'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model', '-timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f'{self.timestamp} - {user_str} - {self.action} - {self.model} (ID: {self.object_id})'
