import pytest

class TestAuthenticationNoRateLimits:
    """Test authentication functionality without rate limiting."""
    
    def test_login_page_loads(self, client_no_rate_limits):
        """Test that login page loads without rate limiting."""
        response = client_no_rate_limits.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'Login' in response.data
    
    def test_valid_login(self, client_no_rate_limits, valid_login_data, mock_ldap_full):
        """Test valid login without rate limiting."""
        # Mock successful LDAP authentication
        mock_ldap_full['connection'].bind.return_value = True
        mock_ldap_full['connection'].search.return_value = True
        
        # Create a mock user entry
        from unittest.mock import MagicMock
        mock_user = MagicMock()
        mock_user.cn.value = 'Test User'
        mock_user.uid.value = 'testuser'
        mock_user.mail.value = 'testuser@example.com'
        mock_user.entry_dn = 'uid=testuser,ou=users,dc=test,dc=com'
        mock_ldap_full['connection'].entries = [mock_user]
        
        response = client_no_rate_limits.post('/login', data=valid_login_data, follow_redirects=False)
        # Should either succeed (200) or redirect (302) - not be rate limited (429)
        assert response.status_code in [200, 302]
        assert response.status_code != 429
    
    def test_multiple_login_attempts_no_rate_limit(self, client_no_rate_limits, valid_login_data, mock_ldap_full):
        """Test multiple login attempts are not rate limited when rate limiting is disabled."""
        # Mock LDAP authentication
        mock_ldap_full['connection'].bind.return_value = True
        mock_ldap_full['connection'].search.return_value = True
        
        # Create a mock user entry
        from unittest.mock import MagicMock
        mock_user = MagicMock()
        mock_user.cn.value = 'Test User'
        mock_user.uid.value = 'testuser'
        mock_user.mail.value = 'testuser@example.com'
        mock_user.entry_dn = 'uid=testuser,ou=users,dc=test,dc=com'
        mock_ldap_full['connection'].entries = [mock_user]
        
        # Make multiple requests - none should be rate limited
        for i in range(15):
            response = client_no_rate_limits.post('/login', data=valid_login_data)
            # Should not get 429 (Too Many Requests)
            assert response.status_code != 429, f"Request {i+1} was rate limited when it shouldn't be"
    
    def test_invalid_login_no_rate_limit(self, client_no_rate_limits, invalid_login_data, mock_ldap_full):
        """Test invalid login attempts are not rate limited when rate limiting is disabled."""
        # Mock failed LDAP authentication
        mock_ldap_full['connection'].bind.return_value = False
        mock_ldap_full['connection'].search.return_value = False
        mock_ldap_full['connection'].entries = []
        
        # Make multiple invalid login attempts
        for i in range(10):
            response = client_no_rate_limits.post('/login', data=invalid_login_data)
            # Should not get 429 (Too Many Requests), even for invalid attempts
            assert response.status_code != 429, f"Invalid login attempt {i+1} was rate limited when it shouldn't be"
    
    def test_login_form_present(self, client_no_rate_limits):
        """Test that login form is present on the login page."""
        response = client_no_rate_limits.get('/login')
        assert response.status_code == 200
        
        # Check for form elements
        response_text = response.data.decode('utf-8').lower()
        assert 'username' in response_text or 'user' in response_text
        assert 'password' in response_text
        assert 'form' in response_text or 'input' in response_text
