"""
Targeted tests for specific missing lines.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

@pytest.fixture(autouse=True)
def disable_limiter():
    """Disable rate limiter for all tests."""
    with patch('flask_limiter.Limiter.limit') as mock_limit:
        mock_limit.return_value = lambda f: f
        yield

class TestMissingLines:
    """Tests targeting specific missing lines."""
    
    def test_role_required_insufficient_permissions_lines_135_137(self, app):
        """Test role_required decorator when user lacks permissions - lines 135-137."""
        
        # Mock login_required to pass through at the module level
        with patch('flask_login.login_required', lambda f: f):
            
            with app.test_client() as client:
                
                # Mock current_user with insufficient role
                with patch('flask_login.current_user') as mock_user:
                    mock_user.is_authenticated = True
                    mock_user.role = 'admin'  # Not 'super_admin'
                    
                    # Access the settings route which requires super_admin
                    response = client.get('/settings')
                    
                    # The response should be a redirect (302) due to insufficient permissions
                    # This should hit lines 135-137
                    assert response.status_code == 302
                    
                    # Check that it redirects to dashboard
                    assert '/dashboard' in response.location or 'dashboard' in str(response.location)
    
    def test_login_route_authenticated_user_redirect_line_195(self, app):
        """Test login route when user is already authenticated - line 195."""
        with app.test_client() as client:
            
            # Mock authenticated user
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                
                # Access login route while already authenticated
                response = client.get('/login')
                
                # Should redirect to dashboard (line 195)
                assert response.status_code == 302
    
    def test_logout_route_lines_221_224(self, app):
        """Test logout route - lines 221-224."""
        
        # Mock login_required to pass through
        with patch('flask_login.login_required', lambda f: f):
            
            with app.test_client() as client:
                
                with patch('app.log_action') as mock_log_action, \
                     patch('flask_login.logout_user') as mock_logout_user:
                    
                    # Access logout route
                    response = client.get('/logout')
                    
                    # Should hit line 221: log_action('logout')
                    mock_log_action.assert_called_with('logout')
                    
                    # Should hit line 222: logout_user()
                    mock_logout_user.assert_called_once()
                    
                    # Should redirect to login (lines 223-224)
                    assert response.status_code == 302
    
    def test_load_user_function_lines_124_127(self, app):
        """Test load_user function - lines 124-127."""
        with app.app_context():
            from app import load_user, ADMIN_USERS
            
            # Test with existing user (lines 124-126)
            if ADMIN_USERS:
                username = list(ADMIN_USERS.keys())[0]
                user = load_user(username)
                assert user is not None
                assert user.username == username
            
            # Test with non-existent user (line 127)
            user = load_user('nonexistent_user')
            assert user is None
    
    def test_login_failed_authentication_lines_213_214(self, app):
        """Test login with failed authentication - lines 213-214."""
        with app.test_client() as client:
            
            with patch('app.log_action') as mock_log_action:
                
                # Test with wrong credentials
                response = client.post('/login', data={
                    'username': 'nonexistent_user',
                    'password': 'wrong_password',
                    'csrf_token': 'dummy'  # Add CSRF token
                })
                
                # Should hit lines 213-214 (failed login logging)
                # The exact call depends on the implementation
                assert mock_log_action.called
