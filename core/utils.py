import logging
from django.utils import timezone
from .models import AuditLog

logger = logging.getLogger(__name__)


def log_action(user, action, model, object_id=None, details=None):
    """
    Log an action to the AuditLog model and file logger.
    
    Args:
        user: User object (can be None)
        action: Action type (CREATE, UPDATE, DELETE, LOGIN, VIEW)
        model: Name of the model being acted upon
        object_id: ID of the object (optional)
        details: Additional details as a dictionary (optional)
    """
    # Log to database
    AuditLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=object_id,
        details=details or {}
    )
    
    # Log to file
    user_str = user.username if user else 'Anonymous'
    details_str = str(details) if details else ''
    logger.info(
        f'{action} - {model} - User: {user_str} - Object ID: {object_id} - Details: {details_str}'
    )


def log_login(user):
    """Log user login."""
    log_action(
        user=user,
        action=AuditLog.Action.LOGIN,
        model='User',
        object_id=user.id,
        details={'username': user.username}
    )


def log_create(user, model_name, object_id, details=None):
    """Log object creation."""
    log_action(
        user=user,
        action=AuditLog.Action.CREATE,
        model=model_name,
        object_id=object_id,
        details=details
    )


def log_update(user, model_name, object_id, details=None):
    """Log object update."""
    log_action(
        user=user,
        action=AuditLog.Action.UPDATE,
        model=model_name,
        object_id=object_id,
        details=details
    )


def log_delete(user, model_name, object_id, details=None):
    """Log object deletion."""
    log_action(
        user=user,
        action=AuditLog.Action.DELETE,
        model=model_name,
        object_id=object_id,
        details=details
    )


def log_view(user, model_name, object_id, details=None):
    """Log object view."""
    log_action(
        user=user,
        action=AuditLog.Action.VIEW,
        model=model_name,
        object_id=object_id,
        details=details
    )
