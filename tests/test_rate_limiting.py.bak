import pytest
from unittest.mock import Mock, patch

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_login_rate_limiting(self, client, mock_ldap_connection):
        """Test that login is rate limited."""
        login_data = {
            'username': 'admin',
            'password': 'password'
        }
        
        # Mock successful LDAP bind
        mock_ldap_connection.bind.return_value = True
        
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            # Make multiple requests to trigger rate limiting
            responses = []
            for _ in range(20):  # Try enough times to trigger rate limiting
                resp = client.post('/login', data=login_data)
                responses.append(resp.status_code)
                
                # If we hit a rate limit, we're done
                if resp.status_code == 429:
                    break
            
            # Check if rate limiting was triggered
            assert 429 in responses, "Rate limiting should be triggered after multiple requests"
