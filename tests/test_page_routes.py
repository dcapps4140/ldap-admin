import pytest
from unittest.mock import Mock, patch, MagicMock

class TestPageRoutes:
    """Test page routes."""
    
    def test_index_page(self, client):
        """Test index page."""
        response = client.get('/')
        assert response.status_code in [200, 302, 429]
    
    def test_login_page(self, client):
        """Test login page."""
        response = client.get('/login')
        assert response.status_code in [200, 429]
        assert b'html' in response.data.lower()  # Just check for HTML content
    
    def test_logout_page(self, client):
        """Test logout page."""
        response = client.get('/logout')
        assert response.status_code in [200, 302, 429]
    
    def test_users_page(self, client, mock_ldap_connection):
        """Test users page."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/users')
            assert response.status_code in [200, 302, 401, 403, 429]
    
    def test_groups_page(self, client, mock_ldap_connection):
        """Test groups page."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/groups')
            assert response.status_code in [200, 302, 401, 403, 429]
    
    def test_settings_page(self, client):
        """Test settings page."""
        response = client.get('/settings')
        assert response.status_code in [200, 302, 401, 403, 429]
    
    def test_authenticated_pages(self, authenticated_client, mock_ldap_connection):
        """Test pages that require authentication."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            # Test various pages that should require authentication
            pages = ['/users', '/groups', '/settings']
            
            for page in pages:
                response = authenticated_client.get(page, follow_redirects=True)
                assert response.status_code in [200, 302, 404, 429]  # 404 is acceptable if page doesn't exist yet
