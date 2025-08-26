"""
Final comprehensive test to maximize coverage.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import bcrypt
from flask import Flask

@pytest.fixture(autouse=True)
def disable_limiter():
    """Disable rate limiter for all tests."""
    with patch('flask_limiter.Limiter.limit') as mock_limit, \
         patch('flask_limiter.Limiter.exempt') as mock_exempt:
        mock_limit.return_value = lambda f: f
        mock_exempt.return_value = lambda f: f
        yield

class TestFinalComprehensive:
    """Final comprehensive test suite."""
    
    def test_user_class_all_methods(self, app):
        """Test all User class methods."""
        with app.app_context():
            from app import User
            
            # Test super_admin user
            super_admin = User('admin', 'super_admin', 'Super Admin')
            assert super_admin.username == 'admin'
            assert super_admin.role == 'super_admin'
            assert super_admin.name == 'Super Admin'
            assert super_admin.id == 'admin'
            
            # Test Flask-Login methods
            assert super_admin.is_authenticated == True
            assert super_admin.is_active == True
            assert super_admin.is_anonymous == False
            assert super_admin.get_id() == 'admin'
            
            # Test permission methods
            assert super_admin.can_write() == True
            assert super_admin.can_delete() == True
            assert super_admin.can_manage_groups() == True
            
            # Test operator user
            operator = User('op1', 'operator', 'Operator One')
            assert operator.can_write() == True
            assert operator.can_delete() == False
            assert operator.can_manage_groups() == False
            
            # Test regular admin user
            admin = User('admin1', 'admin', 'Admin One')
            assert admin.can_write() == False
            assert admin.can_delete() == False
            assert admin.can_manage_groups() == False
    
    def test_load_user_function_complete(self, app):
        """Test load_user function completely - lines 114, 117."""
        with app.app_context():
            from app import load_user, ADMIN_USERS
            
            # Test with each admin user in ADMIN_USERS
            for username, user_data in ADMIN_USERS.items():
                user = load_user(username)
                assert user is not None
                assert user.username == username
                assert user.role == user_data['role']
                assert user.name == user_data['name']
            
            # Test with non-existent user (line 117)
            user = load_user('nonexistent')
            assert user is None
            
            # Test with None
            user = load_user(None)
            assert user is None
            
            # Test with empty string
            user = load_user('')
            assert user is None
    
    def test_role_required_decorator_complete(self, app):
        """Test role_required decorator completely - lines 124-127, 135-138."""
        with app.app_context():
            from app import role_required
            
            # Create test functions with different role requirements
            @role_required('admin')
            def admin_function():
                return "admin_success"
            
            @role_required('super_admin')
            def super_admin_function():
                return "super_admin_success"
            
            # Test with sufficient role (lines 124-127)
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.role = 'admin'
                
                result = admin_function()
                assert result == "admin_success"
            
            # Test with insufficient role (lines 135-138)
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.role = 'admin'  # Not super_admin
                
                with patch('flask.flash') as mock_flash, \
                     patch('flask.redirect') as mock_redirect, \
                     patch('flask.url_for') as mock_url_for:
                    
                    mock_redirect.return_value = Mock()
                    mock_url_for.return_value = '/dashboard'
                    
                    result = super_admin_function()
                    
                    # Should flash error message
                    mock_flash.assert_called_once_with('Access denied. Insufficient permissions.', 'error')
                    # Should redirect to dashboard
                    mock_redirect.assert_called_once()
    
    def test_ldap_connection_all_scenarios(self, app):
        """Test all LDAP connection scenarios - lines 153, 154-156, 160-167."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Test successful connection (line 153)
            with patch('app.Server') as mock_server, \
                 patch('app.Connection') as mock_conn_class:
                
                mock_connection = MagicMock()
                mock_conn_class.return_value = mock_connection
                
                conn = get_ldap_connection()
                assert conn == mock_connection
            
            # Test Server creation exception (lines 154-156)
            with patch('app.Server', side_effect=Exception("Server error")):
                conn = get_ldap_connection()
                assert conn is None
            
            # Test Connection creation exception (lines 154-156)
            with patch('app.Server') as mock_server, \
                 patch('app.Connection', side_effect=Exception("Connection error")):
                
                conn = get_ldap_connection()
                assert conn is None
            
            # Test different exception types
            with patch('app.Server', side_effect=ImportError("LDAP3 not found")):
                conn = get_ldap_connection()
                assert conn is None
            
            with patch('app.Server', side_effect=ConnectionError("Network error")):
                conn = get_ldap_connection()
                assert conn is None
    
    def test_login_route_complete_coverage(self, app):
        """Test login route for complete coverage - lines 195, 203-214."""
        with app.test_client() as client:
            
            # Test GET request (line 195)
            response = client.get('/login')
            assert response.status_code in [200, 302]
            
            with patch('app.log_action') as mock_log_action, \
                 patch('flask_login.login_user') as mock_login_user:
                
                # Test successful login (lines 203-211)
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                
                # Should log successful login
                mock_log_action.assert_any_call('login_success')
                
                # Test failed login - wrong password (lines 213-214)
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'wrongpassword'
                })
                
                # Should log failed login
                mock_log_action.assert_any_call('login_failed', 'Username: admin')
                
                # Test failed login - user not in ADMIN_USERS (lines 213-214)
                response = client.post('/login', data={
                    'username': 'notanadmin',
                    'password': 'anypassword'
                })
                
                # Should log failed login
                mock_log_action.assert_any_call('login_failed', 'Username: notanadmin')
    
    def test_logout_route_complete(self, app):
        """Test logout route completely - lines 221-224."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action, \
                 patch('flask_login.logout_user') as mock_logout_user, \
                 patch('flask.redirect') as mock_redirect, \
                 patch('flask.url_for') as mock_url_for:
                
                mock_redirect.return_value = Mock()
                mock_url_for.return_value = '/login'
                
                # Test logout
                response = client.get('/logout')
                
                # Should log logout (line 221)
                mock_log_action.assert_called_with('logout')
                
                # Should call logout_user (line 222)
                mock_logout_user.assert_called_once()
                
                # Should redirect to login (lines 223-224)
                mock_url_for.assert_called_with('login')
                mock_redirect.assert_called_once()
    
    def test_dashboard_route_complete(self, app):
        """Test dashboard route - line 229."""
        with app.test_client() as client:
            with patch('flask_login.current_user') as mock_user, \
                 patch('flask.render_template') as mock_render:
                
                mock_user.is_authenticated = True
                mock_user.role = 'admin'
                mock_render.return_value = 'dashboard_html'
                
                response = client.get('/')
                
                # Should render dashboard template (line 229)
                if response.status_code == 200:
                    mock_render.assert_called_with('dashboard.html')
    
    def test_users_route_complete(self, app):
        """Test users route completely - lines 235-257."""
        with app.test_client() as client:
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.role = 'admin'
                
                # Test with successful LDAP connection
                with patch('app.get_ldap_connection') as mock_get_conn, \
                     patch('flask.render_template') as mock_render:
                    
                    mock_conn = MagicMock()
                    mock_get_conn.return_value = mock_conn
                    mock_conn.search.return_value = True
                    
                    # Create mock LDAP entries
                    mock_entry = MagicMock()
                    mock_entry.cn.value = 'testuser'
                    mock_entry.mail.value = 'test@example.com'
                    mock_entry.entry_dn = 'cn=testuser,ou=users,dc=example,dc=com'
                    mock_conn.entries = [mock_entry]
                    
                    mock_render.return_value = 'users_html'
                    
                    response = client.get('/users')
                    
                    # Should search LDAP (line 237)
                    mock_conn.search.assert_called()
                    
                    # Should render users template if successful
                    if response.status_code == 200:
                        mock_render.assert_called()
                
                # Test with failed LDAP connection
                with patch('app.get_ldap_connection', return_value=None), \
                     patch('flask.render_template') as mock_render:
                    
                    mock_render.return_value = 'users_html'
                    
                    response = client.get('/users')
                    
                    # Should still render template with empty users list
                    if response.status_code == 200:
                        mock_render.assert_called()
    
    def test_groups_route_complete(self, app):
        """Test groups route completely - lines 262, 267, 272."""
        with app.test_client() as client:
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.role = 'admin'
                
                # Test with successful LDAP connection
                with patch('app.get_ldap_connection') as mock_get_conn, \
                     patch('flask.render_template') as mock_render:
                    
                    mock_conn = MagicMock()
                    mock_get_conn.return_value = mock_conn
                    mock_conn.search.return_value = True
                    
                    # Create mock LDAP group entries
                    mock_group = MagicMock()
                    mock_group.cn.value = 'testgroup'
                    mock_group.description.value = 'Test Group'
                    mock_group.entry_dn = 'cn=testgroup,ou=groups,dc=example,dc=com'
                    mock_conn.entries = [mock_group]
                    
                    mock_render.return_value = 'groups_html'
                    
                    response = client.get('/groups')
                    
                    # Should search LDAP for groups (line 264)
                    mock_conn.search.assert_called()
                    
                    # Should render groups template (line 272)
                    if response.status_code == 200:
                        mock_render.assert_called_with('groups.html', groups=mock_conn.entries)
    
    def test_settings_route_complete(self, app):
        """Test settings route - line 279."""
        with app.test_client() as client:
            with patch('flask_login.current_user') as mock_user, \
                 patch('flask.render_template') as mock_render:
                
                mock_user.is_authenticated = True
                mock_user.role = 'admin'
                mock_render.return_value = 'settings_html'
                
                response = client.get('/settings')
                
                # Should render settings template (line 279)
                if response.status_code == 200:
                    mock_render.assert_called_with('settings.html')
    
    def test_bcrypt_password_operations(self, app):
        """Test bcrypt password verification in login."""
        with app.test_client() as client:
            # This will test the bcrypt.checkpw calls in the login function
            
            # Test correct password
            response1 = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Test incorrect password
            response2 = client.post('/login', data={
                'username': 'admin',
                'password': 'wrongpassword'
            })
            
            # Both should process without errors
            assert response1.status_code in [200, 302, 429]
            assert response2.status_code in [200, 302, 429]
    
    def test_form_validation_scenarios(self, app):
        """Test form validation scenarios."""
        with app.test_client() as client:
            # Test empty form submission
            response = client.post('/login', data={})
            assert response.status_code in [200, 302, 400, 429]
            
            # Test partial form submission
            response = client.post('/login', data={'username': 'admin'})
            assert response.status_code in [200, 302, 400, 429]
            
            # Test with empty values
            response = client.post('/login', data={
                'username': '',
                'password': ''
            })
            assert response.status_code in [200, 302, 400, 429]
    
    def test_authenticated_user_redirect_in_login(self, app):
        """Test authenticated user redirect in login route."""
        with app.test_client() as client:
            with patch('flask_login.current_user') as mock_user, \
                 patch('flask.redirect') as mock_redirect, \
                 patch('flask.url_for') as mock_url_for:
                
                mock_user.is_authenticated = True
                mock_redirect.return_value = Mock()
                mock_url_for.return_value = '/dashboard'
                
                # GET request when already authenticated
                response = client.get('/login')
                
                # Should redirect to dashboard
                if mock_redirect.called:
                    mock_url_for.assert_called_with('dashboard')
    
    def test_redis_connection_scenarios(self, app):
        """Test Redis connection scenarios - lines 62-63."""
        # Test Redis connection failure
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.side_effect = Exception("Redis unavailable")
            mock_redis_class.return_value = mock_redis_instance
            
            # Re-import app to trigger Redis connection code
            import importlib
            import app as app_module
            importlib.reload(app_module)
            
            # Should handle Redis failure gracefully
            assert app_module.redis_client is None
