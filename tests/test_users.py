from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import Role, Permission, UserRole, RolePermission

User = get_user_model()


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_creation(self):
        """Test user model creation"""
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertTrue(self.user.is_active)
    
    def test_user_str_method(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), self.user_data['username'])


class RoleModelTestCase(TestCase):
    def setUp(self):
        self.role_data = {
            'name': 'ADMIN',
            'description': 'Administrator role',
            'is_active': True
        }
        self.role = Role.objects.create(**self.role_data)
    
    def test_role_creation(self):
        """Test role model creation"""
        self.assertEqual(self.role.name, self.role_data['name'])
        self.assertEqual(self.role.description, self.role_data['description'])
        self.assertTrue(self.role.is_active)
    
    def test_role_str_method(self):
        """Test role string representation"""
        self.assertEqual(str(self.role), self.role_data['name'])


class UserAPITestCase(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create admin role
        self.admin_role = Role.objects.create(name='ADMIN', description='Admin role')
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        
        # Create user role
        self.user_role = Role.objects.create(name='USER', description='User role')
        UserRole.objects.create(user=self.regular_user, role=self.user_role)
    
    def authenticate_as_admin(self):
        """Helper method to authenticate as admin"""
        login_url = reverse('token_obtain_pair')
        login_data = {
            'username': 'admin',
            'password': 'adminpass123'
        }
        login_response = self.client.post(login_url, login_data)
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_get_users_list(self):
        """Test getting users list"""
        self.authenticate_as_admin()
        url = reverse('user-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_user(self):
        """Test creating a new user"""
        self.authenticate_as_admin()
        url = reverse('user-list')
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post(url, user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], user_data['username'])
        self.assertEqual(response.data['email'], user_data['email'])
        self.assertTrue(User.objects.filter(username=user_data['username']).exists())
    
    def test_get_user_detail(self):
        """Test getting user details"""
        self.authenticate_as_admin()
        url = reverse('user-detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)
        self.assertEqual(response.data['email'], self.regular_user.email)
        self.assertIn('USER', response.data['roles'])
    
    def test_assign_role_to_user(self):
        """Test assigning a role to a user"""
        self.authenticate_as_admin()
        
        # Create new role
        new_role = Role.objects.create(name='MANAGER', description='Manager role')
        
        url = reverse('user-assign-role', kwargs={'pk': self.regular_user.pk})
        data = {'role_id': new_role.id}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserRole.objects.filter(user=self.regular_user, role=new_role).exists()
        )
    
    def test_remove_role_from_user(self):
        """Test removing a role from a user"""
        self.authenticate_as_admin()
        
        url = reverse('user-remove-role', kwargs={'pk': self.regular_user.pk})
        data = {'role_id': self.user_role.id}
        
        response = self.client.delete(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserRole.objects.filter(user=self.regular_user, role=self.user_role).exists()
        )