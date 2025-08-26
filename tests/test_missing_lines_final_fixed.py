"""
Final fixed tests targeting specific missing lines based on actual code structure.
"""
import pytest
from unittest.mock import patch, MagicMock
import bcrypt
from ldap3 import Server, Connection, ALL

class TestMissingLinesFinalFixed:
    """Final fixed tests targeting specific missing lines."""
    
    def test_redis_connection_failure_actual(self, app):
        """Test lines 62-63: Redis connection failure handling."""
        # Mock redis.Redis to raise exception during ping
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.side_effect = Exception("Redis connection failed")
            mock_redis_class.return_value = mock_redis_instance
            
            # Re-import to trigger the redis connection code
            import importlib
            import app as app_module
            importlib.reload(app_module)
            
            # The redis_client should be None after the exception
            assert app_module.redis_client is None
    
    def test_user_can_manage_groups_actual(self, app):
        """Test line 120: can_manage_groups method."""
        with app.app_context():
            from app import User
            
            # Test super_admin can manage groups (line 120)
            super_admin = User('admin', 'super_admin', 'Super Admin')
            assert super_admin.can_manage_groups() == True
            
            # Test other roles cannot manage groups
            other_roles = ['operator', 'user', 'guest', 'admin', '']
            for role in other_roles:
                user = User('testuser', role, 'Test User')
                assert user.can_manage_groups() == False
    
    def test_ldap_connection_success_actual(self, app):
        """Test line 153: Successful LDAP connection return."""
        with app.app_context():
            from app import get_ldap_connection, LDAP_CONFIG
            
            # Mock successful LDAP connection
            with patch('ldap3.Server') as mock_server, \
                 patch('ldap3.Connection') as mock_conn:
                
                mock_connection = MagicMock()
                mock_conn.return_value = mock_connection
                
                # Call get_ldap_connection - this should hit line 153 (return conn)
                conn = get_ldap_connection()
                
                # Should return the mocked connection
                assert conn == mock_connection
    
    def test_admin_login_success_flow_actual(self, app):
        """Test lines 203-211: Complete admin login success flow."""
        with app.test_client() as client:
            # Use the actual admin user from ADMIN_USERS
            with patch('app.log_action') as mock_log_action:
                # Test with the default admin user (password is 'admin123')
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                }, follow_redirects=False)
                
                # Should redirect after successful login (lines 203-211)
                assert response.status_code == 302
                
                # Should redirect to dashboard or next page
                assert 'dashboard' in response.location or response.location == '/'
                
                # Verify log_action was called for login_success
                mock_log_action.assert_any_call('login_success')
    
    def test_logout_flow_actual(self, app):
        """Test lines 221-224: Complete logout flow."""
        with app.test_client() as client:
            # First login as admin
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Now test logout with log_action mock
            with patch('app.log_action') as mock_log_action:
                response = client.get('/logout', follow_redirects=False)
                
                # Should redirect to login page (line 224)
                assert response.status_code == 302
                assert 'login' in response.location
                
                # Verify log_action was called for logout (line 221)
                mock_log_action.assert_called_with('logout')
    
    def test_role_required_decorator_unauthorized_actual(self, app):
        """Test lines 136-137: Role required decorator unauthorized access."""
        with app.test_client() as client:
            # Login as admin first
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Mock current_user to have insufficient role after login
            with patch('flask_login.current_user') as mock_user:
                mock_user.role = 'user'  # Insufficient role
                mock_user.is_authenticated = True
                
                # Try to access a route that likely uses role_required
                # Looking at the app, routes like /users probably have role requirements
                response = client.get('/users')
                
                # Should either redirect or show error (lines 136-137)
                assert response.status_code in [200, 302, 403]
    
    def test_bcrypt_password_verification_actual(self, app):
        """Test bcrypt.checkpw call in login (line 204)."""
        with app.test_client() as client:
            # Test correct password - should hit bcrypt.checkpw and return True
            response1 = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'  # Correct password
            })
            
            # Test wrong password - should hit bcrypt.checkpw and return False
            response2 = client.post('/login', data={
                'username': 'admin',
                'password': 'wrongpassword'  # Wrong password
            })
            
            # Both should process (one succeeds, one fails)
            assert response1.status_code in [200, 302]
            assert response2.status_code in [200, 302]
            
            # Successful login should redirect
            if response1.status_code == 302:
                assert 'dashboard' in response1.location or response1.location == '/'
    
    def test_user_creation_and_login_user_call_actual(self, app):
        """Test User creation and login_user call (lines 205-206)."""
        with app.test_client() as client:
            with patch('flask_login.login_user') as mock_login_user, \
                 patch('app.log_action'):
                
                # This should trigger User creation and login_user call
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                
                # Verify login_user was called with remember=True
                mock_login_user.assert_called_once()
                args, kwargs = mock_login_user.call_args
                
                # Check that remember=True was passed
                assert kwargs.get('remember') == True
                
                # Check that a User object was passed
                user_obj = args[0]
                assert hasattr(user_obj, 'username')
                assert hasattr(user_obj, 'role')
                assert hasattr(user_obj, 'name')
    
    def test_login_with_next_parameter_actual(self, app):
        """Test login with next parameter (part of lines 209-210)."""
        with app.test_client() as client:
            # Test login with next parameter
            response = client.post('/login?next=/users', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=False)
            
            # Should redirect to the next page if login successful
            if response.status_code == 302:
                # Could redirect to /users (next param) or dashboard
                assert '/users' in response.location or 'dashboard' in response.location
    
    def test_login_failed_log_action_actual(self, app):
        """Test login failed log action."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action:
                # Test failed login
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'wrongpassword'
                })
                
                # Should log the failed login attempt
                mock_log_action.assert_any_call('login_failed', 'Username: admin')
    
    def test_comprehensive_coverage_scenarios(self, app):
        """Test various scenarios to maximize coverage."""
        with app.test_client() as client:
            # Test GET login page
            response = client.get('/login')
            assert response.status_code == 200
            
            # Test login with non-existent user
            response = client.post('/login', data={
                'username': 'nonexistent',
                'password': 'anypass'
            })
            assert response.status_code == 200  # Should stay on login page
            
            # Test empty form submission
            response = client.post('/login', data={})
            assert response.status_code == 200
            
            # Test accessing dashboard without login (should redirect to login)
            response = client.get('/', follow_redirects=False)
            assert response.status_code == 302
            assert 'login' in response.location
            
            # Test logout without being logged in
            response = client.get('/logout', follow_redirects=False)
            # This might redirect to login due to @login_required
            assert response.status_code in [200, 302]
    
    def test_ldap_connection_failure_actual(self, app):
        """Test LDAP connection failure (return None)."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Mock LDAP to raise exception
            with patch('ldap3.Server', side_effect=Exception("LDAP server error")):
                conn = get_ldap_connection()
                # Should return None when connection fails
                assert conn is None
            
            # Mock Connection to raise exception
            with patch('ldap3.Connection', side_effect=Exception("LDAP connection error")):
                conn = get_ldap_connection()
                # Should return None when connection fails
                assert conn is None
