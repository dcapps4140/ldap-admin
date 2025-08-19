import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestOtherRoutes:
    """Test other application routes."""
    
    def test_get__(self, client, mock_ldap_connection):
        """Test GET /"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
    def test_get__settings(self, client, mock_ldap_connection):
        """Test GET /settings"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/settings')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
    def test_get__api_test_connection(self, client, mock_ldap_connection):
        """Test GET /api/test-connection"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/test-connection')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
    def test_get__api_stats(self, client, mock_ldap_connection):
        """Test GET /api/stats"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/stats')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
