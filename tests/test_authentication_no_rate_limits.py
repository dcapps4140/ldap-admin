import pytest
from unittest.mock import Mock, patch

@pytest.mark.usefixtures("disable_rate_limits")
class TestAuthenticationNoRateLimits:
    """Test authentication with rate limiting disabled."""
    
    def test_login_page_loads(self, client):
        """Test login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'username' in response.data.lower()
    
    def test_valid_login(self, client, mock_ldap_connection):
        """Test successful login."""
        login_data = {
            'username': 'admin',
            'password': 'correct_password'
        }
        
        # Mock successful LDAP bind
        mock_ldap_connection.bind.return_value = True
        
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.post('/login', data=login_data, follow_redirects=True)
            assert response.status_code == 200
