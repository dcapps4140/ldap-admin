import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestApiRoutes:
    """Test API routes."""
    
    def test_api_users_get(self, client, mock_ldap_connection):
        """Test GET /api/users endpoint."""
        # Mock user data
        mock_user = Mock()
        mock_user.cn.value = 'testuser'
        mock_user.mail.value = 'test@example.com'
        mock_user.givenName.value = 'Test'
        mock_user.sn.value = 'User'
        mock_ldap_connection.entries = [mock_user]
        
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/users')
            assert response.status_code in [200, 401, 403]
            
            # If successful, check response format
            if response.status_code == 200:
                data = response.get_json()
                assert isinstance(data, list)
    
    def test_api_users_post(self, client, mock_ldap_connection):
        """Test POST /api/users endpoint."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'SecurePass123!'
        }
        
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.post('/api/users', 
                                  data=json.dumps(user_data),
                                  content_type='application/json')
            assert response.status_code in [201, 400, 401, 403, 409]
    
    def test_api_users_delete(self, client, mock_ldap_connection):
        """Test DELETE /api/users/<username> endpoint."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.delete('/api/users/testuser')
            assert response.status_code in [200, 401, 403, 404]
    
    def test_api_groups_get(self, client, mock_ldap_connection):
        """Test GET /api/groups endpoint."""
        # Mock group data
        mock_group = Mock()
        mock_group.cn.value = 'testgroup'
        mock_group.description.value = 'Test Group'
        mock_ldap_connection.entries = [mock_group]
        
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/groups')
            assert response.status_code in [200, 401, 403]
            
            # If successful, check response format
            if response.status_code == 200:
                data = response.get_json()
                assert isinstance(data, list)
    
    def test_api_stats(self, client, mock_ldap_connection):
        """Test GET /api/stats endpoint."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/stats')
            assert response.status_code in [200, 401, 403]
            
            # If successful, check response format
            if response.status_code == 200:
                data = response.get_json()
                assert isinstance(data, dict)
    
    def test_api_test_connection(self, client, mock_ldap_connection):
        """Test GET /api/test_connection endpoint."""
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
            response = client.get('/api/test_connection')
            assert response.status_code in [200, 401, 403]
            
            # If successful, check response format
            if response.status_code == 200:
                data = response.get_json()
                assert isinstance(data, dict)
                assert 'success' in data
