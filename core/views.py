from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from .models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


@staff_member_required
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if username and password and role:
            user = User.objects.create_user(
                username=username,
                password=password,
                role=role
            )
            messages.success(request, f'Пользователь {username} создан успешно')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля')
    
    return render(request, 'auth/register.html')


@login_required
def dashboard_view(request):
    return HttpResponse(f"Добро пожаловать, {request.user.username}! Ваш роль: {request.user.get_role_display()}")
