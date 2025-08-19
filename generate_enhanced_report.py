#!/usr/bin/env python3
import os
import re
import sys
import json
from datetime import datetime

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
    
    # Extract test run time
    time_match = re.search(r'in (\d+\.\d+)s', content)
    run_time = float(time_match.group(1)) if time_match else 0
    
    # Extract failed tests
    failed_tests = []
    for match in re.finditer(r'FAILED ([^\s]+)', content):
        failed_tests.append(match.group(1))
    
    # Extract error tests
    error_tests = []
    for match in re.finditer(r'ERROR ([^\s]+)', content):
        error_tests.append(match.group(1))
    
    # Extract coverage info if available
    coverage_match = re.search(r'Coverage HTML written to dir (\w+)', content)
    coverage_dir = coverage_match.group(1) if coverage_match else None
    
    return {
        'total': total_tests,
        'passed': passed,
        'failed': failed,
        'warnings': warnings,
        'errors': errors,
        'run_time': run_time,
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'coverage_dir': coverage_dir
    }

def parse_coverage_data(coverage_dir):
    """Parse coverage data from coverage JSON file."""
    if not coverage_dir or not os.path.exists(coverage_dir):
        return None
    
    json_file = os.path.join(coverage_dir, 'coverage.json')
    if not os.path.exists(json_file):
        return None
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        total_statements = 0
        covered_statements = 0
        
        for file_data in data['files'].values():
            total_statements += file_data['summary']['num_statements']
            covered_statements += file_data['summary']['covered_statements']
        
        coverage_percent = (covered_statements / total_statements * 100) if total_statements > 0 else 0
        
        return {
            'total_statements': total_statements,
            'covered_statements': covered_statements,
            'coverage_percent': coverage_percent
        }
    except Exception as e:
        print(f"Error parsing coverage data: {e}")
        return None

def generate_report(log_dir='test_logs'):
    """Generate a test summary report from all test logs."""
    report = []
    report.append("# Enhanced Test Summary Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Find all test output files
    log_files = []
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.startswith('test-output-') and file.endswith('.txt'):
                log_files.append(os.path.join(log_dir, file))
    
    if not log_files:
        report.append("No test logs found in directory: " + log_dir)
        return '\n'.join(report)
    
    log_files.sort(key=lambda x: os.path.getmtime(x))
    
    # Get the latest test run
    latest_log = log_files[-1]
    latest_results = parse_test_output(latest_log)
    
    report.append("## Latest Test Run")
    report.append(f"- **File**: {os.path.basename(latest_log)}")
    report.append(f"- **Total Tests**: {latest_results['total']}")
    
    if latest_results['total'] > 0:
        pass_rate = latest_results['passed']/latest_results['total']*100
        report.append(f"- **Passed**: {latest_results['passed']} ({pass_rate:.1f}%)")
        report.append(f"- **Failed**: {latest_results['failed']} ({latest_results['failed']/latest_results['total']*100:.1f}%)")
    else:
        report.append(f"- **Passed**: {latest_results['passed']}")
        report.append(f"- **Failed**: {latest_results['failed']}")
    
    report.append(f"- **Warnings**: {latest_results['warnings']}")
    report.append(f"- **Errors**: {latest_results['errors']}")
    report.append(f"- **Run Time**: {latest_results['run_time']:.2f}s")
    
    # Add coverage info if available
    coverage_data = parse_coverage_data(latest_results['coverage_dir'])
    if coverage_data:
        report.append(f"- **Code Coverage**: {coverage_data['coverage_percent']:.1f}% ({coverage_data['covered_statements']}/{coverage_data['total_statements']} statements)")
    
    report.append("")
    
    if latest_results['failed_tests']:
        report.append("### Failed Tests")
        for test in latest_results['failed_tests']:
            report.append(f"- {test}")
        report.append("")
    
    if latest_results['error_tests']:
        report.append("### Error Tests")
        for test in latest_results['error_tests']:
            report.append(f"- {test}")
        report.append("")
    
    # Show test trend
    report.append("## Test Trend")
    report.append("| Run | Total | Passed | Failed | Errors | Pass Rate |")
    report.append("|-----|-------|--------|--------|--------|-----------|")
    
    for i, log_file in enumerate(log_files[-5:]):  # Show last 5 runs
        results = parse_test_output(log_file)
        pass_rate = results['passed']/results['total']*100 if results['total'] > 0 else 0
        report.append(f"| {i+1} | {results['total']} | {results['passed']} | {results['failed']} | {results['errors']} | {pass_rate:.1f}% |")
    
    report.append("")
    report.append("## Test Categories")
    
    # Analyze test categories
    test_categories = {
        'Authentication': [],
        'User Management': [],
        'Group Management': [],
        'API': [],
        'Basic': [],
        'Other': []
    }
    
    # Get all test files
    test_files = []
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    # Categorize tests
    for file in test_files:
        with open(file, 'r') as f:
            content = f.read()
        
        test_count = len(re.findall(r'def test_', content))
        
        if 'authentication' in file.lower():
            test_categories['Authentication'].append((file, test_count))
        elif 'user' in file.lower():
            test_categories['User Management'].append((file, test_count))
        elif 'group' in file.lower():
            test_categories['Group Management'].append((file, test_count))
        elif 'api' in file.lower():
            test_categories['API'].append((file, test_count))
        elif 'basic' in file.lower():
            test_categories['Basic'].append((file, test_count))
        else:
            test_categories['Other'].append((file, test_count))
    
    # Report on test categories
    for category, files in test_categories.items():
        if files:
            report.append(f"### {category}")
            report.append(f"- **Test Files**: {len(files)}")
            report.append(f"- **Test Count**: {sum(count for _, count in files)}")
            report.append("- **Files**:")
            for file, count in files:
                report.append(f"  - {os.path.basename(file)} ({count} tests)")
            report.append("")
    
    report.append("## Recommendations")
    report.append("")
    
    # Add recommendations based on test results
    if latest_results['failed'] > 0:
        report.append("1. **Fix failing tests**: Address the specific test failures listed above.")
    
    if latest_results['warnings'] > 0:
        report.append("2. **Address warnings**: Review and fix the warnings in the test output.")
    
    if latest_results['errors'] > 0:
        report.append("3. **Fix test errors**: Some tests have setup or execution errors that need to be fixed.")
    
    # Add coverage recommendations
    if coverage_data and coverage_data['coverage_percent'] < 80:
        report.append("4. **Improve code coverage**: Current coverage is below 80%. Add more tests to cover untested code.")
    
    # Add general recommendations
    report.append("5. **Update tests for missing routes**: Some tests are failing because they're testing routes that don't exist yet.")
    report.append("6. **Handle rate limiting**: Configure tests to handle or disable rate limiting during testing.")
    report.append("7. **Improve test coverage**: Focus on testing the core functionality of your application.")
    
    return '\n'.join(report)

if __name__ == "__main__":
    # Check if a directory was provided
    log_dir = 'test_logs'
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
    
    report = generate_report(log_dir)
    print(report)
    
    # Save report to file
    with open('enhanced_test_report.md', 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to enhanced_test_report.md")
