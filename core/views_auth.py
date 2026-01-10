from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
from .forms import LoginForm
from .models import User, AuditLog
from .auth_utils import log_action

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect_by_role(request.user)
        form = LoginForm()
        return render(request, 'auth/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    log_action(user, AuditLog.ACTION_LOGIN, details="Successful login")
                    messages.success(request, f"Welcome, {user.username}!")
                    return self.redirect_by_role(user)
                else:
                    messages.error(request, "This account is inactive.")
            else:
                # Log failed attempt
                try:
                    u = User.objects.get(username=username)
                    log_action(u, AuditLog.ACTION_LOGIN, details="Failed login attempt: wrong password")
                except User.DoesNotExist:
                    log_action(None, AuditLog.ACTION_LOGIN, details=f"Failed login attempt: user {username} not found")
                
                messages.error(request, "Invalid username or password.")
        return render(request, 'auth/login.html', {'form': form})

    def redirect_by_role(self, user):
        if user.role == User.ROLE_SUPERUSER:
            return redirect('superuser-dashboard')
        elif user.role == User.ROLE_DEPT_EDUCATION:
            return redirect('dashboard') # Or specifically director dashboard if it exists
        elif user.role == User.ROLE_ADMIN_SCHOOL:
            return redirect('dashboard') # Or specifically school admin dashboard if it exists
        return redirect('dashboard')

class LogoutView(View):
    def get(self, request):
        log_action(request.user, AuditLog.ACTION_LOGIN, details="Successful logout")
        logout(request)
        return redirect('login')
