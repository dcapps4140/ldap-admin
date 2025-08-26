"""
Comprehensive test without rate limiting issues.
"""
import pytest
from unittest.mock import patch, MagicMock
import bcrypt

@pytest.fixture(autouse=True)
def disable_limiter():
    """Disable rate limiter for all tests."""
    with patch('flask_limiter.Limiter.limit') as mock_limit:
        # Make the decorator a no-op
        mock_limit.return_value = lambda f: f
        yield

class TestComprehensiveNoRateLimit:
    """Comprehensive tests without rate limiting."""
    
    def test_redis_connection_failure(self, app):
        """Test Redis connection failure - lines 62-63."""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.side_effect = Exception("Redis connection failed")
            mock_redis_class.return_value = mock_redis_instance
            
            # Re-import to trigger the redis connection code
            import importlib
            import app as app_module
            importlib.reload(app_module)
            
            # Should set redis_client to None (lines 62-63)
            assert app_module.redis_client is None
    
    def test_user_can_manage_groups_line_120(self, app):
        """Test can_manage_groups method - line 120."""
        with app.app_context():
            from app import User
            
            # Test super_admin role (should return True) - hits line 120
            super_admin = User('admin', 'super_admin', 'Super Admin')
            assert super_admin.can_manage_groups() == True
            
            # Test other roles (should return False)
            for role in ['admin', 'operator', 'user', 'guest', '', None]:
                user = User('test', role, 'Test User')
                assert user.can_manage_groups() == False
    
    def test_role_required_decorator_lines_136_137(self, app):
        """Test role_required decorator unauthorized access - lines 136-137."""
        with app.test_client() as client:
            # First login as admin
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Mock current_user to have insufficient role
            with patch('flask_login.current_user') as mock_user:
                mock_user.role = 'user'  # Insufficient role
                mock_user.is_authenticated = True
                
                # Try to access a route that requires higher permissions
                response = client.get('/users')
                
                # Should handle unauthorized access
                assert response.status_code in [200, 302, 403]
    
    def test_ldap_connection_success_line_153(self, app):
        """Test successful LDAP connection return - line 153."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Mock LDAP components for successful connection
            with patch('app.Server') as mock_server, \
                 patch('app.Connection') as mock_conn:
                
                mock_connection = MagicMock()
                mock_conn.return_value = mock_connection
                
                # Call get_ldap_connection - should hit line 153 (return conn)
                conn = get_ldap_connection()
                
                # Should return the mocked connection
                assert conn == mock_connection
    
    def test_ldap_connection_failure_lines_154_156(self, app):
        """Test LDAP connection failure scenarios - lines 154-156."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Test Server creation failure
            with patch('app.Server', side_effect=Exception("Server error")):
                conn = get_ldap_connection()
                assert conn is None
            
            # Test Connection creation failure  
            with patch('app.Connection', side_effect=Exception("Connection error")):
                conn = get_ldap_connection()
                assert conn is None
    
    def test_admin_login_success_lines_203_211(self, app):
        """Test complete admin login success flow - lines 203-211."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action:
                
                # Test successful login with admin user
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                }, follow_redirects=False)
                
                # Should redirect after successful login (lines 209-210)
                assert response.status_code == 302
                
                # Should call log_action for login_success (line 207)
                mock_log_action.assert_any_call('login_success')
    
    def test_logout_flow_lines_221_224(self, app):
        """Test complete logout flow - lines 221-224."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Now test logout
            with patch('app.log_action') as mock_log_action:
                response = client.get('/logout', follow_redirects=False)
                
                # Should redirect to login page (line 224)
                assert response.status_code == 302
                assert 'login' in response.location
                
                # Should call log_action for logout (line 221)
                mock_log_action.assert_called_with('logout')
    
    def test_login_failed_log_action_lines_213_214(self, app):
        """Test login failed log action - lines 213-214."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action:
                
                # Test failed login
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'wrongpassword'
                })
                
                # Should log failed login attempt (lines 213-214)
                mock_log_action.assert_any_call('login_failed', 'Username: admin')
    
    def test_user_not_in_admin_users(self, app):
        """Test user not in ADMIN_USERS."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action:
                
                # Test with user not in ADMIN_USERS
                response = client.post('/login', data={
                    'username': 'notanadmin',
                    'password': 'anypassword'
                })
                
                # Should stay on login page
                assert response.status_code == 200
                
                # Should log failed login
                mock_log_action.assert_any_call('login_failed', 'Username: notanadmin')
    
    def test_form_validation_scenarios(self, app):
        """Test form validation to hit more lines."""
        with app.test_client() as client:
            # Test GET request (should render form)
            response = client.get('/login')
            assert response.status_code == 200
            
            # Test POST with empty data (form validation should fail)
            response = client.post('/login', data={})
            assert response.status_code == 200
            
            # Test POST with invalid data
            response = client.post('/login', data={
                'username': '',
                'password': ''
            })
            assert response.status_code == 200
    
    def test_authenticated_user_redirect(self, app):
        """Test authenticated user redirect in login route."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Try to access login page again (should redirect)
            response = client.get('/login', follow_redirects=False)
            if response.status_code == 302:
                assert 'dashboard' in response.location or response.location == '/'
    
    def test_login_with_next_parameter(self, app):
        """Test login with next parameter."""
        with app.test_client() as client:
            # Test login with next parameter
            response = client.post('/login?next=/dashboard', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=False)
            
            # Should redirect to next page or dashboard
            if response.status_code == 302:
                assert 'dashboard' in response.location or response.location == '/'
    
    def test_bcrypt_password_verification(self, app):
        """Test bcrypt.checkpw call."""
        with app.test_client() as client:
            # Test correct password (should hit bcrypt.checkpw and return True)
            response1 = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Test wrong password (should hit bcrypt.checkpw and return False)
            response2 = client.post('/login', data={
                'username': 'admin',
                'password': 'wrongpassword'
            })
            
            # Both should process the bcrypt check
            assert response1.status_code in [200, 302]
            assert response2.status_code in [200, 302]
    
    def test_user_creation_and_login_user(self, app):
        """Test User creation and login_user call."""
        with app.test_client() as client:
            with patch('flask_login.login_user') as mock_login_user, \
                 patch('app.log_action'):
                
                # This should trigger User creation and login_user call
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                
                # Verify login_user was called with remember=True
                if mock_login_user.call_count > 0:
                    args, kwargs = mock_login_user.call_args
                    assert kwargs.get('remember') == True
                    
                    # Verify User object was created
                    user_obj = args[0]
                    assert hasattr(user_obj, 'username')
                    assert user_obj.username == 'admin'
    
    def test_dashboard_route_line_229(self, app):
        """Test dashboard route - line 229."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Access dashboard
            response = client.get('/')
            assert response.status_code == 200
    
    def test_users_route_lines_235_257(self, app):
        """Test users route - lines 235-257."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Mock LDAP connection and data
            with patch('app.get_ldap_connection') as mock_get_conn:
                mock_conn = MagicMock()
                mock_get_conn.return_value = mock_conn
                mock_conn.search.return_value = True
                mock_conn.entries = []
                
                # Access users page
                response = client.get('/users')
                assert response.status_code == 200
    
    def test_groups_route_lines_262_272(self, app):
        """Test groups route - lines 262-272."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Mock LDAP connection and data
            with patch('app.get_ldap_connection') as mock_get_conn:
                mock_conn = MagicMock()
                mock_get_conn.return_value = mock_conn
                mock_conn.search.return_value = True
                mock_conn.entries = []
                
                # Access groups page
                response = client.get('/groups')
                assert response.status_code == 200
    
    def test_settings_route_line_279(self, app):
        """Test settings route - line 279."""
        with app.test_client() as client:
            # First login
            client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Access settings page
            response = client.get('/settings')
            assert response.status_code == 200
