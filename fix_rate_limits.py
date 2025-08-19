#!/usr/bin/env python3
import os
import re
import shutil

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def fix_rate_limits():
    """Update the disable_rate_limits fixture in conftest.py."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return False
    
    # Backup the file
    backup_file(conftest_path)
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    # Find the disable_rate_limits fixture
    fixture_match = re.search(r'@pytest\.fixture\s+def\s+disable_rate_limits.*?yield', content, re.DOTALL)
    
    if fixture_match:
        fixture_code = fixture_match.group(0)
        print("Found existing disable_rate_limits fixture:")
        print("=" * 40)
        print(fixture_code)
        print("=" * 40)
        
        # Update the fixture to be more robust
        updated_fixture = '''@pytest.fixture(autouse=True)
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
        app.extensions['limiter'].enabled = original_limiter_enabled'''
        
        # Update the content
        new_content = content.replace(fixture_code, updated_fixture)
        
        with open(conftest_path, 'w') as f:
            f.write(new_content)
        
        print("\nFixture updated successfully!")
        return True
    else:
        print("Could not find the disable_rate_limits fixture. Manual update required.")
        return False

if __name__ == "__main__":
    fix_rate_limits()
