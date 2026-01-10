from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import SchoolAdminProfile
from .utils import get_school_admin_school


class SchoolAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "school_admin_profile"):
            raise PermissionDenied("Требуется роль администратора школы")
        return super().dispatch(request, *args, **kwargs)

    @property
    def school(self):
        return get_school_admin_school(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("school", self.school)
        return context


class SchoolObjectAccessMixin(SchoolAdminRequiredMixin):
    school_lookup_path: str | None = None

    def has_school_access(self, obj) -> bool:
        if self.school_lookup_path is None:
            raise NotImplementedError

        current = obj
        for attr in self.school_lookup_path.split("__"):
            current = getattr(current, attr)
        return current == self.school

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not self.has_school_access(obj):
            raise PermissionDenied("Нет доступа")
        return obj


class SuccessMessageMixin:
    success_message: str | None = None

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
