#!/usr/bin/env python3
import subprocess
import re
import json
from datetime import datetime

def run_tests(test_path):
    """Run tests and capture output."""
    result = subprocess.run(
        ['pytest', test_path, '-v'],
        capture_output=True,
        text=True
    )
    return result.stdout, result.returncode

def parse_test_results(output):
    """Parse test output to extract results."""
    results = []
    
    # Extract test results
    for line in output.split('\n'):
        if '::' in line and any(x in line for x in ['PASSED', 'FAILED', 'SKIPPED', 'ERROR']):
            parts = line.strip().split(' ')
            test_path = parts[0]
            status = next((p for p in parts if p in ['PASSED', 'FAILED', 'SKIPPED', 'ERROR']), 'UNKNOWN')
            
            results.append({
                'test': test_path,
                'status': status
            })
    
    return results

def generate_report(results):
    """Generate a markdown report from test results."""
    report = []
    report.append("# Test Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    skipped = sum(1 for r in results if r['status'] == 'SKIPPED')
    error = sum(1 for r in results if r['status'] == 'ERROR')
    
    report.append("## Summary")
    report.append(f"- **Total Tests**: {total}")
    report.append(f"- **Passed**: {passed} ({passed/total*100:.1f}% if total > 0 else 0.0}%)")
    report.append(f"- **Failed**: {failed} ({failed/total*100:.1f}% if total > 0 else 0.0}%)")
    report.append(f"- **Skipped**: {skipped} ({skipped/total*100:.1f}% if total > 0 else 0.0}%)")
    report.append(f"- **Error**: {error} ({error/total*100:.1f}% if total > 0 else 0.0}%)")
    report.append("")
    
    # Results by category
    categories = {}
    for result in results:
        test_path = result['test']
        category = test_path.split('::')[0].replace('tests/test_', '').replace('.py', '')
        
        if category not in categories:
            categories[category] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'error': 0,
                'tests': []
            }
        
        categories[category]['total'] += 1
        categories[category][result['status'].lower()] += 1
        categories[category]['tests'].append(result)
    
    report.append("## Results by Category")
    report.append("")
    
    for category, data in sorted(categories.items(), key=lambda x: x[1]['failed'], reverse=True):
        pass_rate = data['passed'] / data['total'] * 100 if data['total'] > 0 else 0.0
        report.append(f"### {category}")
        report.append(f"- **Pass Rate**: {pass_rate:.1f}%")
        report.append(f"- **Tests**: {data['total']}")
        report.append(f"- **Passed**: {data['passed']}")
        report.append(f"- **Failed**: {data['failed']}")
        if data['skipped'] > 0:
            report.append(f"- **Skipped**: {data['skipped']}")
        if data['error'] > 0:
            report.append(f"- **Error**: {data['error']}")
        
        if data['failed'] > 0 or data['error'] > 0:
            report.append("")
            report.append("#### Failed Tests")
            for test in data['tests']:
                if test['status'] in ['FAILED', 'ERROR']:
                    test_name = test['test'].split('::')[-1]
                    report.append(f"- {test_name}")
        
        report.append("")
    
    return '\n'.join(report)

def main():
    print("Running tests...")
    output, returncode = run_tests('tests/')
    
    print("Parsing results...")
    results = parse_test_results(output)
    
    print("Generating report...")
    report = generate_report(results)
    
    # Save report
    with open('test_report.md', 'w') as f:
        f.write(report)
    
    print(f"Report saved to test_report.md")
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    
    print(f"\nSummary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    if failed > 0:
        print(f"Failed: {failed}/{total} tests failed ({failed/total*100:.1f}% if total > 0 else 0.0}%)")

if __name__ == "__main__":
    main()
