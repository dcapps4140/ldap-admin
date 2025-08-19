# Test Summary Report
Generated: 2025-08-19 19:08:01

## Latest Test Run
- **File**: test-output-15.txt
- **Total Tests**: 2
- **Passed**: 0 (0.0%)
- **Failed**: 0 (0.0%)
- **Warnings**: 5
- **Errors**: 2
- **Run Time**: 1.00s

### Error Tests
- [
- [100%]
- at
- at
- tests/test_authentication_rate_limits.py::TestAuthenticationWithRateLimits::test_login_with_rate_limits_disabled
- tests/test_authentication_rate_limits.py::TestAuthenticationWithRateLimits::test_login_with_rate_limits_enabled

## Test Trend
| Run | Total | Passed | Failed | Errors | Pass Rate |
|-----|-------|--------|--------|--------|-----------|
| 1 | 0 | 0 | 0 | 0 | 0.0% |
| 2 | 6 | 0 | 0 | 0 | 0.0% |
| 3 | 7 | 7 | 0 | 0 | 100.0% |
| 4 | 56 | 38 | 18 | 0 | 67.9% |
| 5 | 2 | 0 | 0 | 2 | 0.0% |

## Recommendations

2. **Address warnings**: Review and fix the warnings in the test output.
3. **Fix test errors**: Some tests have setup or execution errors that need to be fixed.
4. **Update tests for missing routes**: Some tests are failing because they're testing routes that don't exist yet.
5. **Handle rate limiting**: Configure tests to handle or disable rate limiting during testing.
6. **Improve test coverage**: Focus on testing the core functionality of your application.