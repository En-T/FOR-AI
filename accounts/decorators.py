from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(required_role):
    """
    Decorator to restrict access to users with a specific role.
    
    Args:
        required_role (str): The role required to access the view ('administration' or 'education')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            
            # Check if user has the required role
            if user.role == required_role:
                return view_func(request, *args, **kwargs)
            else:
                # Determine appropriate message based on user's current role
                if user.role == 'administration':
                    if required_role == 'education':
                        message = "Access denied. Administration department cannot access Education areas."
                    else:
                        message = "Access denied. You don't have permission to access this area."
                elif user.role == 'education':
                    if required_role == 'administration':
                        message = "Access denied. Education department cannot access Administration areas."
                    else:
                        message = "Access denied. You don't have permission to access this area."
                else:
                    message = "Access denied. Invalid user role."
                
                messages.error(request, message)
                
                # Redirect to appropriate area based on user's role
                if user.role == 'administration':
                    return redirect('administration:dashboard')
                elif user.role == 'education':
                    return redirect('education:dashboard')
                else:
                    return redirect('accounts:login')
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator to restrict access to users with 'administration' role only.
    """
    return role_required('administration')(view_func)


def education_required(view_func):
    """
    Decorator to restrict access to users with 'education' role only.
    """
    return role_required('education')(view_func)