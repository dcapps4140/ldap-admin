"""
Test app factory for creating a test-specific Flask app.
"""
import os
import sys
import logging
from unittest.mock import patch, Mock

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Create a logs directory in the project
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Define the test log file path
test_log_file = os.path.join(logs_dir, 'test.log')

def create_test_app():
    """Create a test-specific Flask app."""
    # Patch logging.FileHandler to use a file in the project directory
    with patch('logging.FileHandler') as mock_handler:
        mock_handler.return_value = Mock()
        
        # Import the app
        import app as app_module
        
        # Get the Flask app instance
        if hasattr(app_module, 'app'):
            flask_app = app_module.app
        else:
            # Look for Flask app instance
            for attr_name in dir(app_module):
                attr = getattr(app_module, attr_name)
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
            'RATELIMIT_ENABLED': False,  # Disable rate limiting for testing
            'LOG_FILE': test_log_file,   # Use test log file
        })
        
        # Disable rate limiting if Flask-Limiter is used
        if hasattr(flask_app, 'extensions'):
            for ext_name, ext in flask_app.extensions.items():
                if 'limiter' in ext_name.lower():
                    try:
                        ext.enabled = False
                    except:
                        pass
        
        return flask_app
