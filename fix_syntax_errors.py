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

def fix_authentication_file():
    """Fix syntax error in test_authentication.py."""
    file_path = 'tests/test_authentication.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the syntax error with escaped quotes
    new_content = content.replace("b\\'username\\'", "b'username'")
    new_content = new_content.replace("b\\'password\\'", "b'password'")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed syntax error in {file_path}")
    return True

def fix_indentation_errors():
    """Fix indentation errors in test files."""
    files_to_fix = [
        'tests/test_group_management.py',
        'tests/test_user_management.py'
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found")
            continue
        
        # Backup the file
        backup_file(file_path)
        
        # Read the file line by line to fix indentation
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Fix indentation
        fixed_lines = []
        in_class = False
        class_indent = 0
        
        for line in lines:
            # Check if we're entering a class definition
            if line.strip().startswith('class ') and line.strip().endswith(':'):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue
            
            # Check if we're in a class and this is a method definition
            if in_class and line.strip().startswith('def test_'):
                # Make sure method is indented properly
                method_indent = class_indent + 4
                stripped_line = line.lstrip()
                fixed_line = ' ' * method_indent + stripped_line
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        # Write the fixed content
        with open(file_path, 'w') as f:
            f.writelines(fixed_lines)
        
        print(f"Fixed indentation in {file_path}")
    
    return True

def main():
    """Fix syntax errors in test files."""
    fix_authentication_file()
    fix_indentation_errors()
    
    return 0

if __name__ == "__main__":
    main()
