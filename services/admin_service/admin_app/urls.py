"""
Admin App URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check_view, name='health'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Admin logs
    path('logs/', views.AdminLogListView.as_view(), name='admin-logs'),
    
    # System settings
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    path('settings/<str:key>/', views.SystemSettingDetailView.as_view(), name='setting-detail'),
    
    # Metrics
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
    
    # Health check
    path('health-check/', views.HealthCheckView.as_view(), name='health-check'),
]