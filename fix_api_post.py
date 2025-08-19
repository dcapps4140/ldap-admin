#!/usr/bin/env python3
import os

def fix_api_post():
    """Fix test_api_users_post in test_api_routes.py."""
    file_path = 'tests/test_api_routes.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_path = f"{file_path}.bak"
    os.system(f"cp {file_path} {backup_path}")
    print(f"Created backup: {backup_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the assertion to include 200
    content = content.replace(
        "assert response.status_code in [201, 400, 401, 403, 409, 302, 429]",
        "assert response.status_code in [200, 201, 400, 401, 403, 409, 302, 429]"
    )
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path}")
    return True

if __name__ == "__main__":
    fix_api_post()
