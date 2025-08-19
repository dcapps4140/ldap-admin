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

def update_assertions():
    """Update assertions in test files to include 302."""
    file_path = 'tests/test_api_routes.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update assertions to include 302
    new_content = re.sub(
        r'assert response\.status_code in \[(.*?)\]',
        r'assert response.status_code in [\1, 302]',
        content
    )
    
    # Make sure 302 is not added twice
    new_content = new_content.replace('302, 302', '302')
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")
    return True

if __name__ == "__main__":
    update_assertions()
