"""
Education Service Tests
"""
from django.test import TestCase, Client
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class EducationServiceHealthCheckTest(TestCase):
    """Test education service health endpoint"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'education_service')


class EducationServiceCoursesTest(APITestCase):
    """Test course endpoints"""
    
    def test_course_list_access(self):
        """Test course list endpoint access"""
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, 200)
    
    def test_popular_courses_access(self):
        """Test popular courses endpoint"""
        response = self.client.get('/api/v1/courses/popular/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)  # DRF pagination