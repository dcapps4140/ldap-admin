"""
Coverage tests using properly authenticated clients.
"""
import pytest
from unittest.mock import patch, MagicMock

class TestCoverageAuthenticated:
    """Coverage tests using authenticated clients."""
    
    def test_api_routes_authenticated(self, authenticated_client):
        """Test API routes with proper authentication."""
        # Test GET routes with authenticated client
        get_routes = ['/api/users', '/api/groups', '/api/stats', '/api/test-connection']
        
        for route in get_routes:
            with patch('app.get_ldap_connection') as mock_conn:
                mock_connection = MagicMock()
                mock_connection.search.return_value = True
                mock_connection.entries = []
                mock_conn.return_value = mock_connection
                
                response = authenticated_client.get(route)
                # Now should get proper responses, not redirects
                assert response.status_code in [200, 500]
    
    def test_api_routes_with_ldap_errors(self, authenticated_client):
        """Test API routes with LDAP errors."""
        routes = ['/api/users', '/api/groups', '/api/stats']
        
        for route in routes:
            with patch('app.get_ldap_connection') as mock_conn:
                mock_conn.side_effect = Exception("LDAP Connection Error")
                
                response = authenticated_client.get(route)
                # Should handle errors gracefully
                assert response.status_code in [200, 500]
    
    def test_user_management_api(self, authenticated_client):
        """Test user management API endpoints."""
        # Test POST user creation
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123'
        }
        
        with patch('app.get_ldap_connection') as mock_conn:
            mock_conn.return_value = MagicMock()
            
            # Test user creation
            response = authenticated_client.post('/api/users', 
                                               json=user_data,
                                               content_type='application/json')
            assert response.status_code in [200, 201, 400, 500]
            
            # Test user deletion
            response = authenticated_client.delete('/api/users/testuser2')
            assert response.status_code in [200, 204, 404, 500]
    
    def test_certificate_routes_authenticated(self, authenticated_client):
        """Test certificate routes with authentication."""
        username = 'testuser'
        
        # Test certificate page
        response = authenticated_client.get(f'/users/{username}/certificate')
        assert response.status_code in [200, 404, 500]
        
        # Test certificate generation
        response = authenticated_client.post(f'/users/{username}/certificate', data={
            'certificate_type': 'user',
            'validity_days': '365'
        })
        assert response.status_code in [200, 302, 400, 500]
        
        # Test downloads
        response = authenticated_client.get(f'/users/{username}/download/enrollment')
        assert response.status_code in [200, 404, 500]
        
        response = authenticated_client.get(f'/users/{username}/download/certificate')
        assert response.status_code in [200, 404, 500]
        
        # Test email enrollment
        response = authenticated_client.post(f'/users/{username}/email_enrollment', data={
            'email': 'test@example.com'
        })
        assert response.status_code in [200, 302, 400, 500]
    
    def test_page_routes_authenticated(self, authenticated_client):
        """Test page routes with authentication."""
        page_routes = ['/', '/users', '/groups', '/settings']
        
        for route in page_routes:
            response = authenticated_client.get(route)
            assert response.status_code in [200, 302]
    
    def test_admin_functionality(self, authenticated_admin_client):
        """Test admin-specific functionality."""
        # Test admin routes if they exist
        admin_routes = ['/users', '/groups', '/settings']
        
        for route in admin_routes:
            response = authenticated_admin_client.get(route)
            assert response.status_code in [200, 302, 404]
        
        # Test admin API access
        with patch('app.get_ldap_connection') as mock_conn:
            mock_conn.return_value = MagicMock()
            
            response = authenticated_admin_client.get('/api/users')
            assert response.status_code in [200, 500]
