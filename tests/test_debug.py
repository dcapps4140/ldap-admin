import pytest
from unittest.mock import Mock, patch
import json

def test_debug_api_response(authenticated_client_no_rate_limits):
    """Debug test to print API response details."""
    response = authenticated_client_no_rate_limits.get('/api/users', follow_redirects=True)
    
    print("\n=== DEBUG API RESPONSE ===")
    print(f"Status code: {response.status_code}")
    print(f"Content type: {response.content_type}")
    print(f"Headers: {dict(response.headers)}")
    
    # Try to get JSON data
    json_data = response.get_json(silent=True)
    if json_data is not None:
        print(f"JSON data: {json.dumps(json_data, indent=2)}")
    else:
        # Print the first 500 characters of the response data
        print(f"Response data (first 500 chars): {response.data[:500]}")
    
    # Check if it looks like HTML
    if b'<html' in response.data or b'<!DOCTYPE html' in response.data:
        print("Response appears to be HTML")
        
        # Check if it's a login page
        if b'login' in response.data.lower():
            print("Response appears to be a login page")
    
    # Always pass the test
    assert True
