"""
Admin App Admin Configuration
"""
from django.contrib import admin
from .models import AdminLog, SystemSettings, DashboardMetrics


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin interface for AdminLog model"""
    list_display = ('user', 'action', 'model_name', 'object_id', 'created_at', 'ip_address')
    list_filter = ('action', 'created_at', 'user')
    search_fields = ('user__username', 'model_name', 'details')
    readonly_fields = ('created_at', 'user')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False  # Logs are created programmatically
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for SystemSettings model"""
    list_display = ('key', 'value_preview', 'is_public', 'updated_at')
    list_filter = ('is_public', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('key',)
    
    def value_preview(self, obj):
        return obj.value[:50] + ('...' if len(obj.value) > 50 else '')
    value_preview.short_description = 'Value Preview'


@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    """Admin interface for DashboardMetrics model"""
    list_display = ('date', 'total_users', 'new_registrations', 'total_requests', 'error_count')
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser