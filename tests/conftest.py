import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import logging

# Mock the logging configuration before importing the app
@pytest.fixture(scope="session", autouse=True)
def mock_logging():
    """Mock logging configuration to avoid permission issues during testing."""
    with patch('logging.FileHandler') as mock_file_handler:
        # Create a mock file handler that doesn't actually write to /var/log
        mock_handler = MagicMock()
        mock_file_handler.return_value = mock_handler
        yield mock_handler

# Now we can safely import the app
@pytest.fixture(scope="session")
def flask_app():
    """Import the Flask app with mocked logging."""
    with patch('logging.FileHandler'):
        from app import app as flask_app, limiter
        return flask_app, limiter

@pytest.fixture
def app(flask_app):
    """Create and configure a new app instance for each test."""
    app_instance, limiter_instance = flask_app
    
    # Save original config
    original_config = app_instance.config.copy()
    
    # Configure for testing
    app_instance.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
        'RATELIMIT_ENABLED': False,  # Disable rate limiting for most tests
        'SECRET_KEY': 'test-secret-key-for-testing',
        # LDAP test config
        'LDAP_SERVER': 'ldap://test-server:389',
        'LDAP_BASE_DN': 'dc=test,dc=com',
        'LDAP_USER_DN': 'ou=users,dc=test,dc=com',
        'LDAP_GROUP_DN': 'ou=groups,dc=test,dc=com',
        'LDAP_BIND_USER': 'cn=admin,dc=test,dc=com',
        'LDAP_BIND_PASSWORD': 'testpassword',
        # Redis test config
        'REDIS_URL': 'redis://localhost:6379/15',  # Use test database
    })
    
    with app_instance.app_context():
        yield app_instance
    
    # Restore original config
    app_instance.config.update(original_config)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

# RATE LIMITING FIXTURES

@pytest.fixture
def app_no_rate_limits(flask_app):
    """Create app instance with rate limiting disabled."""
    app_instance, limiter_instance = flask_app
    original_config = app_instance.config.copy()
    
    app_instance.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-for-testing',
    })
    
    # Disable the limiter for these tests
    original_enabled = limiter_instance.enabled
    limiter_instance.enabled = False
    
    with app_instance.app_context():
        yield app_instance
    
    # Restore
    limiter_instance.enabled = original_enabled
    app_instance.config.update(original_config)

@pytest.fixture
def client_no_rate_limits(app_no_rate_limits):
    """Test client with rate limiting disabled."""
    return app_no_rate_limits.test_client()

@pytest.fixture
def app_with_rate_limits(flask_app):
    """Create app instance with rate limiting enabled."""
    app_instance, limiter_instance = flask_app
    original_config = app_instance.config.copy()
    
    app_instance.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': True,
        'SECRET_KEY': 'test-secret-key-for-testing',
    })
    
    # Enable the limiter for these tests
    original_enabled = limiter_instance.enabled
    limiter_instance.enabled = True
    
    with app_instance.app_context():
        yield app_instance
    
    # Restore
    limiter_instance.enabled = original_enabled
    app_instance.config.update(original_config)

@pytest.fixture
def client_with_rate_limits(app_with_rate_limits):
    """Test client with rate limiting enabled."""
    return app_with_rate_limits.test_client()

# LDAP MOCKING FIXTURES

@pytest.fixture
def mock_ldap_connection():
    """Mock LDAP connection for testing."""
    with patch('ldap3.Connection') as mock_conn:
        mock_instance = MagicMock()
        mock_instance.bind.return_value = True
        mock_instance.search.return_value = True
        mock_instance.entries = []
        mock_instance.result = {'result': 0, 'description': 'success'}
        mock_conn.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_ldap_server():
    """Mock LDAP server for testing."""
    with patch('ldap3.Server') as mock_server:
        mock_server.return_value = MagicMock()
        yield mock_server

@pytest.fixture
def mock_ldap_user():
    """Mock LDAP user entry."""
    mock_user = MagicMock()
    mock_user.cn.value = 'Test User'
    mock_user.uid.value = 'testuser'
    mock_user.mail.value = 'testuser@example.com'
    mock_user.entry_dn = 'uid=testuser,ou=users,dc=test,dc=com'
    return mock_user

@pytest.fixture
def mock_ldap_group():
    """Mock LDAP group entry."""
    mock_group = MagicMock()
    mock_group.cn.value = 'Test Group'
    mock_group.description.value = 'Test group description'
    mock_group.member.values = ['uid=testuser,ou=users,dc=test,dc=com']
    mock_group.entry_dn = 'cn=testgroup,ou=groups,dc=test,dc=com'
    return mock_group

# AUTHENTICATION FIXTURES

@pytest.fixture
def mock_user():
    """Mock user object for Flask-Login."""
    from flask_login import UserMixin
    
    class MockUser(UserMixin):
        def __init__(self, username='testuser'):
            self.id = username
            self.username = username
            self.email = f'{username}@example.com'
            self.is_admin = False
        
        def get_id(self):
            return self.username
    
    return MockUser()

@pytest.fixture
def mock_admin_user():
    """Mock admin user object."""
    from flask_login import UserMixin
    
    class MockAdminUser(UserMixin):
        def __init__(self):
            self.id = 'admin'
            self.username = 'admin'
            self.email = 'admin@example.com'
            self.is_admin = True
        
        def get_id(self):
            return self.username
    
    return MockAdminUser()

@pytest.fixture
def authenticated_client(client, mock_user):
    """Client with authenticated user session."""
    with client.session_transaction() as sess:
        sess['_user_id'] = mock_user.get_id()
        sess['_fresh'] = True
    return client

@pytest.fixture
def authenticated_admin_client(client, mock_admin_user):
    """Client with authenticated admin user session."""
    with client.session_transaction() as sess:
        sess['_user_id'] = mock_admin_user.get_id()
        sess['_fresh'] = True
        sess['is_admin'] = True
    return client

# REDIS FIXTURES

@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_instance = MagicMock()
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis_instance.exists.return_value = False
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance

# FORM DATA FIXTURES

@pytest.fixture
def valid_login_data():
    """Valid login form data."""
    return {
        'username': 'testuser',
        'password': 'testpassword'
    }

@pytest.fixture
def invalid_login_data():
    """Invalid login form data."""
    return {
        'username': 'invaliduser',
        'password': 'wrongpassword'
    }

@pytest.fixture
def valid_user_data():
    """Valid user creation data."""
    return {
        'username': 'newuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
        'password': 'newpassword123'
    }

@pytest.fixture
def valid_group_data():
    """Valid group creation data."""
    return {
        'name': 'newgroup',
        'description': 'New test group'
    }

# ENVIRONMENT FIXTURES

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'LDAP_SERVER': 'ldap://test-server:389',
        'LDAP_BASE_DN': 'dc=test,dc=com',
        'LDAP_USER_DN': 'ou=users,dc=test,dc=com',
        'LDAP_GROUP_DN': 'ou=groups,dc=test,dc=com',
        'LDAP_BIND_USER': 'cn=admin,dc=test,dc=com',
        'LDAP_BIND_PASSWORD': 'testpassword',
        'SECRET_KEY': 'test-secret-key',
        'REDIS_URL': 'redis://localhost:6379/15'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

# COMPREHENSIVE LDAP MOCK FIXTURE

@pytest.fixture
def mock_ldap_full():
    """Comprehensive LDAP mocking for full functionality tests."""
    with patch('ldap3.Server') as mock_server, \
         patch('ldap3.Connection') as mock_conn:
        
        # Setup server mock
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        
        # Setup connection mock
        mock_conn_instance = MagicMock()
        mock_conn_instance.bind.return_value = True
        mock_conn_instance.search.return_value = True
        mock_conn_instance.add.return_value = True
        mock_conn_instance.modify.return_value = True
        mock_conn_instance.delete.return_value = True
        mock_conn_instance.result = {'result': 0, 'description': 'success'}
        mock_conn_instance.entries = []
        mock_conn.return_value = mock_conn_instance
        
        yield {
            'server': mock_server_instance,
            'connection': mock_conn_instance
        }

# CLEAN SESSION FIXTURE

@pytest.fixture
def clean_session(client):
    """Client with a clean session."""
    with client.session_transaction() as sess:
        sess.clear()
    return client

# MISSING FIXTURES - Add these to the end of conftest.py

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'username': 'sampleuser',
        'first_name': 'Sample',
        'last_name': 'User',
        'email': 'sampleuser@example.com',
        'password': 'samplepassword123',
        'department': 'IT',
        'title': 'Developer'
    }

@pytest.fixture
def sample_group_data():
    """Sample group data for testing."""
    return {
        'name': 'samplegroup',
        'description': 'Sample group for testing',
        'members': ['sampleuser', 'testuser']
    }

@pytest.fixture
def authenticated_client_no_rate_limits(client_no_rate_limits, mock_user):
    """Authenticated client with rate limiting disabled."""
    with client_no_rate_limits.session_transaction() as sess:
        sess['_user_id'] = mock_user.get_id()
        sess['_fresh'] = True
    return client_no_rate_limits

@pytest.fixture
def working_authenticated_client(app):
    """Create a properly authenticated client."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = True  # Disable login requirement for testing
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
            sess['roles'] = ['user', 'admin']
            sess['_fresh'] = True
        yield client

@pytest.fixture  
def bypass_auth_client(app):
    """Create a client that bypasses authentication."""
    # Temporarily disable authentication
    original_login_required = app.view_functions.get('api_get_users', lambda: None)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
            sess['roles'] = ['user', 'admin']
        
        # Mock the login_required decorator to do nothing
        with patch('flask_login.login_required', lambda f: f):
            yield client
