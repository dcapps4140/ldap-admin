#!/usr/bin/env python3
import os
import sys

def patch_flask_limiter():
    """Create a patch for Flask-Limiter."""
    patch_file = 'tests/flask_limiter_patch.py'
    
    patch_content = '''
# Flask-Limiter patch for testing
from unittest.mock import patch
import sys
import importlib

# Try to import Flask-Limiter
try:
    import flask_limiter
    
    # Save original Limiter class
    original_limiter = flask_limiter.Limiter
    
    # Create a patched Limiter class
    class PatchedLimiter(original_limiter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.enabled = False
        
        def limit(self, *args, **kwargs):
            # Return a no-op decorator when disabled
            if not self.enabled:
                return lambda f: f
            return super().limit(*args, **kwargs)
    
    # Replace the original Limiter with our patched version
    flask_limiter.Limiter = PatchedLimiter
    
    # Reload any modules that might have imported the original
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('flask_limiter'):
            importlib.reload(sys.modules[module_name])
    
    print("Flask-Limiter patched for testing")
except ImportError:
    print("Flask-Limiter not found, no patching needed")
'''
    
    with open(patch_file, 'w') as f:
        f.write(patch_content)
    
    # Create an __init__.py file to make it a proper package
    init_file = 'tests/__init__.py'
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Tests package\n')
    
    print(f"Created {patch_file}")
    
    # Create a conftest update to use the patch
    conftest_path = 'tests/conftest.py'
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    if 'flask_limiter_patch' not in content:
        # Add import at the top
        import_line = 'import pytest\n'
        new_import = 'import pytest\nimport tests.flask_limiter_patch\n'
        content = content.replace(import_line, new_import)
        
        with open(conftest_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {conftest_path} to use the patch")
    
    return True

if __name__ == "__main__":
    patch_flask_limiter()
