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
    
    def test_redis_connection_failure_lines_62_63(self, app):
        """Test Redis connection failure - lines 62-63."""
        # We need to test this by importing the module with Redis failing
        with patch('redis.Redis') as mock_redis_class:
            # Make Redis constructor raise an exception
            mock_redis_class.side_effect = Exception("Redis connection failed")
            
            # Import the module (this will trigger the Redis connection attempt)
            import importlib
            import app as app_module
            importlib.reload(app_module)
            
            # The redis_client should be None due to the exception (lines 62-63)
            assert app_module.redis_client is None
    
    def test_login_failed_authentication_lines_213_214(self, app):
        """Test login with failed authentication - lines 213-214."""
        with app.test_client() as client:
            
            with patch('app.log_action') as mock_log_action:
                
                # Test with wrong credentials - this should hit lines 213-214
                response = client.post('/login', data={
                    'username': 'nonexistent_user',
                    'password': 'wrong_password'
                })
                
                # Should hit line 213: log_action('login_failed', f'Username: {username}')
                # Should hit line 214: flash('Invalid username or password.', 'error')
                mock_log_action.assert_called_with('login_failed', 'Username: nonexistent_user')
                
                # Should return to login page
                assert response.status_code == 200
    
    def test_login_successful_authentication_lines_199_211(self, app):
        """Test successful login - lines 199-211."""
        with app.test_client() as client:
            
            with patch('app.ADMIN_USERS') as mock_admin_users, \
                 patch('app.bcrypt.checkpw', return_value=True) as mock_checkpw, \
                 patch('app.login_user') as mock_login_user, \
                 patch('app.log_action') as mock_log_action:
                
                # Set up a test user
                mock_admin_users.__contains__ = lambda self, key: key == 'testuser'
                mock_admin_users.__getitem__ = lambda self, key: {
                    'password_hash': b'fake_hash',
                    'role': 'admin',
                    'name': 'Test User'
                }
                
                # Submit valid credentials
                response = client.post('/login', data={
                    'username': 'testuser',
                    'password': 'correct_password'
                })
                
                # Should hit lines 199-211 (successful login path)
                mock_log_action.assert_called_with('login_success')
                mock_login_user.assert_called_once()
                
                # Should redirect
                assert response.status_code == 302
    
    def test_user_class_methods_lines_117_120(self, app):
        """Test User class methods - lines 117, 120."""
        from app import User
        
        # Test super_admin user (lines 117, 120 return True)
        super_admin_user = User('admin', 'super_admin', 'Super Admin User')
        assert super_admin_user.can_write() == True  # line 114 (super_admin in ['super_admin', 'operator'])
        assert super_admin_user.can_delete() == True  # line 117 (super_admin == 'super_admin')
        assert super_admin_user.can_manage_groups() == True  # line 120 (super_admin == 'super_admin')
        
        # Test operator user (line 114 returns True, lines 117, 120 return False)
        operator_user = User('operator', 'operator', 'Operator User')
        assert operator_user.can_write() == True  # line 114 (operator in ['super_admin', 'operator'])
        assert operator_user.can_delete() == False  # line 117 (operator != 'super_admin')
        assert operator_user.can_manage_groups() == False  # line 120 (operator != 'super_admin')
        
        # Test viewer user (all return False - but these don't hit the missing lines)
        viewer_user = User('viewer', 'viewer', 'Viewer User')
        assert viewer_user.can_write() == False
        assert viewer_user.can_delete() == False
        assert viewer_user.can_manage_groups() == False
    
    def test_login_authenticated_user_redirect_line_195(self, app):
        """Test login route when user is already authenticated - line 195."""
        with app.test_client() as client:
            # Mock authenticated user
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                
                # Access login route while already authenticated
                response = client.get('/login')
                
                # Should redirect to dashboard (line 195)
                assert response.status_code == 302
    
    def test_get_ldap_connection_failure_lines_145_156(self, app):
        """Test LDAP connection failure - lines 145-156."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Mock ldap3.Server and Connection to fail
            with patch('ldap3.Server') as mock_server, \
                 patch('ldap3.Connection') as mock_connection_class:
                
                # Make the connection fail
                mock_connection = Mock()
                mock_connection.bind.return_value = False
                mock_connection_class.return_value = mock_connection
                
                # Call get_ldap_connection
                result = get_ldap_connection()
                
                # Should return None when connection fails (lines 145-156)
                assert result is None
    
    def test_log_action_with_redis_lines_160_167(self, app):
        """Test log_action function with Redis - lines 160-167."""
        with app.app_context():
            from app import log_action
            
            # Mock redis_client
            with patch('app.redis_client') as mock_redis:
                mock_redis.lpush = Mock()
                mock_redis.ltrim = Mock()
                
                # Call log_action
                log_action('test_action', 'test_details')
                
                # Should call redis operations (lines 160-167)
                mock_redis.lpush.assert_called_once()
                mock_redis.ltrim.assert_called_once()
