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

def fix_client_reference():
    """Fix client reference in test_api_routes.py."""
    file_path = 'tests/test_api_routes.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace client with authenticated_client
    new_content = content.replace('response = client.post', 'response = authenticated_client.post')
    new_content = new_content.replace('response = client.get', 'response = authenticated_client.get')
    new_content = new_content.replace('response = client.delete', 'response = authenticated_client.delete')
    new_content = new_content.replace('response = client.put', 'response = authenticated_client.put')
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")
    return True

if __name__ == "__main__":
    fix_client_reference()
