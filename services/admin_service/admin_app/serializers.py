"""
Admin App Serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AdminLog, SystemSettings, DashboardMetrics


class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer for admin logs"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = (
            'id', 'user', 'user_username', 'action', 'model_name', 
            'object_id', 'details', 'ip_address', 'user_agent', 
            'created_at'
        )
        read_only_fields = ('id', 'created_at', 'user')


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings"""
    
    class Meta:
        model = SystemSettings
        fields = ('id', 'key', 'value', 'description', 'is_public', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class DashboardMetricsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard metrics"""
    
    class Meta:
        model = DashboardMetrics
        fields = (
            'id', 'date', 'total_users', 'active_users', 'new_registrations',
            'total_requests', 'error_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for user management (admin view)"""
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'is_active', 'date_joined',
            'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')