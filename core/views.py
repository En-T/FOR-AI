from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                request.session['user_id'] = user.id
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials or inactive account')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials')

    return render(request, 'auth/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not request.session.get('user_id'):
            return HttpResponseForbidden('Only for superuser')

        try:
            user = User.objects.get(username=username)
            messages.error(request, 'Username already exists')
        except User.DoesNotExist:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            new_user.save()
            messages.success(request, 'User created successfully')
            return redirect('dashboard')

    return render(request, 'auth/register.html')
