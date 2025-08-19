#!/usr/bin/env python3
import os

def fix_fstring():
    """Fix f-string syntax error in generate_test_report.py."""
    file_path = 'generate_test_report.py'
    
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
    
    # Fix the f-string syntax error
    content = content.replace(
        'report.append(f"- **Passed**: {passed} ({passed/total*100:.1f}% if total > 0 else 0.0}%)")',
        'report.append(f"- **Passed**: {passed} ({passed/total*100:.1f} if total > 0 else 0.0}%)")'
    )
    
    content = content.replace(
        'report.append(f"- **Failed**: {failed} ({failed/total*100:.1f}% if total > 0 else 0.0}%)")',
        'report.append(f"- **Failed**: {failed} ({failed/total*100:.1f} if total > 0 else 0.0}%)")'
    )
    
    content = content.replace(
        'report.append(f"- **Skipped**: {skipped} ({skipped/total*100:.1f}% if total > 0 else 0.0}%)")',
        'report.append(f"- **Skipped**: {skipped} ({skipped/total*100:.1f} if total > 0 else 0.0}%)")'
    )
    
    content = content.replace(
        'report.append(f"- **Error**: {error} ({error/total*100:.1f}% if total > 0 else 0.0}%)")',
        'report.append(f"- **Error**: {error} ({error/total*100:.1f} if total > 0 else 0.0}%)")'
    )
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed f-string syntax error in {file_path}")
    return True

if __name__ == "__main__":
    fix_fstring()
