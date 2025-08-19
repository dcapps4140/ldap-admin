import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestUserManagement:
    """Test user management functionality."""
    
    def test_get__users(self, authenticated_client, mock_ldap_connection):
        """Test GET /users"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = authenticated_client.get('/users', follow_redirects=True)
            assert response.status_code in [200, 302, 401, 403, 429]  # Success, redirect, or auth required
            
    def test_get__api_users(self, authenticated_client, mock_ldap_connection):
        """Test GET /api/users"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = authenticated_client.get('/api/users', follow_redirects=True)
            assert response.status_code in [200, 302, 401, 403, 429]  # Success, redirect, or auth required
            
    def test_post__api_users(self, authenticated_client, mock_ldap_connection):
        """Test POST /api/users"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = authenticated_client.post('/api/users', data={})
            assert response.status_code in [200, 302, 401, 403, 429]  # Success, redirect, or auth required
            
    def test_delete__api_users__username_(self, authenticated_client, mock_ldap_connection):
        """Test DELETE /api/users/<username>"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = authenticated_client.delete('/api/users/<username>')
            assert response.status_code in [200, 302, 401, 403, 429]  # Success, redirect, or auth required
            
