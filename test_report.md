# Test Report
Generated: 2025-08-19 21:49:20

## Summary
- **Total Tests**: 71
- **Passed**: 55 (77.5%)
- **Failed**: 0 (0.0%)
- **Skipped**: 16 (22.5%)
- **Error**: 0 (0.0%)

## Results by Module

### test_api_routes
- **Pass Rate**: 83.3%
- **Total Tests**: 6
- **Passed**: 5
- **Skipped**: 1

#### Skipped Tests
- **test_api_test_connection** - *Reason: Route returns 404*

### test_api_routes_with_auth
- **Pass Rate**: 100.0%
- **Total Tests**: 3
- **Passed**: 3

### test_authentication
- **Pass Rate**: 87.5%
- **Total Tests**: 8
- **Passed**: 7
- **Skipped**: 1

#### Skipped Tests
- **test_admin_required_routes** - *Reason: Route returns 404*

### test_authentication_auto
- **Pass Rate**: 100.0%
- **Total Tests**: 3
- **Passed**: 3

### test_authentication_updated
- **Pass Rate**: 66.7%
- **Total Tests**: 9
- **Passed**: 6
- **Skipped**: 3

#### Skipped Tests
- **test_protected_route_with_auth** - *Reason: Dashboard route doesn*
- **test_admin_required_routes** - *Reason: Admin route doesn*
- **test_password_reset_request** - *Reason: Password reset route doesn*

### test_basic
- **Pass Rate**: 100.0%
- **Total Tests**: 6
- **Passed**: 6

### test_debug
- **Pass Rate**: 100.0%
- **Total Tests**: 1
- **Passed**: 1

### test_group_management
- **Pass Rate**: 42.9%
- **Total Tests**: 7
- **Passed**: 3
- **Skipped**: 4

#### Skipped Tests
- **test_add_group_form** - *Reason: Route not implemented yet or missing fixture*
- **test_group_membership** - *Reason: Route returns 404*
- **test_group_edit** - *Reason: Route returns 404*
- **test_group_delete** - *Reason: Route returns 404*

### test_group_management_auto
- **Pass Rate**: 100.0%
- **Total Tests**: 2
- **Passed**: 2

### test_other_routes_auto
- **Pass Rate**: 100.0%
- **Total Tests**: 4
- **Passed**: 4

### test_page_routes
- **Pass Rate**: 100.0%
- **Total Tests**: 7
- **Passed**: 7

### test_rate_limiting
- **Pass Rate**: 100.0%
- **Total Tests**: 1
- **Passed**: 1

### test_user_management
- **Pass Rate**: 50.0%
- **Total Tests**: 6
- **Passed**: 3
- **Skipped**: 3

#### Skipped Tests
- **test_add_user_form** - *Reason: Route not implemented yet or missing fixture*
- **test_user_edit** - *Reason: Route returns 404*
- **test_user_delete** - *Reason: Route returns 404*

### test_user_management_auto
- **Pass Rate**: 100.0%
- **Total Tests**: 4
- **Passed**: 4

### test_authentication_no_rate_limits
- **Pass Rate**: 0.0%
- **Total Tests**: 2
- **Passed**: 0
- **Skipped**: 2

#### Skipped Tests
- **test_login_page_loads** - *Reason: Missing fixture*
- **test_valid_login** - *Reason: Missing fixture*

### test_authentication_rate_limits
- **Pass Rate**: 0.0%
- **Total Tests**: 2
- **Passed**: 0
- **Skipped**: 2

#### Skipped Tests
- **test_login_with_rate_limits_disabled** - *Reason: Missing fixture*
- **test_login_with_rate_limits_enabled** - *Reason: Missing fixture*

## Skipped Tests
- **test_api_test_connection** - *Reason: Route returns 404*
- **test_admin_required_routes** - *Reason: Route returns 404*
- **test_login_page_loads** - *Reason: Missing fixture*
- **test_valid_login** - *Reason: Missing fixture*
- **test_login_with_rate_limits_disabled** - *Reason: Missing fixture*
- **test_login_with_rate_limits_enabled** - *Reason: Missing fixture*
- **test_protected_route_with_auth** - *Reason: Dashboard route doesn*
- **test_admin_required_routes** - *Reason: Admin route doesn*
- **test_password_reset_request** - *Reason: Password reset route doesn*
- **test_add_group_form** - *Reason: Route not implemented yet or missing fixture*
- **test_group_membership** - *Reason: Route returns 404*
- **test_group_edit** - *Reason: Route returns 404*
- **test_group_delete** - *Reason: Route returns 404*
- **test_add_user_form** - *Reason: Route not implemented yet or missing fixture*
- **test_user_edit** - *Reason: Route returns 404*
- **test_user_delete** - *Reason: Route returns 404*
