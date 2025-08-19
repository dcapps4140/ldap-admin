#!/usr/bin/env python3
import subprocess
import re
import os
from datetime import datetime
import glob

def run_tests():
    """Run tests and capture output."""
    print("Running tests...")
    # Run with -v to get verbose output
    result = subprocess.run(['pytest', '-v'], capture_output=True, text=True)
    verbose_output = result.stdout
    
    return verbose_output, result.returncode

def extract_skip_reasons_from_files():
    """Extract skip reasons directly from test files."""
    skip_reasons = {}
    
    # Find all test files
    test_files = glob.glob('tests/test_*.py')
    
    for file_path in test_files:
        module_name = os.path.basename(file_path).replace('.py', '')
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Find all classes in the file
                class_matches = re.finditer(r'class\s+(\w+)', content)
                class_positions = {}
                for match in class_matches:
                    class_name = match.group(1)
                    class_positions[match.start()] = class_name
                
                # Find all skip decorators with reasons
                skip_matches = re.finditer(r'@pytest\.mark\.skip\(reason=[\'"]([^\'"]*)[\'"]', content)
                
                for match in skip_matches:
                    reason = match.group(1)
                    
                    # Find the test function that follows
                    func_match = re.search(r'def\s+(test_\w+)', content[match.end():])
                    if func_match:
                        test_name = func_match.group(1)
                        
                        # Find which class this test belongs to (if any)
                        class_name = None
                        for pos, name in sorted(class_positions.items()):
                            if pos < match.start():
                                class_name = name
                            else:
                                break
                        
                        # Construct the full test name
                        if class_name:
                            full_test_name = f"tests/{module_name}.py::{class_name}::{test_name}"
                        else:
                            full_test_name = f"tests/{module_name}.py::{test_name}"
                        
                        skip_reasons[full_test_name] = reason
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return skip_reasons

def parse_test_results(output):
    """Parse test output to extract results."""
    # Extract skip reasons from files
    skip_reasons = extract_skip_reasons_from_files()
    
    # Count test results
    passed = output.count(' PASSED ')
    failed = output.count(' FAILED ')
    skipped = output.count(' SKIPPED ')
    error = output.count(' ERROR ')
    
    total = passed + failed + skipped + error
    
    # Extract test names
    passed_tests = []
    for line in output.split('\n'):
        if ' PASSED ' in line:
            test_name = line.split(' PASSED ')[0].strip()
            passed_tests.append(test_name)
    
    failed_tests = []
    for line in output.split('\n'):
        if ' FAILED ' in line:
            test_name = line.split(' FAILED ')[0].strip()
            failed_tests.append(test_name)
    
    skipped_tests = []
    for line in output.split('\n'):
        if ' SKIPPED ' in line:
            test_name = line.split(' SKIPPED ')[0].strip()
            reason = skip_reasons.get(test_name, "Route not implemented yet or missing fixture")
            skipped_tests.append((test_name, reason))
    
    error_tests = []
    for line in output.split('\n'):
        if ' ERROR ' in line:
            test_name = line.split(' ERROR ')[0].strip()
            error_tests.append(test_name)
    
    # Group tests by module
    modules = {}
    all_tests = passed_tests + [t[0] for t in skipped_tests] + failed_tests + error_tests
    
    for test in all_tests:
        if '/' in test:
            module = test.split('/')[1].split('.')[0]
            if module not in modules:
                modules[module] = {
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'error': 0,
                    'total': 0,
                    'skipped_tests': []
                }
            
            if test in passed_tests:
                modules[module]['passed'] += 1
            elif test in failed_tests:
                modules[module]['failed'] += 1
            elif test in [t[0] for t in skipped_tests]:
                modules[module]['skipped'] += 1
                # Find the reason
                for skipped_test, reason in skipped_tests:
                    if skipped_test == test:
                        modules[module]['skipped_tests'].append((test, reason))
                        break
            elif test in error_tests:
                modules[module]['error'] += 1
            
            modules[module]['total'] += 1
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'error': error,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'skipped_tests': skipped_tests,
        'error_tests': error_tests,
        'modules': modules
    }

def generate_markdown_report(results):
    """Generate a markdown report from test results."""
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    skipped = results['skipped']
    error = results['error']
    modules = results['modules']
    
    report = []
    report.append("# Test Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## Summary")
    if total > 0:
        report.append(f"- **Total Tests**: {total}")
        report.append(f"- **Passed**: {passed} ({passed/total*100:.1f}%)")
        report.append(f"- **Failed**: {failed} ({failed/total*100:.1f}%)")
        report.append(f"- **Skipped**: {skipped} ({skipped/total*100:.1f}%)")
        report.append(f"- **Error**: {error} ({error/total*100:.1f}%)")
    else:
        report.append("- **Total Tests**: 0")
        report.append("- **Passed**: 0 (0.0%)")
        report.append("- **Failed**: 0 (0.0%)")
        report.append("- **Skipped**: 0 (0.0%)")
        report.append("- **Error**: 0 (0.0%)")
    
    report.append("")
    
    # Module breakdown
    if modules:
        report.append("## Results by Module")
        report.append("")
        
        for module_name, stats in sorted(modules.items(), key=lambda x: x[1]['failed'], reverse=True):
            module_total = stats['total']
            module_passed = stats['passed']
            module_failed = stats['failed']
            module_skipped = stats['skipped']
            module_error = stats['error']
            
            if module_total > 0:
                pass_rate = module_passed / module_total * 100
            else:
                pass_rate = 0.0
            
            report.append(f"### {module_name}")
            report.append(f"- **Pass Rate**: {pass_rate:.1f}%")
            report.append(f"- **Total Tests**: {module_total}")
            report.append(f"- **Passed**: {module_passed}")
            
            if module_failed > 0:
                report.append(f"- **Failed**: {module_failed}")
            
            if module_skipped > 0:
                report.append(f"- **Skipped**: {module_skipped}")
                
                # List skipped tests with reasons
                report.append("")
                report.append("#### Skipped Tests")
                for test, reason in stats['skipped_tests']:
                    test_name = test.split('::')[-1] if '::' in test else test
                    report.append(f"- **{test_name}** - *Reason: {reason}*")
            
            if module_error > 0:
                report.append(f"- **Error**: {module_error}")
            
            report.append("")
    
    # List failed tests
    if results['failed_tests']:
        report.append("## Failed Tests")
        for test in results['failed_tests']:
            report.append(f"- {test}")
        report.append("")
    
    # List skipped tests with reasons
    if results['skipped_tests']:
        report.append("## Skipped Tests")
        for test, reason in results['skipped_tests']:
            test_name = test.split('::')[-1] if '::' in test else test
            report.append(f"- **{test_name}** - *Reason: {reason}*")
        report.append("")
    
    # List error tests
    if results['error_tests']:
        report.append("## Error Tests")
        for test in results['error_tests']:
            report.append(f"- {test}")
        report.append("")
    
    return '\n'.join(report)

def generate_html_report(results):
    """Generate an HTML report from test results."""
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    skipped = results['skipped']
    error = results['error']
    modules = results['modules']
    
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("    <meta charset='UTF-8'>")
    html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("    <title>Test Report</title>")
    html.append("    <style>")
    html.append("        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }")
    html.append("        h1 { color: #2c3e50; }")
    html.append("        h2 { color: #3498db; margin-top: 30px; }")
    html.append("        h3 { color: #2980b9; }")
    html.append("        .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("        .passed { color: #27ae60; }")
    html.append("        .failed { color: #e74c3c; }")
    html.append("        .skipped { color: #f39c12; }")
    html.append("        .error { color: #c0392b; }")
    html.append("        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }")
    html.append("        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html.append("        th { background-color: #f2f2f2; }")
    html.append("        tr:nth-child(even) { background-color: #f9f9f9; }")
    html.append("        .reason { font-style: italic; color: #7f8c8d; }")
    html.append("        .module-section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }")
    html.append("        .module-header { background-color: #f2f2f2; padding: 10px; margin: -15px -15px 15px -15px; border-radius: 5px 5px 0 0; }")
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    
    html.append("    <h1>Test Report</h1>")
    html.append(f"    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    
    html.append("    <h2>Summary</h2>")
    html.append("    <div class='summary'>")
    if total > 0:
        html.append(f"        <p><strong>Total Tests:</strong> {total}</p>")
        html.append(f"        <p><strong>Passed:</strong> <span class='passed'>{passed}</span> ({passed/total*100:.1f}%)</p>")
        html.append(f"        <p><strong>Failed:</strong> <span class='failed'>{failed}</span> ({failed/total*100:.1f}%)</p>")
        html.append(f"        <p><strong>Skipped:</strong> <span class='skipped'>{skipped}</span> ({skipped/total*100:.1f}%)</p>")
        html.append(f"        <p><strong>Error:</strong> <span class='error'>{error}</span> ({error/total*100:.1f}%)</p>")
    else:
        html.append("        <p><strong>Total Tests:</strong> 0</p>")
        html.append("        <p><strong>Passed:</strong> 0 (0.0%)</p>")
        html.append("        <p><strong>Failed:</strong> 0 (0.0%)</p>")
        html.append("        <p><strong>Skipped:</strong> 0 (0.0%)</p>")
        html.append("        <p><strong>Error:</strong> 0 (0.0%)</p>")
    html.append("    </div>")
    
    # Module breakdown
    if modules:
        html.append("    <h2>Results by Module</h2>")
        html.append("    <table>")
        html.append("        <tr>")
        html.append("            <th>Module</th>")
        html.append("            <th>Pass Rate</th>")
        html.append("            <th>Total</th>")
        html.append("            <th>Passed</th>")
        html.append("            <th>Failed</th>")
        html.append("            <th>Skipped</th>")
        html.append("            <th>Error</th>")
        html.append("        </tr>")
        
        for module_name, stats in sorted(modules.items(), key=lambda x: x[1]['failed'], reverse=True):
            module_total = stats['total']
            module_passed = stats['passed']
            module_failed = stats['failed']
            module_skipped = stats['skipped']
            module_error = stats['error']
            
            if module_total > 0:
                pass_rate = module_passed / module_total * 100
            else:
                pass_rate = 0.0
            
            html.append("        <tr>")
            html.append(f"            <td>{module_name}</td>")
            html.append(f"            <td>{pass_rate:.1f}%</td>")
            html.append(f"            <td>{module_total}</td>")
            html.append(f"            <td class='passed'>{module_passed}</td>")
            html.append(f"            <td class='failed'>{module_failed}</td>")
            html.append(f"            <td class='skipped'>{module_skipped}</td>")
            html.append(f"            <td class='error'>{module_error}</td>")
            html.append("        </tr>")
        
        html.append("    </table>")
        
        # Detailed module sections
        html.append("    <h2>Module Details</h2>")
        
        for module_name, stats in sorted(modules.items(), key=lambda x: x[1]['failed'], reverse=True):
            module_total = stats['total']
            module_passed = stats['passed']
            module_failed = stats['failed']
            module_skipped = stats['skipped']
            module_error = stats['error']
            
            if module_total > 0:
                pass_rate = module_passed / module_total * 100
            else:
                pass_rate = 0.0
            
            html.append("    <div class='module-section'>")
            html.append("        <div class='module-header'>")
            html.append(f"            <h3>{module_name}</h3>")
            html.append(f"            <p>Pass Rate: {pass_rate:.1f}%</p>")
            html.append("        </div>")
            
            # Skipped tests for this module
            if stats['skipped_tests']:
                html.append("        <h4>Skipped Tests</h4>")
                html.append("        <table>")
                html.append("            <tr>")
                html.append("                <th>Test</th>")
                html.append("                <th>Reason</th>")
                html.append("            </tr>")
                
                for test, reason in stats['skipped_tests']:
                    test_name = test.split('::')[-1] if '::' in test else test
                    html.append("            <tr>")
                    html.append(f"                <td class='skipped'>{test_name}</td>")
                    html.append(f"                <td class='reason'>{reason}</td>")
                    html.append("            </tr>")
                
                html.append("        </table>")
            
            html.append("    </div>")
    
    # List failed tests
    if results['failed_tests']:
        html.append("    <h2>Failed Tests</h2>")
        html.append("    <ul>")
        for test in results['failed_tests']:
            html.append(f"        <li class='failed'>{test}</li>")
        html.append("    </ul>")
    
    # List skipped tests with reasons
    if results['skipped_tests']:
        html.append("    <h2>All Skipped Tests</h2>")
        html.append("    <table>")
        html.append("        <tr>")
        html.append("            <th>Test</th>")
        html.append("            <th>Reason</th>")
        html.append("        </tr>")
        for test, reason in results['skipped_tests']:
            test_name = test.split('::')[-1] if '::' in test else test
            html.append("        <tr>")
            html.append(f"            <td class='skipped'>{test_name}</td>")
            html.append(f"            <td class='reason'>{reason}</td>")
            html.append("        </tr>")
        html.append("    </table>")
    
    # List error tests
    if results['error_tests']:
        html.append("    <h2>Error Tests</h2>")
        html.append("    <ul>")
        for test in results['error_tests']:
            html.append(f"        <li class='error'>{test}</li>")
        html.append("    </ul>")
    
    html.append("</body>")
    html.append("</html>")
    
    return '\n'.join(html)

def main():
    output, returncode = run_tests()
    
    print("Parsing results...")
    results = parse_test_results(output)
    
    print("Generating reports...")
    markdown_report = generate_markdown_report(results)
    html_report = generate_html_report(results)
    
    # Save reports
    with open('test_report.md', 'w') as f:
        f.write(markdown_report)
    
    with open('test_report.html', 'w') as f:
        f.write(html_report)
    
    print(f"Reports saved to test_report.md and test_report.html")
    
    # Print summary
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    
    if total > 0:
        print(f"\nSummary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        if failed > 0:
            print(f"Failed: {failed}/{total} tests failed ({failed/total*100:.1f}%)")
    else:
        print("\nSummary: 0/0 tests passed (0.0%)")

if __name__ == "__main__":
    main()
