from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from django.contrib.auth.models import AnonymousUser, User

_current_user: ContextVar[Optional[User]] = ContextVar("current_user", default=None)


def set_current_user(user: User | AnonymousUser | None) -> None:
    if user is None or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        _current_user.set(None)
        return

    _current_user.set(user)


def get_current_user() -> Optional[User]:
    return _current_user.get()
