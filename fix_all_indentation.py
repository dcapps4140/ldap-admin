#!/usr/bin/env python3
import os

def fix_indentation(file_path):
    """Fix indentation in a test file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Fix indentation
    fixed_lines = []
    in_class = False
    class_indent = 0
    method_indent = 0
    
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
        
        # Check if we're in a class and this is a method definition
        if in_class and line.strip().startswith('def test_'):
            # Make sure method is indented properly
            method_indent = class_indent + 4
            stripped_line = line.lstrip()
            fixed_line = ' ' * method_indent + stripped_line
            fixed_lines.append(fixed_line)
        elif in_class and line.strip() and not line.strip().startswith('@'):
            # For other lines inside a class, ensure proper indentation
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent <= class_indent:
                # This line is indented less than or equal to the class
                # It should be indented more
                stripped_line = line.lstrip()
                if stripped_line.startswith('def '):
                    # This is a method definition
                    fixed_line = ' ' * method_indent + stripped_line
                else:
                    # This is some other line in the class
                    fixed_line = ' ' * (method_indent + 4) + stripped_line
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Join lines back into content
    fixed_content = '\n'.join(fixed_lines)
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed indentation in {file_path}")
    return True

def find_test_files():
    """Find all test files."""
    test_files = []
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    return test_files

def main():
    """Fix indentation in all test files."""
    test_files = find_test_files()
    
    if not test_files:
        print("No test files found")
        return 0
    
    print(f"Found {len(test_files)} test files")
    
    # Fix indentation in all test files
    for file_path in test_files:
        fix_indentation(file_path)
    
    print("Fixed indentation in all test files")
    return 0

if __name__ == "__main__":
    main()
