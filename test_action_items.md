# Test Action Items
Generated: 2025-08-19 22:04:00
Based on: test-output-20.txt

**Test Summary**: 45 passed, 25 failed, 0 errors, 3 warnings

## High Priority Items
### 3. Fix Status Code Issues
#### Status Code 302 Issues
These tests are getting redirected (302). You need to:
- Use authenticated client for API tests
- Update assertions to accept 302 as valid response
- Use `follow_redirects=True` in client requests

Affected tests:
- TestApiRoutes.test_api_users_get
- TestApiRoutes.test_api_users_post
- TestApiRoutes.test_api_users_delete
- TestApiRoutes.test_api_groups_get
- TestApiRoutes.test_api_stats

#### Status Code 429 Issues
These tests are hitting rate limits (429). You need to:
- Use the `disable_rate_limits` fixture

Affected tests:
- TestAuthentication.test_post__login
- TestAuthenticationNoRateLimits.test_login_page_loads
- TestAuthenticationNoRateLimits.test_valid_login
- TestAuthenticationUpdated.test_login_page_loads
- TestAuthenticationUpdated.test_valid_login
- TestAuthenticationUpdated.test_invalid_login
- TestAuthenticationUpdated.test_logout
- TestPageRoutes.test_login_page

## Medium Priority Items
## Low Priority Items
### 1. Address Warnings
#### Other Warnings
- warnings.warn(f"{attr} is deprecated. Please use {newAttr} instead.", DeprecationWarning)
- warnings.warn(
- tests/test_api_routes.py::TestApiRoutes::test_api_users_get

#### DeprecationWarning Warnings
- /home/dcapps/projects/ldap-admin/venv/lib/python3.10/site-packages/pyasn1/codec/ber/encoder.py:952: DeprecationWarning: typeMap is deprecated. Please use TYPE_MAP instead.
- /home/dcapps/projects/ldap-admin/venv/lib/python3.10/site-packages/pyasn1/codec/ber/encoder.py:952: DeprecationWarning: tagMap is deprecated. Please use TAG_MAP instead.

#### UserWarning Warnings
Configure a proper storage backend for Flask-Limiter:
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis\://127.0.0.1:6379",
)
```

## Implementation Plan
1. **Fix authentication in tests** - Use authenticated client for protected routes
2. **Address warnings** - Fix or suppress warnings