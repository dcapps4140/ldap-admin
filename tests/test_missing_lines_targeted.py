"""
Targeted tests for specific missing lines in coverage.
"""
import pytest
from unittest.mock import patch, MagicMock
import redis
import bcrypt

class TestMissingLinesTargeted:
    """Target specific missing lines identified in coverage report."""
    
    def test_redis_connection_failure(self, app):
        """Test lines 62-63: Redis connection failure handling."""
        with app.app_context():
            # Mock redis to raise an exception
            with patch('redis.Redis') as mock_redis:
                mock_redis.side_effect = Exception("Redis connection failed")
                
                # Re-import the module to trigger the redis connection code
                import importlib
                import app as app_module
                importlib.reload(app_module)
                
                # The redis_client should be None after the exception
                assert app_module.redis_client is None
    
    def test_user_can_manage_groups(self, app):
        """Test line 120: can_manage_groups method."""
        with app.app_context():
            from app import User
            
            # Test super_admin can manage groups
            super_admin = User('admin', 'super_admin', 'Super Admin')
            assert super_admin.can_manage_groups() == True
            
            # Test other roles cannot manage groups
            roles_to_test = ['operator', 'user', 'guest', 'admin', '']
            for role in roles_to_test:
                user = User('testuser', role, 'Test User')
                assert user.can_manage_groups() == False
    
    def test_role_required_decorator_unauthorized(self, app):
        """Test lines 136-137: Role required decorator with unauthorized access."""
        with app.test_client() as client:
            from app import role_required
            from flask import Blueprint
            
            # Create a test blueprint with role-required route
            test_bp = Blueprint('test', __name__)
            
            @test_bp.route('/admin-only')
            @role_required('super_admin')
            def admin_only():
                return 'Admin content'
            
            app.register_blueprint(test_bp)
            
            # Mock a logged-in user with insufficient privileges
            with patch('flask_login.current_user') as mock_user:
                mock_user.role = 'user'  # Not super_admin
                mock_user.is_authenticated = True
                
                with client.session_transaction() as sess:
                    sess['user_id'] = 'testuser'
                
                # This should trigger the flash message and redirect
                response = client.get('/admin-only')
                # Should redirect due to insufficient permissions
                assert response.status_code in [302, 403]
    
    def test_ldap_connection_success(self, app):
        """Test line 153: Successful LDAP connection return."""
        with app.app_context():
            from app import get_ldap_connection
            
            # Mock successful LDAP connection
            with patch('ldap3.Server') as mock_server, \
                 patch('ldap3.Connection') as mock_conn:
                
                mock_connection = MagicMock()
                mock_connection.bind.return_value = True
                mock_conn.return_value = mock_connection
                
                # Mock app config
                with patch.object(app, 'config', {
                    'LDAP_SERVER': 'ldap://test.com',
                    'LDAP_BIND_DN': 'cn=admin,dc=test,dc=com',
                    'LDAP_BIND_PASSWORD': 'password'
                }):
                    conn = get_ldap_connection()
                    # This should return the connection (line 153)
                    assert conn == mock_connection
    
    def test_admin_user_login_success(self, app):
        """Test lines 203-211: Successful admin user login flow."""
        with app.test_client() as client:
            # We need to patch ADMIN_USERS to have a test user
            test_password = 'testpass123'
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            test_admin_users = {
                'testadmin': {
                    'password_hash': hashed_password,
                    'role': 'super_admin',
                    'name': 'Test Administrator'
                }
            }
            
            with patch('app.ADMIN_USERS', test_admin_users), \
                 patch('app.log_action') as mock_log_action:
                
                # Test successful login
                response = client.post('/login', data={
                    'username': 'testadmin',
                    'password': test_password
                }, follow_redirects=False)
                
                # Should redirect after successful login (lines 203-211)
                assert response.status_code == 302
                
                # Verify log_action was called
                mock_log_action.assert_called()
    
    def test_logout_flow(self, app):
        """Test lines 221-224: Complete logout flow."""
        with app.test_client() as client:
            with patch('app.log_action') as mock_log_action:
                # Set up a logged-in session
                with client.session_transaction() as sess:
                    sess['user_id'] = 'testuser'
                    sess['_user_id'] = 'testuser'
                    sess['_fresh'] = True
                
                # Mock current_user
                with patch('flask_login.current_user') as mock_user:
                    mock_user.is_authenticated = True
                    mock_user.username = 'testuser'
                    
                    # Test logout
                    response = client.get('/logout', follow_redirects=False)
                    
                    # Should redirect to login page (lines 221-224)
                    assert response.status_code == 302
                    assert '/login' in response.location
                    
                    # Verify log_action was called for logout
                    mock_log_action.assert_called_with('logout')
    
    def test_admin_user_login_with_next_parameter(self, app):
        """Test login with next parameter (part of lines 203-211)."""
        with app.test_client() as client:
            test_password = 'testpass123'
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            test_admin_users = {
                'testadmin': {
                    'password_hash': hashed_password,
                    'role': 'super_admin',
                    'name': 'Test Administrator'
                }
            }
            
            with patch('app.ADMIN_USERS', test_admin_users), \
                 patch('app.log_action'):
                
                # Test login with next parameter
                response = client.post('/login?next=/users', data={
                    'username': 'testadmin',
                    'password': test_password
                }, follow_redirects=False)
                
                # Should redirect to the next page
                assert response.status_code == 302
    
    def test_bcrypt_password_verification(self, app):
        """Test bcrypt password verification (line 204)."""
        with app.test_client() as client:
            # Test with correct password
            test_password = 'correctpass'
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            test_admin_users = {
                'testuser': {
                    'password_hash': hashed_password,
                    'role': 'admin',
                    'name': 'Test User'
                }
            }
            
            with patch('app.ADMIN_USERS', test_admin_users):
                # This should trigger the bcrypt.checkpw line
                response = client.post('/login', data={
                    'username': 'testuser',
                    'password': test_password
                })
                
                # Test with wrong password
                response = client.post('/login', data={
                    'username': 'testuser',
                    'password': 'wrongpass'
                })
    
    def test_user_creation_and_login_user_call(self, app):
        """Test User creation and login_user call (lines 205-206)."""
        with app.test_client() as client:
            test_password = 'testpass'
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            test_admin_users = {
                'logintest': {
                    'password_hash': hashed_password,
                    'role': 'operator',
                    'name': 'Login Test User'
                }
            }
            
            with patch('app.ADMIN_USERS', test_admin_users), \
                 patch('flask_login.login_user') as mock_login_user, \
                 patch('app.log_action'):
                
                response = client.post('/login', data={
                    'username': 'logintest',
                    'password': test_password
                })
                
                # Verify login_user was called with remember=True
                mock_login_user.assert_called_once()
                args, kwargs = mock_login_user.call_args
                assert kwargs.get('remember') == True
