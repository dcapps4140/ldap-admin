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

def fix_json_dumps():
    """Fix the follow_redirects parameter in json.dumps()."""
    file_path = 'tests/test_api_routes.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the json.dumps() call
    new_content = re.sub(
        r'json\.dumps\((.*?), follow_redirects=True\)',
        r'json.dumps(\1)',
        content
    )
    
    # Fix the post() call
    new_content = re.sub(
        r'(authenticated_client\.post\([^)]*)\)',
        r'\1, follow_redirects=True)',
        new_content
    )
    
    # Fix any double follow_redirects
    new_content = new_content.replace('follow_redirects=True, follow_redirects=True', 'follow_redirects=True')
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")
    return True

if __name__ == "__main__":
    fix_json_dumps()
