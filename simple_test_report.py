#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime

def run_tests():
    """Run tests and capture output."""
    print("Running tests...")
    result = subprocess.run(['pytest', '-v'], capture_output=True, text=True)
    return result.stdout

def parse_test_results(output):
    """Parse test output to extract results."""
    # Count test results
    passed = output.count(' PASSED ')
    failed = output.count(' FAILED ')
    skipped = output.count(' SKIPPED ')
    error = output.count(' ERROR ')
    
    total = passed + failed + skipped + error
    
    # Extract test names
    failed_tests = []
    for line in output.split('\n'):
        if ' FAILED ' in line:
            test_name = line.split(' FAILED ')[0].strip()
            failed_tests.append(test_name)
    
    skipped_tests = []
    for line in output.split('\n'):
        if ' SKIPPED ' in line:
            test_name = line.split(' SKIPPED ')[0].strip()
            skipped_tests.append(test_name)
    
    error_tests = []
    for line in output.split('\n'):
        if ' ERROR ' in line:
            test_name = line.split(' ERROR ')[0].strip()
            error_tests.append(test_name)
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'error': error,
        'failed_tests': failed_tests,
        'skipped_tests': skipped_tests,
        'error_tests': error_tests
    }

def generate_report(results):
    """Generate a markdown report from test results."""
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    skipped = results['skipped']
    error = results['error']
    
    report = []
    report.append("# Test Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## Summary")
    report.append(f"- **Total Tests**: {total}")
    
    if total > 0:
        pass_pct = passed / total * 100
        fail_pct = failed / total * 100
        skip_pct = skipped / total * 100
        error_pct = error / total * 100
        
        report.append(f"- **Passed**: {passed} ({pass_pct:.1f}%)")
        report.append(f"- **Failed**: {failed} ({fail_pct:.1f}%)")
        report.append(f"- **Skipped**: {skipped} ({skip_pct:.1f}%)")
        report.append(f"- **Error**: {error} ({error_pct:.1f}%)")
    else:
        report.append(f"- **Passed**: {passed} (0.0%)")
        report.append(f"- **Failed**: {failed} (0.0%)")
        report.append(f"- **Skipped**: {skipped} (0.0%)")
        report.append(f"- **Error**: {error} (0.0%)")
    
    report.append("")
    
    if failed > 0:
        report.append("## Failed Tests")
        for test in results['failed_tests']:
            report.append(f"- {test}")
        report.append("")
    
    if skipped > 0:
        report.append("## Skipped Tests")
        for test in results['skipped_tests']:
            report.append(f"- {test}")
        report.append("")
    
    if error > 0:
        report.append("## Error Tests")
        for test in results['error_tests']:
            report.append(f"- {test}")
        report.append("")
    
    return '\n'.join(report)

def main():
    output = run_tests()
    
    print("Parsing results...")
    results = parse_test_results(output)
    
    print("Generating report...")
    report = generate_report(results)
    
    # Save report
    with open('test_report.md', 'w') as f:
        f.write(report)
    
    print(f"Report saved to test_report.md")
    
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
