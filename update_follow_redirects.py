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

def update_follow_redirects():
    """Update tests to follow redirects."""
    file_path = 'tests/test_api_routes.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add follow_redirects=True to all HTTP method calls
    new_content = re.sub(
        r'(authenticated_client\.(get|post|put|delete|patch)\([^)]*)',
        r'\1, follow_redirects=True',
        content
    )
    
    # Fix any double follow_redirects
    new_content = new_content.replace('follow_redirects=True, follow_redirects=True', 'follow_redirects=True')
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")
    return True

if __name__ == "__main__":
    update_follow_redirects()
