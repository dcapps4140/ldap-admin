#!/usr/bin/env python3
import os

def fix_indentation(file_path):
    """Fix indentation in a test file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Backup the file
    backup_path = f"{file_path}.bak"
    os.system(f"cp {file_path} {backup_path}")
    print(f"Created backup: {backup_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Fix indentation
    fixed_lines = []
    in_class = False
    class_indent = 0
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue
        
        # Check if we're entering a class definition
        if line.strip().startswith('class ') and line.strip().endswith(':'):
            in_class = True
            class_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Check if we're in a class
        if in_class:
            # Check if this is a decorator
            if line.strip().startswith('@'):
                # Indent decorator properly
                stripped_line = line.lstrip()
                fixed_line = ' ' * (class_indent + 4) + stripped_line
                fixed_lines.append(fixed_line)
            # Check if this is a method definition
            elif line.strip().startswith('def '):
                # Indent method properly
                stripped_line = line.lstrip()
                fixed_line = ' ' * (class_indent + 4) + stripped_line
                fixed_lines.append(fixed_line)
            else:
                # For other lines, preserve indentation
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed indentation in {file_path}")
    return True

def main():
    """Fix indentation errors in test files."""
    files_to_fix = [
        'tests/test_api_routes.py',
        'tests/test_authentication.py',
        'tests/test_authentication_no_rate_limits.py',
        'tests/test_authentication_rate_limits.py',
        'tests/test_group_management.py',
        'tests/test_user_management.py'
    ]
    
    for file_path in files_to_fix:
        fix_indentation(file_path)
    
    return 0

if __name__ == "__main__":
    main()
