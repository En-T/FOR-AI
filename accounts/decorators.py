from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def school_admin_required(view_func):
    """Decorator to restrict access to school administrators only."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_school_admin:
            messages.error(request, 'You do not have permission to access this page. School administrator access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def education_dept_required(view_func):
    """Decorator to restrict access to education department users only."""
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_education_dept:
            messages.error(request, 'You do not have permission to access this page. Education department access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class SchoolAdminRequiredMixin:
    """Mixin to restrict access to school administrators only."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_school_admin:
            messages.error(request, 'You do not have permission to access this page. School administrator access required.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class EducationDeptRequiredMixin:
    """Mixin to restrict access to education department users only."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_education_dept:
            messages.error(request, 'You do not have permission to access this page. Education department access required.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)