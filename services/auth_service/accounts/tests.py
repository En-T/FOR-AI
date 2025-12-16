from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import User


class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, User.SCHOOL_ADMIN)
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            role=User.EDUCATION_DEPARTMENT
        )
        self.assertEqual(user.username, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_str(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )
        self.assertEqual(str(user), 'testuser')

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='testpass123', role=User.SCHOOL_ADMIN)


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_user_login(self):
        logged_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(logged_in)

    def test_user_login_wrong_password(self):
        logged_in = self.client.login(username='testuser', password='wrongpass')
        self.assertFalse(logged_in)


class RegistrationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_view_post_valid(self):
        data = {
            'username': 'newuser',
            'role': User.SCHOOL_ADMIN,
            'password1': 'newpass123!@#',
            'password2': 'newpass123!@#',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_password_mismatch(self):
        data = {
            'username': 'newuser',
            'role': User.SCHOOL_ADMIN,
            'password1': 'newpass123',
            'password2': 'differentpass123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_post_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_invalid(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)


class APIRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_register_url = reverse('accounts:api_register')

    def test_api_register_valid(self):
        data = {
            'username': 'apiuser',
            'password': 'apipass123',
            'role': User.SCHOOL_ADMIN,
        }
        response = self.client.post(
            self.api_register_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='apiuser').exists())
        self.assertIn('user', response.json())

    def test_api_register_missing_fields(self):
        data = {
            'username': 'apiuser',
        }
        response = self.client.post(
            self.api_register_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_register_invalid_role(self):
        data = {
            'username': 'apiuser',
            'password': 'apipass123',
            'role': 'invalid_role',
        }
        response = self.client.post(
            self.api_register_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_register_duplicate_username(self):
        User.objects.create_user(
            username='apiuser',
            password='apipass123',
            role=User.SCHOOL_ADMIN
        )
        data = {
            'username': 'apiuser',
            'password': 'newpass123',
            'role': User.EDUCATION_DEPARTMENT,
        }
        response = self.client.post(
            self.api_register_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APILoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_login_url = reverse('accounts:api_login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_api_login_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(
            self.api_login_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.json())

    def test_api_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass',
        }
        response = self.client.post(
            self.api_login_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_login_missing_fields(self):
        data = {
            'username': 'testuser',
        }
        response = self.client.post(
            self.api_login_url,
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APIValidateSessionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_validate_url = reverse('accounts:api_validate_session')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_validate_session_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_validate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['authenticated'])
        self.assertIn('user', data)

    def test_validate_session_unauthenticated(self):
        response = self.client.get(self.api_validate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertFalse(data['authenticated'])


class APILogoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_logout_url = reverse('accounts:api_logout')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_api_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.api_logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APICurrentUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_current_user_url = reverse('accounts:api_current_user')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=User.SCHOOL_ADMIN
        )

    def test_current_user_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['role'], User.SCHOOL_ADMIN)

    def test_current_user_unauthenticated(self):
        response = self.client.get(self.api_current_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
