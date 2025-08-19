#!/usr/bin/env python3
"""
Script to generate tests based on discovered routes.
"""
import sys
import os
import re
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from unittest.mock import patch, Mock
    import tempfile
    
    # Create temp log file to avoid permission issues
    temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
    temp_log.close()
    
    with patch('logging.FileHandler') as mock_handler:
        mock_handler.return_value = Mock()
        
        # Import the app
        import app
        
        # Get the Flask app instance
        if hasattr(app, 'app'):
            flask_app = app.app
        else:
            # Look for Flask app instance
            for attr_name in dir(app):
                attr = getattr(app, attr_name)
                if hasattr(attr, 'config') and hasattr(attr, 'test_client'):
                    flask_app = attr
                    break
            else:
                print("Could not find Flask app instance")
                sys.exit(1)
        
        # Group routes by functionality
        user_routes = [rule for rule in flask_app.url_map.iter_rules() if 'user' in rule.rule.lower()]
        group_routes = [rule for rule in flask_app.url_map.iter_rules() if 'group' in rule.rule.lower()]
        auth_routes = [rule for rule in flask_app.url_map.iter_rules() if any(x in rule.rule.lower() for x in ['login', 'logout', 'auth'])]
        other_routes = [rule for rule in flask_app.url_map.iter_rules() 
                        if rule not in user_routes and rule not in group_routes and rule not in auth_routes]
        
        # Generate user management tests
        user_test_file = Path("tests/test_user_management_auto.py")
        with open(user_test_file, 'w') as f:
            f.write("""import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestUserManagement:
    \"\"\"Test user management functionality.\"\"\"
    
""")
            # Generate a test for each user route
            for rule in user_routes:
                route = rule.rule
                methods = list(rule.methods - {'HEAD', 'OPTIONS'})
                
                for method in methods:
                    test_name = f"test_{method.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', route)}"
                    
                    f.write(f"""    def {test_name}(self, client, mock_ldap_connection):
        \"\"\"Test {method} {route}\"\"\"
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
""")
                    
                    if method == 'GET':
                        f.write(f"""            response = client.get('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'POST':
                        # Check if it's likely a form submission
                        if 'add' in route.lower() or 'create' in route.lower():
                            f.write(f"""            # Sample data for {route}
            data = {{
                # Add appropriate form fields here
            }}
            response = client.post('{route}', data=data)
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                        else:
                            f.write(f"""            response = client.post('{route}', data={{}})
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'DELETE':
                        f.write(f"""            response = client.delete('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'PUT':
                        f.write(f"""            response = client.put('{route}', data={{}})
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    
        print(f"Generated user management tests in {user_test_file}")
        
        # Generate group management tests
        group_test_file = Path("tests/test_group_management_auto.py")
        with open(group_test_file, 'w') as f:
            f.write("""import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestGroupManagement:
    \"\"\"Test group management functionality.\"\"\"
    
""")
            # Generate a test for each group route
            for rule in group_routes:
                route = rule.rule
                methods = list(rule.methods - {'HEAD', 'OPTIONS'})
                
                for method in methods:
                    test_name = f"test_{method.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', route)}"
                    
                    f.write(f"""    def {test_name}(self, client, mock_ldap_connection):
        \"\"\"Test {method} {route}\"\"\"
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
""")
                    
                    if method == 'GET':
                        f.write(f"""            response = client.get('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'POST':
                        f.write(f"""            # Sample data for {route}
            data = {{
                # Add appropriate form fields here
            }}
            response = client.post('{route}', data=data)
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'DELETE':
                        f.write(f"""            response = client.delete('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'PUT':
                        f.write(f"""            response = client.put('{route}', data={{}})
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    
        print(f"Generated group management tests in {group_test_file}")
        
        # Generate authentication tests
        auth_test_file = Path("tests/test_authentication_auto.py")
        with open(auth_test_file, 'w') as f:
            f.write("""import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestAuthentication:
    \"\"\"Test authentication functionality.\"\"\"
    
""")
            # Generate a test for each auth route
            for rule in auth_routes:
                route = rule.rule
                methods = list(rule.methods - {'HEAD', 'OPTIONS'})
                
                for method in methods:
                    test_name = f"test_{method.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', route)}"
                    
                    f.write(f"""    def {test_name}(self, client, mock_ldap_connection):
        \"\"\"Test {method} {route}\"\"\"
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
""")
                    
                    if method == 'GET':
                        f.write(f"""            response = client.get('{route}')
            assert response.status_code in [200, 302]  # Success or redirect
            
""")
                    elif method == 'POST':
                        if 'login' in route.lower():
                            f.write(f"""            # Login data
            data = {{
                'username': 'testuser',
                'password': 'password'
            }}
            response = client.post('{route}', data=data)
            assert response.status_code in [200, 302]  # Success or redirect
            
""")
                        else:
                            f.write(f"""            response = client.post('{route}', data={{}})
            assert response.status_code in [200, 302]  # Success or redirect
            
""")
                    
        print(f"Generated authentication tests in {auth_test_file}")
        
        # Generate other tests
        other_test_file = Path("tests/test_other_routes_auto.py")
        with open(other_test_file, 'w') as f:
            f.write("""import pytest
from unittest.mock import Mock, patch, MagicMock
import json

class TestOtherRoutes:
    \"\"\"Test other application routes.\"\"\"
    
""")
            # Generate a test for each other route
            for rule in other_routes:
                route = rule.rule
                methods = list(rule.methods - {'HEAD', 'OPTIONS'})
                
                for method in methods:
                    # Skip static files
                    if 'static' in route.lower():
                        continue
                        
                    test_name = f"test_{method.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', route)}"
                    
                    f.write(f"""    def {test_name}(self, client, mock_ldap_connection):
        \"\"\"Test {method} {route}\"\"\"
        with patch('app.get_ldap_connection', return_value=mock_ldap_connection):
""")
                    
                    if method == 'GET':
                        f.write(f"""            response = client.get('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'POST':
                        f.write(f"""            response = client.post('{route}', data={{}})
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'DELETE':
                        f.write(f"""            response = client.delete('{route}')
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    elif method == 'PUT':
                        f.write(f"""            response = client.put('{route}', data={{}})
            assert response.status_code in [200, 302, 401, 403]  # Success, redirect, or auth required
            
""")
                    
        print(f"Generated other route tests in {other_test_file}")
        
except Exception as e:
    print(f"Error generating tests: {e}")
    import traceback
    traceback.print_exc()
