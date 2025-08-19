#!/usr/bin/env python3
import os
import shutil

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def fix_rate_limits():
    """Fix the disable_rate_limits fixture in conftest.py."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return False
    
    # Backup the file
    backup_file(conftest_path)
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic fixture with a simpler one
    updated_fixture = '''
@pytest.fixture(autouse=True)
def disable_rate_limits(app):
    """Disable rate limits for testing."""
    # Store original config
    original_enabled = app.config.get('RATELIMIT_ENABLED', True)
    
    # Disable rate limits
    app.config['RATELIMIT_ENABLED'] = False
    
    # Patch Flask-Limiter if it exists
    try:
        from flask_limiter import Limiter
        if hasattr(app, 'extensions'):
            for ext in app.extensions.values():
                if isinstance(ext, Limiter):
                    ext.enabled = False
    except (ImportError, AttributeError):
        pass
    
    yield
    
    # Restore original config
    app.config['RATELIMIT_ENABLED'] = original_enabled
'''
    
    # Find and replace the fixture
    import re
    pattern = r'@pytest\.fixture\(autouse=True\)\s*def\s+disable_rate_limits.*?yield'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, updated_fixture.strip(), content, flags=re.DOTALL)
        
        # Write the updated content
        with open(conftest_path, 'w') as f:
            f.write(new_content)
        
        print(f"Updated {conftest_path}")
        return True
    else:
        print("Could not find the disable_rate_limits fixture. Creating a new one.")
        
        # Add the fixture to the end of the file
        with open(conftest_path, 'a') as f:
            f.write(updated_fixture)
        
        print(f"Added fixture to {conftest_path}")
        return True

if __name__ == "__main__":
    fix_rate_limits()
