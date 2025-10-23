from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class LogoutTestCase(TestCase):
    """Test cases for user logout functionality"""
    
    def setUp(self):
        """Create a test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout_redirects_to_home(self):
        """Test that logout redirects to home page"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')
        
        # Verify user is logged in
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # Logout using POST request
        response = self.client.post(reverse('logout'))
        
        # Check redirect to home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        
        # Verify user is logged out
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_logout_requires_post(self):
        """Test that logout only accepts POST requests"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')
        
        # Try to logout with GET request (should fail)
        response = self.client.get(reverse('logout'))
        
        # Should return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
        
        # Verify user is still logged in
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
