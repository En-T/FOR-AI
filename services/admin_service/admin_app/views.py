"""
Admin App Views
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json

from .models import AdminLog, SystemSettings, DashboardMetrics
from .serializers import (
    AdminLogSerializer, SystemSettingsSerializer, 
    DashboardMetricsSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """Health check endpoint for admin service"""
    return Response({
        'status': 'healthy',
        'service': 'admin_service',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


class DashboardView(APIView):
    """Admin dashboard with system metrics"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get dashboard metrics"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User metrics
        total_users = User.objects.count()
        new_users_this_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_users_this_month = User.objects.filter(date_joined__gte=month_ago).count()
        
        # Activity metrics
        recent_logs = AdminLog.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # System settings count
        total_settings = SystemSettings.objects.count()
        
        data = {
            'users': {
                'total': total_users,
                'new_this_week': new_users_this_week,
                'new_this_month': new_users_this_month,
            },
            'activity': {
                'logs_this_week': recent_logs,
            },
            'system': {
                'total_settings': total_settings,
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return Response(data)


class AdminLogListView(generics.ListAPIView):
    """List admin activity logs"""
    queryset = AdminLog.objects.select_related('user')
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None  # Could implement pagination if needed
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by action type if provided
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
            
        # Filter by user if provided
        user = self.request.query_params.get('user', None)
        if user:
            queryset = queryset.filter(user__username=user)
            
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
            
        return queryset[:100]  # Limit to most recent 100 logs


class SystemSettingsView(APIView):
    """System settings management"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get all public settings (or all if admin)"""
        if request.user.is_superuser:
            settings = SystemSettings.objects.all()
        else:
            settings = SystemSettings.objects.filter(is_public=True)
            
        serializer = SystemSettingsSerializer(settings, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new setting"""
        serializer = SystemSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SystemSettingDetailView(APIView):
    """Individual setting management"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def put(self, request, key):
        """Update setting"""
        try:
            setting = SystemSettings.objects.get(key=key)
        except SystemSettings.DoesNotExist:
            return Response(
                {'error': 'Setting not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = SystemSettingsSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, key):
        """Delete setting"""
        try:
            setting = SystemSettings.objects.get(key=key)
            setting.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SystemSettings.DoesNotExist:
            return Response(
                {'error': 'Setting not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MetricsView(APIView):
    """Dashboard metrics management"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get metrics for date range"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        queryset = DashboardMetrics.objects.all()
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        serializer = DashboardMetricsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new metrics entry"""
        serializer = DashboardMetricsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """Detailed health check for all services"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Return detailed system health information"""
        from django.db import connection
        from django.core.cache import cache
        
        health_data = {
            'service': 'admin_service',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        # Database health
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['checks']['database'] = {'status': 'healthy', 'response_time': 'OK'}
        except Exception as e:
            health_data['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
            
        # Cache health
        try:
            cache.set('health_check', 'ok', 10)
            cached_value = cache.get('health_check')
            health_data['checks']['cache'] = {'status': 'healthy' if cached_value else 'unhealthy'}
        except Exception as e:
            health_data['checks']['cache'] = {'status': 'unhealthy', 'error': str(e)}
            
        # Disk space check
        import os
        try:
            statvfs = os.statvfs('/')
            free_space = statvfs.f_frsize * statvfs.f_bavail
            health_data['checks']['disk_space'] = {
                'status': 'healthy' if free_space > 1024*1024*100 else 'warning',
                'free_bytes': free_space
            }
        except Exception as e:
            health_data['checks']['disk_space'] = {'status': 'unknown', 'error': str(e)}
            
        return Response(health_data)