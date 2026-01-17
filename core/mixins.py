from __future__ import annotations

from typing import ClassVar, Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from core.models import UserProfile


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: ClassVar[Iterable[str]] = ()

    def test_func(self) -> bool:
        user = self.request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        profile = getattr(user, "profile", None)
        if profile is None:
            return False

        return profile.role in set(self.allowed_roles)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class SuperuserOnlyMixin(RoleRequiredMixin):
    allowed_roles: ClassVar[Iterable[str]] = (UserProfile.ROLE_SUPERUSER,)

    def test_func(self) -> bool:
        return bool(self.request.user.is_authenticated and self.request.user.is_superuser)


class EducationDeptOnlyMixin(RoleRequiredMixin):
    allowed_roles: ClassVar[Iterable[str]] = (UserProfile.ROLE_EDUCATION_DEPT,)


class SchoolAdminOnlyMixin(RoleRequiredMixin):
    allowed_roles: ClassVar[Iterable[str]] = (UserProfile.ROLE_SCHOOL_ADMIN,)
