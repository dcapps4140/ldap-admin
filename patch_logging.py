#!/usr/bin/env python3
import os
import sys
from unittest.mock import patch, Mock
import tempfile

def create_logging_patch():
    """Create a patch for logging."""
    patch_file = 'tests/logging_patch.py'
    
    patch_content = '''
# Logging patch for testing
import os
import sys
import logging
from unittest.mock import patch, Mock

# Create a logs directory in the project
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Define the test log file path
test_log_file = os.path.join(logs_dir, 'test.log')

# Create a patch for FileHandler
original_file_handler = logging.FileHandler

def patched_file_handler(filename, *args, **kwargs):
    """Patch FileHandler to use a file in the project directory."""
    if filename == '/var/log/ldap-admin.log':
        return original_file_handler(test_log_file, *args, **kwargs)
    return original_file_handler(filename, *args, **kwargs)

# Apply the patch
logging.FileHandler = patched_file_handler

print(f"Logging patched to use {test_log_file}")
'''
    
    with open(patch_file, 'w') as f:
        f.write(patch_content)
    
    print(f"Created {patch_file}")
    
    # Create logs directory
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    print(f"Created logs directory: {logs_dir}")
    
    # Update conftest.py to use the patch
    conftest_path = 'tests/conftest.py'
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    if 'logging_patch' not in content:
        # Add import at the top
        import_line = 'import pytest\n'
        new_import = 'import pytest\nimport tests.logging_patch\n'
        
        if 'flask_limiter_patch' in content:
            # Already has flask_limiter_patch
            new_import = 'import pytest\nimport tests.flask_limiter_patch\nimport tests.logging_patch\n'
            content = content.replace('import pytest\nimport tests.flask_limiter_patch\n', new_import)
        else:
            content = content.replace(import_line, new_import)
        
        with open(conftest_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {conftest_path} to use the logging patch")
    
    return True

if __name__ == "__main__":
    create_logging_patch()
