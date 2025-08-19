#!/usr/bin/env python3
import os
import shutil

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def add_fixtures():
    """Add fixtures to conftest.py."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return False
    
    # Backup the file
    backup_file(conftest_path)
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    # Add the disable_rate_limits fixture
    disable_rate_limits_fixture = '''
@pytest.fixture(autouse=True)
def disable_rate_limits(app):
    """Disable rate limits for testing."""
    # Store original config
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    
    # Disable rate limits
    app.config['RATELIMIT_ENABLED'] = False
    
    # Also patch the limiter if it exists
    if hasattr(app, 'extensions') and 'limiter' in app.extensions:
        limiter = app.extensions['limiter']
        original_limiter_enabled = limiter.enabled
        limiter.enabled = False
    else:
        original_limiter_enabled = None
    
    yield
    
    # Restore original config
    app.config['RATELIMIT_ENABLED'] = original_enabled
    
    # Restore limiter config if it exists
    if hasattr(app, 'extensions') and 'limiter' in app.extensions and original_limiter_enabled is not None:
        app.extensions['limiter'].enabled = original_limiter_enabled
'''
    
    # Add the enhanced authenticated_client fixture
    authenticated_client_fixture = '''
@pytest.fixture
def authenticated_client(client, app):
    """Create a client with an authenticated session."""
    with client.session_transaction() as sess:
        sess['user'] = 'testadmin'
        sess['authenticated'] = True
        sess['is_admin'] = True
        
        # Add any other session variables needed for authentication
        if hasattr(app, 'config'):
            if 'SESSION_COOKIE_NAME' in app.config:
                sess[app.config['SESSION_COOKIE_NAME']] = 'test-session'
    
    # Make a request to ensure the session is saved
    client.get('/')
    
    yield client
'''
    
    # Add the combined fixture
    combined_fixture = '''
@pytest.fixture
def authenticated_client_no_rate_limits(authenticated_client, disable_rate_limits):
    """Create an authenticated client with rate limits disabled."""
    yield authenticated_client
'''
    
    # Check if fixtures already exist
    if 'def disable_rate_limits' not in content:
        content += disable_rate_limits_fixture
        print("Added disable_rate_limits fixture")
    
    if 'def authenticated_client' not in content:
        content += authenticated_client_fixture
        print("Added authenticated_client fixture")
    else:
        # Replace the existing authenticated_client fixture
        import re
        pattern = r'@pytest\.fixture\s+def\s+authenticated_client.*?yield client|return client'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, authenticated_client_fixture.strip(), content, flags=re.DOTALL)
            print("Updated authenticated_client fixture")
    
    if 'def authenticated_client_no_rate_limits' not in content:
        content += combined_fixture
        print("Added authenticated_client_no_rate_limits fixture")
    
    # Write the updated content
    with open(conftest_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {conftest_path}")
    return True

if __name__ == "__main__":
    add_fixtures()
