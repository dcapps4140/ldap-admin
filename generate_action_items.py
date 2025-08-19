#!/usr/bin/env python3
# File: generate_action_items.py

import os
import re
import sys
from datetime import datetime
import json
from collections import Counter

def parse_test_output(file_path):
    """Parse pytest output file and extract test results."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract failed tests with reasons
    failed_tests = []
    error_pattern = re.compile(r'(FAILED|ERROR) ([^\s]+).*?\n(.*?)(?=\n\n|\Z)', re.DOTALL)
    for match in error_pattern.finditer(content):
        test_type = match.group(1)  # FAILED or ERROR
        test_name = match.group(2)
        error_message = match.group(3).strip()
        
        # Extract the most relevant part of the error message
        short_error = error_message.split('\n')[-1] if '\n' in error_message else error_message
        if len(short_error) > 100:
            short_error = short_error[:97] + '...'
        
        failed_tests.append({
            'type': test_type,
            'name': test_name,
            'error': short_error,
            'full_error': error_message
        })
    
    # Extract warnings
    warnings = []
    warning_pattern = re.compile(r'warnings summary.*?\n(.*?)(?=\n\n|\Z)', re.DOTALL)
    warning_match = warning_pattern.search(content)
    if warning_match:
        warning_text = warning_match.group(1)
        for line in warning_text.split('\n'):
            if line.strip() and not line.startswith('--') and not line.startswith('warnings summary'):
                warnings.append(line.strip())
    
    return {
        'failed_tests': failed_tests,
        'warnings': warnings
    }

def categorize_failures(failed_tests):
    """Categorize test failures by type."""
    categories = {
        'missing_routes': [],
        'authentication': [],
        'rate_limiting': [],
        'api_issues': [],
        'other': []
    }
    
    for test in failed_tests:
        error = test['error'].lower()
        name = test['name'].lower()
        
        if '404' in error or 'not found' in error:
            categories['missing_routes'].append(test)
        elif '429' in error or 'too many requests' in error or 'rate limit' in error:
            categories['rate_limiting'].append(test)
        elif '401' in error or '403' in error or 'unauthorized' in error or 'permission' in error or 'authentication' in name:
            categories['authentication'].append(test)
        elif 'api' in name or '/api/' in error:
            categories['api_issues'].append(test)
        else:
            categories['other'].append(test)
    
    return categories

def generate_action_items(log_dir='test_logs'):
    """Generate action items from test results."""
    # Find the latest test output file
    log_files = []
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.startswith('test-output-') and file.endswith('.txt'):
                log_files.append(os.path.join(log_dir, file))
    
    if not log_files:
        return "No test logs found in directory: " + log_dir
    
    latest_log = max(log_files, key=os.path.getmtime)
    results = parse_test_output(latest_log)
    
    # Categorize failures
    categories = categorize_failures(results['failed_tests'])
    
    # Generate action items
    action_items = []
    action_items.append("# Test Action Items")
    action_items.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    action_items.append(f"Based on: {os.path.basename(latest_log)}")
    action_items.append("")
    
    # High priority items
    action_items.append("## High Priority")
    
    # Rate limiting issues
    if categories['rate_limiting']:
        action_items.append("### 1. Fix Rate Limiting Issues")
        action_items.append("```python")
        action_items.append("# Add to tests/conftest.py")
        action_items.append("@pytest.fixture")
        action_items.append("def disable_rate_limits(app):")
        action_items.append("    app.config['RATELIMIT_ENABLED'] = False")
        action_items.append("    yield")
        action_items.append("    app.config['RATELIMIT_ENABLED'] = True")
        action_items.append("```")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in categories['rate_limiting']:
            action_items.append(f"- {test['name']}: {test['error']}")
        action_items.append("")
    
    # Authentication issues
    if categories['authentication']:
        action_items.append("### 2. Fix Authentication Issues")
        action_items.append("- Update tests to use authenticated client")
        action_items.append("- Ensure proper session handling")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in categories['authentication']:
            action_items.append(f"- {test['name']}: {test['error']}")
        action_items.append("")
    
    # API issues
    if categories['api_issues']:
        action_items.append("### 3. Fix API Issues")
        action_items.append("- Update API tests to handle authentication")
        action_items.append("- Ensure proper response handling")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in categories['api_issues']:
            action_items.append(f"- {test['name']}: {test['error']}")
        action_items.append("")
    
    # Medium priority items
    action_items.append("## Medium Priority")
    
    # Missing routes
    if categories['missing_routes']:
        action_items.append("### 1. Implement Missing Routes")
        
        # Group by route pattern
        route_patterns = []
        for test in categories['missing_routes']:
            error = test['error']
            route_match = re.search(r"'(/[^']*)'", error)
            if route_match:
                route_patterns.append(route_match.group(1))
        
        # Count occurrences of each route
        route_counts = Counter(route_patterns)
        
        for route, count in route_counts.most_common():
            action_items.append(f"- Implement route: `{route}` (affects {count} tests)")
        
        action_items.append("")
        action_items.append("Affected tests:")
        for test in categories['missing_routes'][:5]:  # Show only first 5
            action_items.append(f"- {test['name']}: {test['error']}")
        
        if len(categories['missing_routes']) > 5:
            action_items.append(f"- ... and {len(categories['missing_routes']) - 5} more")
        
        action_items.append("")
    
    # Other issues
    if categories['other']:
        action_items.append("### 2. Fix Other Test Issues")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in categories['other']:
            action_items.append(f"- {test['name']}: {test['error']}")
        action_items.append("")
    
    # Low priority items
    action_items.append("## Low Priority")
    
    # Warnings
    if results['warnings']:
        action_items.append("### 1. Address Warnings")
        unique_warnings = set(results['warnings'])
        for warning in unique_warnings:
            action_items.append(f"- {warning}")
        action_items.append("")
    
    # Quick wins
    action_items.append("### 2. Quick Wins")
    action_items.append("- Add `@pytest.mark.skip` to tests for unimplemented features")
    action_items.append("- Update test assertions to match actual application behavior")
    action_items.append("- Add more specific error messages to failing tests")
    action_items.append("")
    
    # Implementation plan
    action_items.append("## Implementation Plan")
    action_items.append("")
    action_items.append("1. **Fix rate limiting in tests first** - This will unblock many tests")
    action_items.append("2. **Update authentication handling** - Ensure tests can authenticate properly")
    action_items.append("3. **Fix API tests** - Update to handle authentication and proper responses")
    action_items.append("4. **Implement missing routes** - Or skip tests for routes not yet implemented")
    action_items.append("5. **Address remaining issues** - Fix other test failures")
    action_items.append("")
    
    return '\n'.join(action_items)

if __name__ == "__main__":
    # Check if a directory was provided
    log_dir = 'test_logs'
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
    
    action_items = generate_action_items(log_dir)
    print(action_items)
    
    # Save to file
    with open('test_action_items.md', 'w') as f:
        f.write(action_items)
    
    print(f"\nAction items saved to test_action_items.md")
    sys.exit(0)