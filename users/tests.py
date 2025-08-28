from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration functionality."""

    def setUp(self):
        cache.clear()  # Clear cache to avoid throttling issues in tests
        self.registration_url = reverse('user-register')
        self.valid_payload = {
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'securepassword123'
        }
        self.invalid_payload = {
            'full_name': '',
            'email': 'invalid-email',
            'password': '123'
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.registration_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that response contains expected fields
        self.assertIn('email', response.data)
        self.assertIn('full_name', response.data)
        self.assertEqual(response.data['email'], self.valid_payload['email'])
        self.assertEqual(response.data['full_name'], self.valid_payload['full_name'])
        
        # Check that id is present (it should be auto-generated)
        self.assertIn('id', response.data)
        self.assertIsInstance(response.data['id'], int)

        # Verify user was created in database
        user = User.objects.get(email=self.valid_payload['email'])
        self.assertEqual(user.full_name, self.valid_payload['full_name'])
        self.assertTrue(user.check_password(self.valid_payload['password']))

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails."""
        # Create first user
        User.objects.create_user(
            email=self.valid_payload['email'],
            full_name=self.valid_payload['full_name'],
            password=self.valid_payload['password']
        )

        # Try to register with same email
        response = self.client.post(self.registration_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_data(self):
        """Test registration with invalid data fails."""
        response = self.client.post(self.registration_url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('full_name', response.data)

    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields."""
        incomplete_payload = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.registration_url, incomplete_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)


class UserLoginTestCase(APITestCase):
    """Test cases for user login functionality."""

    def setUp(self):
        cache.clear()  # Clear cache to avoid throttling issues in tests
        self.login_url = reverse('user-login')
        # Create user using the custom manager
        self.user = User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='testpassword123'
        )
        self.valid_credentials = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.invalid_credentials = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

    def test_user_login_success(self):
        """Test successful user login."""
        response = self.client.post(self.login_url, self.valid_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Verify token is valid
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        self.assertTrue(access_token)
        self.assertTrue(refresh_token)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials fails."""
        response = self.client.post(self.login_url, self.invalid_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user fails."""
        credentials = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_missing_fields(self):
        """Test login with missing fields."""
        incomplete_credentials = {
            'email': 'test@example.com'
        }
        response = self.client.post(self.login_url, incomplete_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordTestCase(APITestCase):
    """Test cases for forgot password functionality."""

    def setUp(self):
        cache.clear()  # Clear cache to avoid throttling issues in tests
        self.forgot_password_url = reverse('forgot-password')
        self.user = User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='testpassword123'
        )
        self.valid_payload = {
            'email': 'test@example.com'
        }
        self.invalid_payload = {
            'email': 'nonexistent@example.com'
        }

    def test_forgot_password_success(self):
        """Test successful forgot password request."""
        response = self.client.post(self.forgot_password_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reset_token', response.data)

        # Verify token was stored in cache
        token = response.data['reset_token']
        cached_user_id = cache.get(f'pwd-reset-{token}')
        self.assertIsNotNone(cached_user_id)
        self.assertEqual(cached_user_id, self.user.pk)

    def test_forgot_password_nonexistent_user(self):
        """Test forgot password with nonexistent user."""
        response = self.client.post(self.forgot_password_url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'User not found.')

    def test_forgot_password_invalid_email(self):
        """Test forgot password with invalid email format."""
        invalid_payload = {
            'email': 'invalid-email-format'
        }
        response = self.client.post(self.forgot_password_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_forgot_password_missing_email(self):
        """Test forgot password with missing email."""
        response = self.client.post(self.forgot_password_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class ResetPasswordTestCase(APITestCase):
    """Test cases for password reset functionality."""

    def setUp(self):
        cache.clear()  # Clear cache to avoid throttling issues in tests
        self.reset_password_url = reverse('reset-password')
        self.user = User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='oldpassword123'
        )
        self.valid_token = '123456'
        self.new_password = 'newpassword123'

        # Set up valid token in cache
        cache.set(f'pwd-reset-{self.valid_token}', self.user.pk, timeout=3600)

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    def test_reset_password_success(self):
        """Test successful password reset."""
        payload = {
            'token': self.valid_token,
            'new_password': self.new_password
        }
        response = self.client.post(self.reset_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Password reset successful.')

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

        # Verify token was deleted from cache
        cached_user_id = cache.get(f'pwd-reset-{self.valid_token}')
        self.assertIsNone(cached_user_id)

    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token."""
        payload = {
            'token': 'invalid-token',
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid or expired token.')

    def test_reset_password_expired_token(self):
        """Test password reset with expired token."""
        # Set token with immediate expiration
        expired_token = 'expired123'
        cache.set(f'pwd-reset-{expired_token}', self.user.pk, timeout=0)

        payload = {
            'token': expired_token,
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid or expired token.')

    def test_reset_password_missing_fields(self):
        """Test password reset with missing fields."""
        incomplete_payload = {
            'token': self.valid_token
        }
        response = self.client.post(self.reset_password_url, incomplete_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_reset_password_invalid_data(self):
        """Test password reset with invalid data."""
        invalid_payload = {
            'token': '',
            'new_password': ''
        }
        response = self.client.post(self.reset_password_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertIn('new_password', response.data)
