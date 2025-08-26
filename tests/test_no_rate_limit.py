"""
Test without rate limiting issues.
"""
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def disable_limiter():
    """Disable rate limiter for all tests."""
    with patch('flask_limiter.Limiter.limit') as mock_limit:
        # Make the decorator a no-op
        mock_limit.return_value = lambda f: f
        yield

class TestNoRateLimit:
    """Tests without rate limiting."""
    
    def test_basic_coverage(self, app):
        """Basic coverage test."""
        with app.test_client() as client:
            # Test login page
            response = client.get('/login')
            assert response.status_code == 200
            
            # Test successful login
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            assert response.status_code in [200, 302]
    
    def test_can_manage_groups(self, app):
        """Test can_manage_groups method."""
        with app.app_context():
            from app import User
            
            user = User('test', 'super_admin', 'Test')
            assert user.can_manage_groups() == True
            
            user2 = User('test', 'admin', 'Test')  
            assert user2.can_manage_groups() == False
    
    def test_ldap_connection(self, app):
        """Test LDAP connection."""
        with app.app_context():
            from app import get_ldap_connection
            
            with patch('app.Server'), patch('app.Connection') as mock_conn:
                mock_connection = MagicMock()
                mock_conn.return_value = mock_connection
                
                result = get_ldap_connection()
                assert result == mock_connection
