#!/usr/bin/env python3
import os
import re
from datetime import datetime
import markdown

def find_skipped_tests():
    """Find all skipped tests by examining test files."""
    skipped_tests = []
    
    # Find all test files
    test_files = []
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    for file_path in test_files:
        module_name = os.path.basename(file_path).replace('.py', '')
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Find all classes in the file
                classes = re.findall(r'class\s+(\w+)', content)
                
                # Find all skip decorators with reasons
                skip_matches = re.finditer(r'@pytest\.mark\.skip\(reason=[\'"]([^\'"]*)[\'"].*?\s+def\s+(test_\w+)', content, re.DOTALL)
                
                for match in skip_matches:
                    reason = match.group(1)
                    test_name = match.group(2)
                    
                    # Find which class this test belongs to (if any)
                    class_name = None
                    for cls in classes:
                        if f"class {cls}" in content[:match.start()]:
                            class_name = cls
                    
                    # Construct the full test name
                    if class_name:
                        full_test_name = f"{module_name}.{class_name}.{test_name}"
                    else:
                        full_test_name = f"{module_name}.{test_name}"
                    
                    skipped_tests.append((full_test_name, reason))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return skipped_tests

def categorize_action_items(skipped_tests):
    """Categorize action items based on skip reasons."""
    action_items = {
        "missing_routes": [],
        "missing_fixtures": [],
        "other": []
    }
    
    for test, reason in skipped_tests:
        if "route" in reason.lower() and ("not implemented" in reason.lower() or "returns 404" in reason.lower() or "doesn" in reason.lower()):
            action_items["missing_routes"].append((test, reason))
        elif "fixture" in reason.lower():
            action_items["missing_fixtures"].append((test, reason))
        else:
            action_items["other"].append((test, reason))
    
    return action_items

def extract_route_from_test_name(test_name):
    """Extract the route from a test name."""
    # Common patterns in test names
    patterns = [
        (r'test_get__(.+)', r'/\1'),
        (r'test_post__(.+)', r'/\1'),
        (r'test_put__(.+)', r'/\1'),
        (r'test_delete__(.+)', r'/\1'),
        (r'test_(.+)_form', r'/\1'),
        (r'test_(.+)_edit', r'/edit_\1'),
        (r'test_(.+)_delete', r'/delete_\1'),
        (r'test_(.+)_page', r'/\1'),
        (r'test_(.+)_required_routes', r'/\1'),
        (r'test_(.+)_request', r'/\1'),
    ]
    
    for pattern, replacement in patterns:
        match = re.search(pattern, test_name)
        if match:
            return re.sub(pattern, replacement, test_name)
    
    # Default: just convert underscores to slashes
    if 'test_' in test_name:
        route_part = test_name.split('test_')[-1]
        return f"/{route_part.replace('_', '/')}"
    
    return None

def generate_action_items():
    """Generate action items based on skipped tests."""
    skipped_tests = find_skipped_tests()
    action_items = categorize_action_items(skipped_tests)
    
    report = []
    report.append("# Action Items")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Missing routes
    if action_items["missing_routes"]:
        report.append("## Missing Routes to Implement")
        report.append("")
        report.append("| Route | Test | Reason |")
        report.append("| ----- | ---- | ------ |")
        
        for test, reason in action_items["missing_routes"]:
            route = extract_route_from_test_name(test.split('.')[-1])
            if route:
                report.append(f"| `{route}` | {test} | {reason} |")
            else:
                report.append(f"| Unknown | {test} | {reason} |")
        
        report.append("")
    
    # Missing fixtures
    if action_items["missing_fixtures"]:
        report.append("## Missing Fixtures to Implement")
        report.append("")
        report.append("| Test | Reason |")
        report.append("| ---- | ------ |")
        
        for test, reason in action_items["missing_fixtures"]:
            report.append(f"| {test} | {reason} |")
        
        report.append("")
    
    # Other issues
    if action_items["other"]:
        report.append("## Other Issues to Address")
        report.append("")
        report.append("| Test | Reason |")
        report.append("| ---- | ------ |")
        
        for test, reason in action_items["other"]:
            report.append(f"| {test} | {reason} |")
        
        report.append("")
    
    # Save Markdown report
    markdown_content = '\n'.join(report)
    with open('action_items.md', 'w') as f:
        f.write(markdown_content)
    
    print("Action items generated and saved to action_items.md")
    
    # Convert to HTML and save
    html_head = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Action Items</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #3498db; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        code { background-color: #f8f9fa; padding: 2px 4px; font-family: monospace; }
    </style>
</head>
<body>
"""
    
    html_foot = """
</body>
</html>
"""
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables'])
    
    # Combine parts
    full_html = html_head + html_content + html_foot
    
    # Save HTML file
    with open('action_items.html', 'w') as f:
        f.write(full_html)
    
    print("Action items also saved as HTML to action_items.html")
    
    # Return a summary
    return {
        "missing_routes": len(action_items["missing_routes"]),
        "missing_fixtures": len(action_items["missing_fixtures"]),
        "other": len(action_items["other"]),
        "total": len(skipped_tests)
    }

if __name__ == "__main__":
    summary = generate_action_items()
    print(f"\nSummary: {summary['total']} action items identified")
    print(f"- Missing Routes: {summary['missing_routes']}")
    print(f"- Missing Fixtures: {summary['missing_fixtures']}")
    print(f"- Other Issues: {summary['other']}")
