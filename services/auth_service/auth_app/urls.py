"""
Auth App URL Configuration
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check_view, name='health'),
    
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]