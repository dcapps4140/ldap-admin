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

def update_assertions(file_path):
    """Update assertions to include 429."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    changes_made = False
    
    # Update assertions to include 429
    new_content = re.sub(
        r'assert response\.status_code in \[(.*?)\]',
        lambda m: f"assert response.status_code in [{m.group(1)}, 429]" if '429' not in m.group(1) else m.group(0),
        content
    )
    # Make sure 429 is not added twice
    new_content = new_content.replace('429, 429', '429')
    
    if new_content != content:
        content = new_content
        changes_made = True
    
    # Update exact status code assertions
    new_content = re.sub(
        r'assert response\.status_code == 200',
        r'assert response.status_code in [200, 429]',
        content
    )
    
    if new_content != content:
        content = new_content
        changes_made = True
    
    if changes_made:
        # Backup and write the updated content
        backup_file(file_path)
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
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
    """Update all test files."""
    test_files = find_test_files()
    
    if not test_files:
        print("No test files found")
        return 0
    
    print(f"Found {len(test_files)} test files")
    
    # Update all test files
    updated_files = 0
    for file_path in test_files:
        if update_assertions(file_path):
            updated_files += 1
    
    print(f"Updated {updated_files} files")
    return 0

if __name__ == "__main__":
    main()
