import pytest
from unittest.mock import Mock, patch

def test_basic_functionality():
    """Basic test to verify testing framework is working."""
    assert True

def test_app_creation(app):
    """Test that the Flask app can be created."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_client_creation(client):
    """Test that test client can be created."""
    assert client is not None

def test_sample_data(sample_user_data, sample_group_data):
    """Test that sample data fixtures work."""
    assert sample_user_data['username'] == 'sampleuser'
    assert sample_group_data['name'] == 'samplegroup'

def test_mock_ldap(mock_ldap_connection):
    """Test that LDAP mocking works."""
    assert mock_ldap_connection is not None
    assert mock_ldap_connection.bind.return_value is True

def test_app_routes(app):
    """Test that the app has routes defined."""
    rules = list(app.url_map.iter_rules())
    assert len(rules) > 0
    print(f"Found {len(rules)} routes in the application")
    
    # Print the first 5 routes for debugging
    for i, rule in enumerate(rules[:5]):
        print(f"Route {i+1}: {rule.rule} - Methods: {', '.join(rule.methods)}")
    
    # Check for common routes
    route_paths = [rule.rule for rule in rules]
    print(f"Available routes: {route_paths}")
    
    # Check for login route (common in most apps)
    login_routes = [r for r in route_paths if 'login' in r.lower()]
    if login_routes:
        print(f"Found login routes: {login_routes}")
    
    # At least one route should exist
    assert len(rules) >= 1
