#!/usr/bin/env python3
import os

def fix_report_script():
    """Fix the division by zero error in the report generation script."""
    script_path = 'generate_test_report.py'
    
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found")
        return False
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Fix the division by zero error
    fixed_content = content.replace(
        "report.append(f\"- **Passed**: {passed} ({passed/total*100:.1f}%)\")",
        "report.append(f\"- **Passed**: {passed} ({passed/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    fixed_content = fixed_content.replace(
        "report.append(f\"- **Failed**: {failed} ({failed/total*100:.1f}%)\")",
        "report.append(f\"- **Failed**: {failed} ({failed/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    fixed_content = fixed_content.replace(
        "report.append(f\"- **Skipped**: {skipped} ({skipped/total*100:.1f}%)\")",
        "report.append(f\"- **Skipped**: {skipped} ({skipped/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    fixed_content = fixed_content.replace(
        "report.append(f\"- **Error**: {error} ({error/total*100:.1f}%)\")",
        "report.append(f\"- **Error**: {error} ({error/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    fixed_content = fixed_content.replace(
        "pass_rate = data['passed'] / data['total'] * 100 if data['total'] > 0 else 0",
        "pass_rate = data['passed'] / data['total'] * 100 if data['total'] > 0 else 0.0"
    )
    
    fixed_content = fixed_content.replace(
        "print(f\"Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)\")",
        "print(f\"Summary: {passed}/{total} tests passed ({passed/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    fixed_content = fixed_content.replace(
        "print(f\"Failed: {failed}/{total} tests failed ({failed/total*100:.1f}%)\")",
        "print(f\"Failed: {failed}/{total} tests failed ({failed/total*100:.1f}% if total > 0 else 0.0}%)\")"
    )
    
    # Write the fixed content
    with open(script_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed {script_path}")
    return True

if __name__ == "__main__":
    fix_report_script()
