# Test Report
Generated: 2025-08-19 21:22:43

## Summary
- **Total Tests**: 71
- **Passed**: 55 (77.5%)
- **Failed**: 0 (0.0%)
- **Skipped**: 16 (22.5%)
- **Error**: 0 (0.0%)

## Results by Module

### tests/test_api_routes.py
- **Pass Rate**: 83.3%
- **Total Tests**: 6
- **Passed**: 5
- **Skipped**: 1

### tests/test_api_routes_with_auth.py
- **Pass Rate**: 100.0%
- **Total Tests**: 3
- **Passed**: 3

### tests/test_authentication.py
- **Pass Rate**: 87.5%
- **Total Tests**: 8
- **Passed**: 7
- **Skipped**: 1

### tests/test_authentication_auto.py
- **Pass Rate**: 100.0%
- **Total Tests**: 3
- **Passed**: 3

### tests/test_authentication_updated.py
- **Pass Rate**: 66.7%
- **Total Tests**: 9
- **Passed**: 6
- **Skipped**: 3

### tests/test_basic.py
- **Pass Rate**: 100.0%
- **Total Tests**: 6
- **Passed**: 6

### tests/test_debug.py
- **Pass Rate**: 100.0%
- **Total Tests**: 1
- **Passed**: 1

### tests/test_group_management.py
- **Pass Rate**: 42.9%
- **Total Tests**: 7
- **Passed**: 3
- **Skipped**: 4

### tests/test_group_management_auto.py
- **Pass Rate**: 100.0%
- **Total Tests**: 2
- **Passed**: 2

### tests/test_other_routes_auto.py
- **Pass Rate**: 100.0%
- **Total Tests**: 4
- **Passed**: 4

### tests/test_page_routes.py
- **Pass Rate**: 100.0%
- **Total Tests**: 7
- **Passed**: 7

### tests/test_rate_limiting.py
- **Pass Rate**: 100.0%
- **Total Tests**: 1
- **Passed**: 1

### tests/test_user_management.py
- **Pass Rate**: 50.0%
- **Total Tests**: 6
- **Passed**: 3
- **Skipped**: 3

### tests/test_user_management_auto.py
- **Pass Rate**: 100.0%
- **Total Tests**: 4
- **Passed**: 4

### tests/test_authentication_no_rate_limits.py
- **Pass Rate**: 0.0%
- **Total Tests**: 2
- **Passed**: 0
- **Skipped**: 2

### tests/test_authentication_rate_limits.py
- **Pass Rate**: 0.0%
- **Total Tests**: 2
- **Passed**: 0
- **Skipped**: 2

## Skipped Tests
- tests/test_api_routes.py::TestApiRoutes::test_api_test_connection
- tests/test_authentication.py::TestAuthentication::test_admin_required_routes
- tests/test_authentication_no_rate_limits.py::TestAuthenticationNoRateLimits::test_login_page_loads
- tests/test_authentication_no_rate_limits.py::TestAuthenticationNoRateLimits::test_valid_login
- tests/test_authentication_rate_limits.py::TestAuthenticationWithRateLimits::test_login_with_rate_limits_disabled
- tests/test_authentication_rate_limits.py::TestAuthenticationWithRateLimits::test_login_with_rate_limits_enabled
- tests/test_authentication_updated.py::TestAuthenticationUpdated::test_protected_route_with_auth
- tests/test_authentication_updated.py::TestAuthenticationUpdated::test_admin_required_routes
- tests/test_authentication_updated.py::TestAuthenticationUpdated::test_password_reset_request
- tests/test_group_management.py::TestGroupManagement::test_add_group_form
- tests/test_group_management.py::TestGroupManagement::test_group_membership
- tests/test_group_management.py::TestGroupManagement::test_group_edit
- tests/test_group_management.py::TestGroupManagement::test_group_delete
- tests/test_user_management.py::TestUserManagement::test_add_user_form
- tests/test_user_management.py::TestUserManagement::test_user_edit
- tests/test_user_management.py::TestUserManagement::test_user_delete
