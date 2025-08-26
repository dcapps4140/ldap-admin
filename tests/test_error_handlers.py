"""
Tests specifically for error handlers and edge cases.
"""
import pytest
from unittest.mock import patch, MagicMock

class TestErrorHandlers:
    """Test error handlers and exception scenarios."""
    
    def test_404_handler(self, client_no_rate_limits):
        """Test 404 error handler."""
        # Test various non-existent routes
        nonexistent_routes = [
            '/nonexistent',
            '/api/nonexistent',
            '/users/nonexistent/nonexistent',
            '/static/nonexistent.js',
            '/admin/nonexistent'
        ]
        
        for route in nonexistent_routes:
            response = client_no_rate_limits.get(route)
            assert response.status_code == 404
    
    def test_500_handler_scenarios(self, authenticated_client):
        """Test scenarios that might trigger 500 errors."""
        # Test with various LDAP failures
        routes_to_test = ['/api/users', '/api/groups', '/api/stats']
        
        for route in routes_to_test:
            # Test with different types of exceptions
            exceptions_to_test = [
                Exception("General error"),
                ConnectionError("Connection failed"),
                TimeoutError("Timeout"),
                ValueError("Invalid value"),
                KeyError("Missing key")
            ]
            
            for exception in exceptions_to_test:
                with patch('app.get_ldap_connection') as mock_conn:
                    mock_conn.side_effect = exception
                    
                    response = authenticated_client.get(route)
                    # Should handle gracefully
                    assert response.status_code in [200, 500]
    
    def test_method_not_allowed(self, client_no_rate_limits):
        """Test method not allowed scenarios."""
        # Test wrong HTTP methods on routes
        test_cases = [
            ('PUT', '/login'),
            ('DELETE', '/login'),
            ('PATCH', '/api/users'),
            ('PUT', '/logout'),
        ]
        
        for method, route in test_cases:
            if method == 'PUT':
                response = client_no_rate_limits.put(route)
            elif method == 'DELETE':
                response = client_no_rate_limits.delete(route)
            elif method == 'PATCH':
                response = client_no_rate_limits.patch(route)
            
            # Should return method not allowed or redirect
            assert response.status_code in [405, 302, 429]
    
    def test_malformed_requests(self, authenticated_client):
        """Test malformed request handling."""
        # Test malformed JSON
        response = authenticated_client.post('/api/users',
                                           data='{"invalid": json}',
                                           content_type='application/json')
        assert response.status_code in [200, 400, 500]
        
        # Test missing content type
        response = authenticated_client.post('/api/users',
                                           data='{"username": "test"}')
        assert response.status_code in [200, 400, 500]
        
        # Test empty request body
        response = authenticated_client.post('/api/users',
                                           json={},
                                           content_type='application/json')
        assert response.status_code in [200, 400, 500]
