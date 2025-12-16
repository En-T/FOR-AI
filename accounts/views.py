from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import RegistrationForm, LoginForm
from .models import UserRole


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_template_names(self):
        if self.request.user.is_school_admin:
            return ['school_dashboard.html']
        elif self.request.user.is_education_dept:
            return ['education_dashboard.html']
        return ['dashboard.html']


class UserRegistrationView(TemplateView):
    template_name = 'registration/register.html'

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm


class UserLogoutView(LogoutView):
    next_page = 'login'


@login_required
def school_admin_required(request):
    """View to demonstrate school admin restriction."""
    if not request.user.is_school_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return render(request, 'school_admin_only.html')


@login_required
def education_dept_required(request):
    """View to demonstrate education department restriction."""
    if not request.user.is_education_dept:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return render(request, 'education_dept_only.html')