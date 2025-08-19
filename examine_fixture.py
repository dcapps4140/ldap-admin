#!/usr/bin/env python3
import os
import re

def examine_fixture():
    """Examine the authenticated_client fixture in conftest.py."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    # Find the authenticated_client fixture
    fixture_match = re.search(r'@pytest\.fixture\s+def\s+authenticated_client.*?yield.*?(?=@|\Z)', content, re.DOTALL)
    
    if fixture_match:
        fixture_code = fixture_match.group(0)
        print("Found authenticated_client fixture:")
        print("=" * 40)
        print(fixture_code)
        print("=" * 40)
        
        # Check if it's setting authentication properly
        if 'authenticated' in fixture_code and 'sess' in fixture_code:
            print("\nThe fixture appears to set session authentication.")
            
            # Check what authentication values are set
            auth_values = {}
            for line in fixture_code.split('\n'):
                if 'sess[' in line:
                    match = re.search(r"sess\['([^']+)'\]\s*=\s*(.+)", line)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        auth_values[key] = value
            
            if auth_values:
                print("\nAuthentication values set in session:")
                for key, value in auth_values.items():
                    print(f"  {key} = {value}")
            else:
                print("\nWarning: No session values found in the fixture.")
        else:
            print("\nWarning: The fixture might not be setting authentication properly.")
    else:
        print("No authenticated_client fixture found in conftest.py")
        
        # Check if there's any other authentication-related code
        auth_matches = re.findall(r'def\s+([^\(]+auth[^\(]*)\(', content, re.IGNORECASE)
        if auth_matches:
            print("\nFound other authentication-related functions:")
            for match in auth_matches:
                print(f"- {match}")

if __name__ == "__main__":
    examine_fixture()
