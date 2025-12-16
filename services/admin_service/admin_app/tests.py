"""
Admin Service Tests
"""
from django.test import TestCase, Client
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class AdminServiceHealthCheckTest(TestCase):
    """Test admin service health endpoint"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'admin_service')


class AdminServiceDashboardTest(APITestCase):
    """Test admin dashboard functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_dashboard_access(self):
        """Test dashboard endpoint for admin user"""
        response = self.client.get('/api/v1/dashboard/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('users', data)
        self.assertIn('activity', data)
        self.assertIn('system', data)