from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseForbidden
from django.urls import reverse
from .forms import RegistrationForm, CustomAuthenticationForm
from .decorators import role_required, admin_required, education_required
from .models import User, School


def home(request):
    """Home page with login/register links"""
    if request.user.is_authenticated:
        # Redirect authenticated users to their role-specific dashboard
        if request.user.role == 'administration':
            return redirect('administration:dashboard')
        elif request.user.role == 'education':
            return redirect('education:dashboard')
    
    return render(request, 'accounts/home.html')


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the user in after registration
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Redirect to role-specific dashboard
            if user.role == 'administration':
                messages.success(request, f"Welcome to the Administration department, {user.first_name}!")
                return redirect('administration:dashboard')
            elif user.role == 'education':
                messages.success(request, f"Welcome to the Education department, {user.first_name}!")
                return redirect('education:dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view with role-based redirect"""
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        
        if user.role == 'administration':
            messages.success(self.request, f"Welcome back, {user.first_name}!")
            return reverse('administration:dashboard')
        elif user.role == 'education':
            messages.success(self.request, f"Welcome back, {user.first_name}!")
            return reverse('education:dashboard')
        else:
            messages.error(self.request, "Invalid user role.")
            return reverse('accounts:login')


@login_required
def user_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('accounts:login')


@admin_required
def administration_dashboard(request):
    """Administration department dashboard"""
    admin_users = User.objects.filter(role='administration').count()
    education_users = User.objects.filter(role='education').count()
    total_schools = School.objects.count()
    total_users = admin_users + education_users
    
    context = {
        'admin_users': admin_users,
        'education_users': education_users,
        'total_schools': total_schools,
        'total_users': total_users,
        'user_school': request.user.school,
    }
    
    return render(request, 'administration/dashboard.html', context)


@education_required
def education_dashboard(request):
    """Education department dashboard"""
    context = {
        'total_education_users': User.objects.filter(role='education').count(),
        'admin_users': User.objects.filter(role='administration').count(),
    }
    
    return render(request, 'education/dashboard.html', context)