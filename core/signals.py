from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from core.current_user import get_current_user
from core.models import AuditLog, ClassSubjectGroup, UserProfile

logger = logging.getLogger("core")


def _to_json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, models.Model):
        return value.pk

    return value


def _serialize_instance(instance: models.Model) -> dict[str, Any]:
    data: dict[str, Any] = {}

    for field in instance._meta.fields:
        name = field.name
        raw_value = getattr(instance, name)

        if isinstance(field, models.ForeignKey):
            data[name] = raw_value.pk if raw_value is not None else None
        else:
            data[name] = _to_json_value(raw_value)

    return data


@receiver(post_save, sender=User)
def ensure_user_profile(sender: type[User], instance: User, created: bool, **kwargs: Any) -> None:
    profile, _ = UserProfile.objects.get_or_create(user=instance)

    if instance.is_superuser and profile.role != UserProfile.ROLE_SUPERUSER:
        profile.role = UserProfile.ROLE_SUPERUSER
        profile.save(update_fields=["role"])


@receiver(user_logged_in)
def log_user_logged_in(sender: type[User], request, user: User, **kwargs: Any) -> None:
    logger.info("login user=%s", user.username)


@receiver(user_logged_out)
def log_user_logged_out(sender: type[User], request, user: User, **kwargs: Any) -> None:
    if user is not None:
        logger.info("logout user=%s", user.username)


@receiver(pre_save)
def audit_pre_save(sender: type[models.Model], instance: models.Model, **kwargs: Any) -> None:
    if getattr(sender, "_meta", None) is None:
        return

    if sender._meta.app_label != "core" or sender is AuditLog:
        return

    if instance.pk is None:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:  # type: ignore[attr-defined]
        return

    instance._audit_old_data = _serialize_instance(old_instance)  # type: ignore[attr-defined]


@receiver(post_save)
def audit_post_save(
    sender: type[models.Model], instance: models.Model, created: bool, **kwargs: Any
) -> None:
    if getattr(sender, "_meta", None) is None:
        return

    if sender._meta.app_label != "core" or sender is AuditLog:
        return

    user = get_current_user()
    new_data = _serialize_instance(instance)

    if created:
        action = AuditLog.ACTION_CREATE
        details = {"new": new_data}
    else:
        action = AuditLog.ACTION_UPDATE
        old_data: dict[str, Any] = getattr(instance, "_audit_old_data", {})

        old_changed: dict[str, Any] = {}
        new_changed: dict[str, Any] = {}
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                old_changed[key] = old_value
                new_changed[key] = new_value

        details = {"old": old_changed, "new": new_changed}

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=sender.__name__,
        object_id=int(instance.pk),
        details=details,
    )

    logger.info(
        "audit %s model=%s id=%s user=%s",
        action,
        sender.__name__,
        instance.pk,
        getattr(user, "username", None),
    )


@receiver(post_delete)
def audit_post_delete(sender: type[models.Model], instance: models.Model, **kwargs: Any) -> None:
    if getattr(sender, "_meta", None) is None:
        return

    if sender._meta.app_label != "core" or sender is AuditLog:
        return

    user = get_current_user()
    old_data = _serialize_instance(instance)

    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_DELETE,
        model_name=sender.__name__,
        object_id=int(instance.pk),
        details={"old": old_data},
    )

    logger.info(
        "audit %s model=%s id=%s user=%s",
        AuditLog.ACTION_DELETE,
        sender.__name__,
        instance.pk,
        getattr(user, "username", None),
    )


@receiver(m2m_changed, sender=ClassSubjectGroup.teachers.through)
def audit_teachers_m2m(
    sender: type[models.Model],
    instance: ClassSubjectGroup,
    action: str,
    pk_set: set[int] | None,
    **kwargs: Any,
) -> None:
    if action not in {"post_add", "post_remove", "post_clear"}:
        return

    user = get_current_user()

    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_UPDATE,
        model_name=instance.__class__.__name__,
        object_id=int(instance.pk),
        details={
            "m2m": {
                "field": "teachers",
                "action": action,
                "pks": sorted(pk_set) if pk_set else [],
            }
        },
    )

    logger.info(
        "audit %s model=%s id=%s user=%s m2m_action=%s",
        AuditLog.ACTION_UPDATE,
        instance.__class__.__name__,
        instance.pk,
        getattr(user, "username", None),
        action,
    )
