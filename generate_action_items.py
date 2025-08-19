#!/usr/bin/env python3
# File: generate_action_items.py

import os
import re
import sys
from datetime import datetime
from collections import Counter, defaultdict

def parse_test_output(file_path):
    """Parse pytest output file and extract test results."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract test session info
    session_match = re.search(r'collected (\d+) items', content)
    total_tests = int(session_match.group(1)) if session_match else 0
    
    # Extract summary
    summary_match = re.search(r'(\d+) failed, (\d+) passed', content)
    if summary_match:
        failed = int(summary_match.group(1))
        passed = int(summary_match.group(2))
    else:
        # Try alternative pattern
        alt_match = re.search(r'(\d+) passed(, \d+ warnings)?', content)
        if alt_match:
            failed = 0
            passed = int(alt_match.group(1))
        else:
            failed = 0
            passed = 0
    
    # Extract warnings
    warnings_match = re.search(r'(\d+) warnings', content)
    warnings = int(warnings_match.group(1)) if warnings_match else 0
    
    # Extract errors
    errors_match = re.search(r'(\d+) errors', content)
    errors = int(errors_match.group(1)) if errors_match else 0
    
    # Extract failed tests with details
    failed_tests = []
    failure_blocks = re.finditer(r'=+ FAILURES =+\n(.*?)(?=\n=+|$)', content, re.DOTALL)
    
    for block in failure_blocks:
        failure_text = block.group(1)
        test_failures = re.finditer(r'_{10,}\s+(.*?)\s+_{10,}.*?E\s+(.*?)(?=\n\n|\n_{10,}|$)', failure_text, re.DOTALL)
        
        for match in test_failures:
            test_name = match.group(1).strip()
            error_message = match.group(2).strip()
            
            # Extract assertion error details
            assertion_match = re.search(r'assert (.*)', error_message)
            assertion_detail = assertion_match.group(1) if assertion_match else ""
            
            # Extract status code if present
            status_code_match = re.search(r'(\d{3}) (?:in|==) ', error_message)
            status_code = status_code_match.group(1) if status_code_match else None
            
            failed_tests.append({
                'name': test_name,
                'error': error_message,
                'assertion': assertion_detail,
                'status_code': status_code
            })
    
    # Extract error tests
    error_tests = []
    error_blocks = re.finditer(r'=+ ERRORS =+\n(.*?)(?=\n=+|$)', content, re.DOTALL)
    
    for block in error_blocks:
        error_text = block.group(1)
        test_errors = re.finditer(r'_{10,}\s+(.*?)\s+_{10,}.*?E\s+(.*?)(?=\n\n|\n_{10,}|$)', error_text, re.DOTALL)
        
        for match in test_errors:
            test_name = match.group(1).strip()
            error_message = match.group(2).strip()
            
            error_tests.append({
                'name': test_name,
                'error': error_message
            })
    
    # Extract warning details
    warning_details = []
    warning_block = re.search(r'=+ warnings summary =+(.*?)(?=\n=+|$)', content, re.DOTALL)
    if warning_block:
        warning_text = warning_block.group(1)
        for line in warning_text.split('\n'):
            if line.strip() and not line.startswith('--') and not line.startswith('warnings summary'):
                warning_details.append(line.strip())
    
    return {
        'total': total_tests,
        'passed': passed,
        'failed': failed,
        'warnings': warnings,
        'errors': errors,
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'warning_details': warning_details
    }

def analyze_test_failures(test_results):
    """Analyze test failures to identify patterns and issues."""
    analysis = {
        'status_code_issues': defaultdict(list),
        'missing_routes': [],
        'rate_limiting_issues': [],
        'authentication_issues': [],
        'assertion_issues': [],
        'fixture_issues': [],
        'other_issues': []
    }
    
    # Analyze failed tests
    for test in test_results['failed_tests']:
        error = test['error'].lower()
        name = test['name'].lower()
        
        # Check for status code issues
        if test['status_code']:
            analysis['status_code_issues'][test['status_code']].append(test)
        
        # Check for missing routes (404)
        elif '404' in error or 'not found' in error:
            analysis['missing_routes'].append(test)
        
        # Check for rate limiting issues (429)
        elif '429' in error or 'too many requests' in error:
            analysis['rate_limiting_issues'].append(test)
        
        # Check for authentication issues
        elif any(x in error for x in ['401', '403', 'unauthorized', 'permission', 'authentication']):
            analysis['authentication_issues'].append(test)
        
        # Check for assertion issues
        elif 'assert' in error:
            analysis['assertion_issues'].append(test)
        
        # Other issues
        else:
            analysis['other_issues'].append(test)
    
    # Analyze error tests
    for test in test_results['error_tests']:
        error = test['error'].lower()
        
        # Check for fixture issues
        if 'fixture' in error:
            analysis['fixture_issues'].append(test)
        else:
            analysis['other_issues'].append(test)
    
    return analysis

def extract_routes_from_failures(failures):
    """Extract route patterns from test failures."""
    routes = []
    for test in failures:
        error = test['error']
        # Look for routes in single quotes
        route_matches = re.finditer(r"'(/[^']*)'", error)
        for match in route_matches:
            routes.append(match.group(1))
        
        # Look for routes in error messages with status codes
        status_route_matches = re.finditer(r"(GET|POST|PUT|DELETE) ([^ ]+)", error)
        for match in status_route_matches:
            routes.append(match.group(2))
    
    return routes

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
    analysis = analyze_test_failures(results)
    
    # Generate action items
    action_items = []
    action_items.append("# Test Action Items")
    action_items.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    action_items.append(f"Based on: {os.path.basename(latest_log)}")
    action_items.append("")
    action_items.append(f"**Test Summary**: {results['passed']} passed, {results['failed']} failed, {results['errors']} errors, {results['warnings']} warnings")
    action_items.append("")
    
    # High priority items
    action_items.append("## High Priority Items")
    
    # Rate limiting issues
    if analysis['rate_limiting_issues']:
        action_items.append("### 1. Fix Rate Limiting Issues")
        action_items.append("Add rate limiting fixture to disable rate limits during testing:")
        action_items.append("```python")
        action_items.append("# Add to tests/conftest.py")
        action_items.append("@pytest.fixture")
        action_items.append("def disable_rate_limits(app):")
        action_items.append("    original_enabled = app.config.get('RATELIMIT_ENABLED', True)")
        action_items.append("    app.config['RATELIMIT_ENABLED'] = False")
        action_items.append("    yield")
        action_items.append("    app.config['RATELIMIT_ENABLED'] = original_enabled")
        action_items.append("```")
        action_items.append("")
        action_items.append("Use the fixture in your tests:")
        action_items.append("```python")
        action_items.append("@pytest.mark.usefixtures('disable_rate_limits')")
        action_items.append("def test_login(client):")
        action_items.append("    # Your test code here")
        action_items.append("```")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in analysis['rate_limiting_issues']:
            action_items.append(f"- {test['name']}")
        action_items.append("")
    
    # Fixture issues
    if analysis['fixture_issues']:
        action_items.append("### 2. Fix Missing Fixtures")
        
        # Group by fixture name
        fixture_names = []
        for test in analysis['fixture_issues']:
            fixture_match = re.search(r"fixture '([^']+)' not found", test['error'])
            if fixture_match:
                fixture_names.append(fixture_match.group(1))
        
        fixture_counts = Counter(fixture_names)
        
        for fixture, count in fixture_counts.most_common():
            action_items.append(f"- Add fixture `{fixture}` (needed by {count} tests)")
        
        action_items.append("")
        action_items.append("Affected tests:")
        for test in analysis['fixture_issues']:
            action_items.append(f"- {test['name']}: {test['error']}")
        action_items.append("")
    
    # Status code issues
    if analysis['status_code_issues']:
        action_items.append("### 3. Fix Status Code Issues")
        
        for status_code, tests in analysis['status_code_issues'].items():
            if status_code == '404':
                continue  # We'll handle 404s separately
                
            action_items.append(f"#### Status Code {status_code} Issues")
            
            if status_code == '302':
                action_items.append("These tests are getting redirected (302). You need to:")
                action_items.append("- Use authenticated client for API tests")
                action_items.append("- Update assertions to accept 302 as valid response")
                action_items.append("- Use `follow_redirects=True` in client requests")
            elif status_code == '429':
                action_items.append("These tests are hitting rate limits (429). You need to:")
                action_items.append("- Use the `disable_rate_limits` fixture")
            elif status_code in ['401', '403']:
                action_items.append("These tests are failing authentication (401/403). You need to:")
                action_items.append("- Use authenticated client for these tests")
                action_items.append("- Ensure proper session setup")
            
            action_items.append("")
            action_items.append("Affected tests:")
            for test in tests:
                action_items.append(f"- {test['name']}")
            action_items.append("")
    
    # Medium priority items
    action_items.append("## Medium Priority Items")
    
    # Missing routes
    if analysis['missing_routes']:
        action_items.append("### 1. Handle Missing Routes")
        
        # Extract routes from errors
        routes = extract_routes_from_failures(analysis['missing_routes'])
        route_counts = Counter(routes)
        
        if route_counts:
            action_items.append("Either implement these missing routes or skip the tests:")
            for route, count in route_counts.most_common():
                action_items.append(f"- Route `{route}` (affects {count} tests)")
            
            action_items.append("")
            action_items.append("To skip tests for unimplemented routes:")
            action_items.append("```python")
            action_items.append("@pytest.mark.skip(reason=\"Route not implemented yet\")")
            action_items.append("def test_unimplemented_route(client):")
            action_items.append("    # Test code")
            action_items.append("```")
        
        action_items.append("")
        action_items.append("Affected tests:")
        for test in analysis['missing_routes'][:5]:  # Show only first 5
            action_items.append(f"- {test['name']}")
        
        if len(analysis['missing_routes']) > 5:
            action_items.append(f"- ... and {len(analysis['missing_routes']) - 5} more")
        
        action_items.append("")
    
    # Authentication issues
    if analysis['authentication_issues']:
        action_items.append("### 2. Fix Authentication Issues")
        action_items.append("Update tests to use authenticated client:")
        action_items.append("```python")
        action_items.append("def test_protected_route(authenticated_client):")
        action_items.append("    response = authenticated_client.get('/protected-route')")
        action_items.append("    assert response.status_code == 200")
        action_items.append("```")
        action_items.append("")
        action_items.append("Or manually set up authentication:")
        action_items.append("```python")
        action_items.append("def test_protected_route(client):")
        action_items.append("    with client.session_transaction() as sess:")
        action_items.append("        sess['user'] = 'testuser'")
        action_items.append("        sess['authenticated'] = True")
        action_items.append("    response = client.get('/protected-route')")
        action_items.append("    assert response.status_code == 200")
        action_items.append("```")
        action_items.append("")
        action_items.append("Affected tests:")
        for test in analysis['authentication_issues']:
            action_items.append(f"- {test['name']}")
        action_items.append("")
    
    # Assertion issues
    if analysis['assertion_issues']:
        action_items.append("### 3. Fix Assertion Issues")
        action_items.append("Update assertions to match actual application behavior:")
        action_items.append("")
        
        # Group by common assertion patterns
        assertion_patterns = defaultdict(list)
        for test in analysis['assertion_issues']:
            if test['assertion']:
                assertion_patterns[test['assertion']].append(test)
        
        for assertion, tests in assertion_patterns.items():
            if len(tests) > 1:  # Only show patterns affecting multiple tests
                action_items.append(f"#### Pattern: `{assertion}`")
                action_items.append(f"Affects {len(tests)} tests. Example fix:")
                
                if '404 in' in assertion:
                    action_items.append("```python")
                    action_items.append("# Change this:")
                    action_items.append("assert response.status_code in [200, 302]")
                    action_items.append("")
                    action_items.append("# To this:")
                    action_items.append("assert response.status_code in [200, 302, 404]  # Include 404 if route not implemented yet")
                    action_items.append("# Or skip the test:")
                    action_items.append("@pytest.mark.skip(reason=\"Route not implemented yet\")")
                    action_items.append("```")
                elif '429 in' in assertion:
                    action_items.append("```python")
                    action_items.append("# Add rate limit fixture:")
                    action_items.append("@pytest.mark.usefixtures('disable_rate_limits')")
                    action_items.append("def test_function(client):")
                    action_items.append("    # Test code")
                    action_items.append("```")
                else:
                    action_items.append("```python")
                    action_items.append("# Review and update the assertion to match actual behavior")
                    action_items.append("```")
                
                action_items.append("")
                action_items.append("Affected tests:")
                for test in tests[:3]:  # Show only first 3
                    action_items.append(f"- {test['name']}")
                
                if len(tests) > 3:
                    action_items.append(f"- ... and {len(tests) - 3} more")
                
                action_items.append("")
    
    # Low priority items
    action_items.append("## Low Priority Items")
    
    # Warnings
    if results['warning_details']:
        action_items.append("### 1. Address Warnings")
        
        # Group warnings by type
        warning_types = defaultdict(list)
        for warning in results['warning_details']:
            # Extract warning type
            warning_match = re.search(r': ([^:]+):', warning)
            warning_type = warning_match.group(1) if warning_match else "Other"
            warning_types[warning_type].append(warning)
        
        for warning_type, warnings_list in warning_types.items():
            action_items.append(f"#### {warning_type} Warnings")
            
            # Special handling for common warnings
            if warning_type == "DeprecationWarning" and any("'flask.Markup' is deprecated" in w for w in warnings_list):
                action_items.append("Fix Flask Markup deprecation warnings by adding to pytest.ini:")
                action_items.append("```ini")
                action_items.append("[pytest]")
                action_items.append("filterwarnings =")
                action_items.append("    ignore:'flask.Markup' is deprecated:DeprecationWarning")
                action_items.append("```")
            elif warning_type == "UserWarning" and any("in-memory storage for tracking rate limits" in w for w in warnings_list):
                action_items.append("Configure a proper storage backend for Flask-Limiter:")
                action_items.append("```python")
                action_items.append("limiter = Limiter(")
                action_items.append("    get_remote_address,")
                action_items.append("    app=app,")
                action_items.append("    storage_uri=\"redis\\://127.0.0.1:6379\",")
                action_items.append(")")
                action_items.append("```")
            else:
                # Show unique warnings (up to 3)
                unique_warnings = set(warnings_list)
                for warning in list(unique_warnings)[:3]:
                    action_items.append(f"- {warning}")
                
                if len(unique_warnings) > 3:
                    action_items.append(f"- ... and {len(unique_warnings) - 3} more")
            
            action_items.append("")
    
    # Other issues
    if analysis['other_issues']:
        action_items.append("### 2. Fix Other Issues")
        action_items.append("Miscellaneous issues that need attention:")
        for test in analysis['other_issues']:
            action_items.append(f"- {test['name']}: {test['error'][:100]}...")
        action_items.append("")
    
    # Implementation plan
    action_items.append("## Implementation Plan")
    
    # Create prioritized plan based on actual issues found
    plan = []
    
    if analysis['rate_limiting_issues']:
        plan.append("1. **Fix rate limiting issues** - Add the disable_rate_limits fixture")
    
    if analysis['fixture_issues']:
        plan.append(f"{'1' if not plan else str(len(plan) + 1)}. **Add missing fixtures** - Create the required test fixtures")
    
    if analysis['status_code_issues'].get('302') or analysis['authentication_issues']:
        plan.append(f"{'1' if not plan else str(len(plan) + 1)}. **Fix authentication in tests** - Use authenticated client for protected routes")
    
    if analysis['missing_routes']:
        plan.append(f"{'1' if not plan else str(len(plan) + 1)}. **Handle missing routes** - Skip tests or implement the routes")
    
    if analysis['assertion_issues']:
        plan.append(f"{'1' if not plan else str(len(plan) + 1)}. **Fix assertion issues** - Update assertions to match actual behavior")
    
    if results['warning_details']:
        plan.append(f"{'1' if not plan else str(len(plan) + 1)}. **Address warnings** - Fix or suppress warnings")
    
    # Add plan to report
    for item in plan:
        action_items.append(item)
    
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
