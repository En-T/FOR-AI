from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from accounts.models import School


User = get_user_model()


class UserModelTest(TestCase):
    """Test the custom User model"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
    
    def test_user_creation_admin_role(self):
        """Test creating a user with administration role"""
        user = User.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='administration',
            school=self.school
        )
        
        self.assertEqual(user.role, 'administration')
        self.assertEqual(user.school, self.school)
        self.assertTrue(user.is_admin_user)
        self.assertFalse(user.is_education_user)
        self.assertFalse(user.is_staff)  # Should be False by default for regular users
        self.assertTrue(user.is_active)
    
    def test_user_creation_education_role(self):
        """Test creating a user with education role"""
        user = User.objects.create_user(
            username='eduser',
            email='education@test.com',
            first_name='Education',
            last_name='User',
            password='edpass123',
            role='education'
        )
        
        self.assertEqual(user.role, 'education')
        self.assertIsNone(user.school)
        self.assertFalse(user.is_admin_user)
        self.assertTrue(user.is_education_user)
    
    def test_user_str_representation(self):
        """Test the string representation of User model"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='administration'
        )
        self.assertEqual(str(user), 'testuser (Administration)')


class RoleBasedAccessTest(TestCase):
    """Test role-based access control"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='administration',
            school=self.school
        )
        self.education_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            first_name='Education',
            last_name='User',
            password='teacherpass123',
            role='education'
        )
    
    def test_admin_access_to_admin_dashboard(self):
        """Test that admin users can access administration dashboard"""
        client = Client()
        client.login(username='admin', password='adminpass123')
        response = client.get('/administration/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration Dashboard')
    
    def test_education_access_to_education_dashboard(self):
        """Test that education users can access education dashboard"""
        client = Client()
        client.login(username='teacher', password='teacherpass123')
        response = client.get('/education/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Education Dashboard')
    
    def test_admin_redirect_from_education_dashboard(self):
        """Test that admin users are redirected from education dashboard"""
        client = Client()
        client.login(username='admin', password='adminpass123')
        response = client.get('/education/', follow=True)
        
        # Should be redirected to admin dashboard
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration Dashboard')
    
    def test_education_redirect_from_admin_dashboard(self):
        """Test that education users are redirected from admin dashboard"""
        client = Client()
        client.login(username='teacher', password='teacherpass123')
        response = client.get('/administration/', follow=True)
        
        # Should be redirected to education dashboard
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Education Dashboard')
    
    def test_unauthorized_access_redirected_to_login(self):
        """Test that unauthorized users are redirected to login"""
        client = Client()
        response = client.get('/administration/', follow=True)
        
        # Should be redirected to login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')


class RegistrationFlowTest(TestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
    
    def test_admin_registration(self):
        """Test registration of admin user"""
        client = Client()
        registration_data = {
            'username': 'newadmin',
            'email': 'newadmin@test.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password1': 'adminpass123',
            'password2': 'adminpass123',
            'role': 'administration',
            'school': self.school.id
        }
        
        response = client.post('/register/', registration_data)
        
        # Should redirect to home after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        user = User.objects.get(username='newadmin')
        self.assertEqual(user.role, 'administration')
        self.assertEqual(user.school, self.school)
    
    def test_education_registration(self):
        """Test registration of education user"""
        client = Client()
        registration_data = {
            'username': 'newteacher',
            'email': 'newteacher@test.com',
            'first_name': 'New',
            'last_name': 'Teacher',
            'password1': 'teacherpass123',
            'password2': 'teacherpass123',
            'role': 'education'
        }
        
        response = client.post('/register/', registration_data)
        
        # Should redirect to home after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        user = User.objects.get(username='newteacher')
        self.assertEqual(user.role, 'education')
        self.assertIsNone(user.school)
    
    def test_admin_registration_requires_school(self):
        """Test that admin registration fails without school selection"""
        client = Client()
        registration_data = {
            'username': 'newadmin',
            'email': 'newadmin@test.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password1': 'adminpass123',
            'password2': 'adminpass123',
            'role': 'administration'
            # No school selected
        }
        
        response = client.post('/register/', registration_data)
        
        # Should show form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'School selection is required')
    
    def test_duplicate_email_registration_fails(self):
        """Test that duplicate email registration fails"""
        # Create a user with this email first
        User.objects.create_user(
            username='existing',
            email='test@test.com',
            password='testpass123',
            role='education'
        )
        
        client = Client()
        registration_data = {
            'username': 'newuser',
            'email': 'test@test.com',  # Duplicate email
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'education'
        }
        
        response = client.post('/register/', registration_data)
        
        # Should show form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')


class LoginFlowTest(TestCase):
    """Test login functionality with role-based redirect"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='administration',
            school=self.school
        )
        self.education_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            first_name='Education',
            last_name='User',
            password='teacherpass123',
            role='education'
        )
    
    def test_admin_login_redirects_to_admin_dashboard(self):
        """Test that admin login redirects to administration dashboard"""
        client = Client()
        login_data = {
            'username': 'admin',
            'password': 'adminpass123'
        }
        
        response = client.post('/login/', login_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration Dashboard')
    
    def test_education_login_redirects_to_education_dashboard(self):
        """Test that education login redirects to education dashboard"""
        client = Client()
        login_data = {
            'username': 'teacher',
            'password': 'teacherpass123'
        }
        
        response = client.post('/login/', login_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Education Dashboard')
    
    def test_invalid_login_shows_error(self):
        """Test that invalid login shows error message"""
        client = Client()
        login_data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        
        response = client.post('/login/', login_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')


class TemplateRenderingTest(TestCase):
    """Test that templates render correctly with role-specific navigation"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='administration',
            school=self.school
        )
        self.education_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            first_name='Education',
            last_name='User',
            password='teacherpass123',
            role='education'
        )
    
    def test_admin_nav_contains_admin_links(self):
        """Test that admin users see administration links in navigation"""
        client = Client()
        client.login(username='admin', password='adminpass123')
        response = client.get('/administration/')
        
        self.assertEqual(response.status_code, 200)
        # Admin user should see administration navigation links
        self.assertContains(response, 'Administration')
        self.assertContains(response, 'nav-link')
    
    def test_education_nav_contains_education_links(self):
        """Test that education users see education links in navigation"""
        client = Client()
        client.login(username='teacher', password='teacherpass123')
        response = client.get('/education/')
        
        self.assertEqual(response.status_code, 200)
        # Education user should see education navigation links
        self.assertContains(response, 'Education')
        self.assertContains(response, 'nav-link')
    
    def test_logged_in_user_sees_logout_in_nav(self):
        """Test that logged-in users see logout option in navigation"""
        client = Client()
        client.login(username='admin', password='adminpass123')
        response = client.get('/administration/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, 'Login')  # Should not see login link
    
    def test_logged_out_user_sees_login_in_nav(self):
        """Test that logged-out users see login and register links"""
        client = Client()
        response = client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')


class LogoutTest(TestCase):
    """Test logout functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
            role='education'
        )
    
    def test_logout_redirects_to_login(self):
        """Test that logout redirects to login page"""
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        response = client.get('/logout/', follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')


class HomePageTest(TestCase):
    """Test home page functionality"""
    
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='123 Test Street'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123',
            role='administration',
            school=self.school
        )
    
    def test_unauthenticated_user_sees_login_register(self):
        """Test that unauthenticated users see login and register options"""
        client = Client()
        response = client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
    
    def test_authenticated_admin_redirected_to_admin_dashboard(self):
        """Test that authenticated admin is redirected to admin dashboard"""
        client = Client()
        client.login(username='admin', password='adminpass123')
        response = client.get('/', follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administration Dashboard')