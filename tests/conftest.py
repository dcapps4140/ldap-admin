import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    try:
        # Create a temporary log file for testing
        temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        temp_log.close()
        
        # Patch the logging configuration before importing
        with patch('logging.FileHandler') as mock_handler:
            # Create a mock file handler that doesn't require permissions
            mock_handler.return_value = Mock()
            
            # Import the main app
            import app as flask_app_module
            
            # Get the Flask app instance
            if hasattr(flask_app_module, 'app'):
                flask_app = flask_app_module.app
            elif hasattr(flask_app_module, 'create_app'):
                flask_app = flask_app_module.create_app()
            else:
                # Look for Flask app instance
                for attr_name in dir(flask_app_module):
                    attr = getattr(flask_app_module, attr_name)
                    if hasattr(attr, 'config') and hasattr(attr, 'test_client'):
                        flask_app = attr
                        break
                else:
                    raise ImportError("Could not find Flask app instance")
        
        # Configure for testing
        flask_app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
            'LOG_FILE': temp_log.name,
        })
        
        return flask_app
        
    except Exception as e:
        pytest.skip(f"Could not import Flask app: {e}")

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def mock_ldap_connection():
    """Mock LDAP connection for testing."""
    with patch('ldap3.Connection') as mock_conn:
        mock_instance = Mock()
        mock_instance.bind.return_value = True
        mock_instance.search.return_value = True
        mock_instance.add.return_value = True
        mock_instance.modify.return_value = True
        mock_instance.delete.return_value = True
        mock_instance.entries = []
        mock_instance.result = {'result': 0, 'description': 'success'}
        mock_conn.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'SecurePass123!',
        'phone': '+1234567890',
        'groups': ['users']
    }

@pytest.fixture
def sample_group_data():
    """Sample group data for testing."""
    return {
        'name': 'testgroup',
        'description': 'Test Group Description',
        'members': ['testuser1', 'testuser2']
    }

@pytest.fixture
def authenticated_client(client, app):
    """Create a client with an authenticated session."""
    with client.session_transaction() as sess:
        sess['user'] = 'testadmin'
        sess['authenticated'] = True
        sess['is_admin'] = True
    return client

@pytest.fixture
def disable_rate_limits(app):
    """Disable rate limits for testing."""
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    app.config['RATELIMIT_ENABLED'] = False
    yield
    app.config['RATELIMIT_ENABLED'] = original_enabled

@pytest.fixture
def with_rate_limits(app):
    """Ensure rate limits are enabled for testing."""
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    app.config['RATELIMIT_ENABLED'] = True
    yield
    app.config['RATELIMIT_ENABLED'] = original_enabled
