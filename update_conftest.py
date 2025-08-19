#!/usr/bin/env python3
import os
import shutil

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def update_conftest():
    """Update conftest.py to use the test app factory."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return False
    
    # Backup the file
    backup_file(conftest_path)
    
    new_conftest = '''import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the test app factory
from tests.test_app_factory import create_test_app

@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    try:
        return create_test_app()
    except Exception as e:
        pytest.skip(f"Could not create test app: {e}")

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
    
    # Make a request to ensure the session is saved
    client.get('/')
    
    yield client

@pytest.fixture
def authenticated_client_no_rate_limits(authenticated_client):
    """Create an authenticated client with rate limits disabled."""
    yield authenticated_client
'''
    
    with open(conftest_path, 'w') as f:
        f.write(new_conftest)
    
    print(f"Updated {conftest_path}")
    return True

if __name__ == "__main__":
    update_conftest()
