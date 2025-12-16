"""
Auth Service Tests
"""
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class AuthServiceHealthCheckTest(TestCase):
    """Test auth service health endpoint"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'auth_service')


class AuthServiceRegistrationTest(APITestCase):
    """Test user registration"""
    
    def test_user_registration(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)


class AuthServiceLoginTest(APITestCase):
    """Test user login"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login(self):
        """Test successful user login"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)