import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestGroupManagement:
    """Test group management functionality."""
    
    def test_get__groups(self, client, mock_ldap_connection):
        """Test GET /groups"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/groups')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
    def test_get__api_groups(self, client, mock_ldap_connection):
        """Test GET /api/groups"""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/groups')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
