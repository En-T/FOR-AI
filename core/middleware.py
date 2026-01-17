from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from django.contrib.auth.models import AnonymousUser

from core.current_user import set_current_user
from core.models import UserProfile

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("core")


class CurrentUserMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = request.user

        if user and not isinstance(user, AnonymousUser) and user.is_authenticated:
            set_current_user(user)
        else:
            set_current_user(None)

        response = self.get_response(request)
        set_current_user(None)

        return response


class RoleCheckMiddleware:
    EXEMPT_PATHS = [
        "/admin/",
        "/login/",
        "/logout/",
        "/static/",
        "/media/",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            response = self.get_response(request)
            return response

        path = request.path

        if any(path.startswith(exempt_path) for exempt_path in self.EXEMPT_PATHS):
            response = self.get_response(request)
            return response

        if request.user.is_superuser:
            response = self.get_response(request)
            return response

        try:
            profile = UserProfile.objects.get(user=request.user)
            request.user_profile = profile
        except UserProfile.DoesNotExist:
            logger.warning(
                f"Пользователь {request.user.username} не имеет профиля, создаем профиль по умолчанию"
            )
            profile = UserProfile.objects.create(user=request.user, role=UserProfile.ROLE_SCHOOL_ADMIN)
            request.user_profile = profile

        response = self.get_response(request)
        return response
