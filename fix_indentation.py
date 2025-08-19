#!/usr/bin/env python3
import os
import re

def fix_indentation(file_path):
    """Fix indentation in a test file."""
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
        
        # Check if we're in a class and this is a method definition
        if in_class and line.strip().startswith('def test_'):
            # Make sure method is indented properly
            method_indent = class_indent + 4
            stripped_line = line.lstrip()
            fixed_line = ' ' * method_indent + stripped_line
            fixed_lines.append(fixed_line)
        else:
            # For other lines, preserve indentation relative to the method
            if in_class and len(fixed_lines) > 0 and fixed_lines[-1].strip().startswith('def test_'):
                # This is the line after a method definition
                prev_indent = len(fixed_lines[-1]) - len(fixed_lines[-1].lstrip())
                curr_indent = len(line) - len(line.lstrip())
                
                if curr_indent < prev_indent:
                    # This line is indented less than the method definition
                    # It should be indented at least as much as the method
                    stripped_line = line.lstrip()
                    fixed_line = ' ' * (prev_indent + 4) + stripped_line
                    fixed_lines.append(fixed_line)
                    continue
            
            fixed_lines.append(line)
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed indentation in {file_path}")
    return True

# Fix the file
fix_indentation('tests/test_other_routes_auto.py')
