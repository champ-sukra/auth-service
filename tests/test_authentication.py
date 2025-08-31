from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import Role, UserRole

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # Create test role
        self.role = Role.objects.create(name='USER', description='Test role')
        UserRole.objects.create(user=self.user, role=self.role)
    
    def test_login_success(self):
        """Test successful login"""
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], self.user_data['username'])
        self.assertIn('USER', response.data['user']['roles'])
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh"""
        # First login to get tokens
        login_url = reverse('token_obtain_pair')
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Test refresh
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        
        response = self.client.post(refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_user_profile_authenticated(self):
        """Test accessing user profile with authentication"""
        # Login and get token
        login_url = reverse('token_obtain_pair')
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(login_url, login_data)
        access_token = login_response.data['access']
        
        # Access profile
        url = reverse('user_profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertIn('USER', response.data['roles'])
    
    def test_user_profile_unauthenticated(self):
        """Test accessing user profile without authentication"""
        url = reverse('user_profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)