
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
