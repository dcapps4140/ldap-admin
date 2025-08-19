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

def fix_client_typo(file_path):
    """Fix the authenticated_authenticated_client typo."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the typo
    new_content = content.replace('authenticated_authenticated_client', 'authenticated_client')
    
    if new_content != content:
        # Backup and write the updated content
        backup_file(file_path)
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Fixed typo in {file_path}")
        return True
    
    return False

def find_test_files():
    """Find all test files."""
    test_files = []
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    return test_files

def main():
    """Fix all test files."""
    test_files = find_test_files()
    
    if not test_files:
        print("No test files found")
        return 0
    
    print(f"Found {len(test_files)} test files")
    
    # Fix all test files
    fixed_files = 0
    for file_path in test_files:
        if fix_client_typo(file_path):
            fixed_files += 1
    
    print(f"Fixed {fixed_files} files")
    return 0

if __name__ == "__main__":
    main()
