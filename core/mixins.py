from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class SuperuserRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DirectorEducationRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_superuser or 
                request.user.role == request.user.Role.DIRECTOR_OF_EDUCATION):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SchoolAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_superuser or 
                request.user.role == request.user.Role.SCHOOL_ADMINISTRATOR or
                request.user.role == request.user.Role.DIRECTOR_OF_EDUCATION):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
