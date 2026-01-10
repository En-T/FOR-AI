from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponseForbidden
from .models import User, AuditLog, School, Class, Student, Teacher

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return HttpResponseForbidden("You don't have permission to access this page.")


class DirectorEducationRequiredMixin(RoleRequiredMixin):
    """Mixin to check if user is Director of Education"""
    allowed_roles = [User.ROLE_DEPT_EDUCATION]


def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != User.ROLE_SUPERUSER:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def log_action(user, action_type, model_name=None, object_id=None, details=None):
    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        model_name=model_name,
        object_id=object_id,
        details=details
    )


def get_director_schools(user):
    """
    Получить все школы, созданные Director of Education.
    """
    if user.is_authenticated and user.role == User.ROLE_DEPT_EDUCATION:
        return School.objects.filter(created_by=user)
    return School.objects.none()


def get_director_users(user):
    """
    Получить всех пользователей (School Administrator) школ Director of Education.
    """
    if user.is_authenticated and user.role == User.ROLE_DEPT_EDUCATION:
        schools = School.objects.filter(created_by=user)
        return User.objects.filter(school__in=schools).exclude(
            role=User.ROLE_SUPERUSER
        ).exclude(role=User.ROLE_DEPT_EDUCATION)
    return User.objects.none()


def get_director_statistics(user):
    """
    Получить статистику для Director of Education.
    """
    if user.is_authenticated and user.role == User.ROLE_DEPT_EDUCATION:
        schools = School.objects.filter(created_by=user)
        return {
            'total_schools': schools.count(),
            'total_classes': Class.objects.filter(school__in=schools).count(),
            'total_students': Student.objects.filter(school_class__school__in=schools).count(),
            'total_teachers': Teacher.objects.filter(school__in=schools).count(),
        }
    return {
        'total_schools': 0,
        'total_classes': 0,
        'total_students': 0,
        'total_teachers': 0,
    }
