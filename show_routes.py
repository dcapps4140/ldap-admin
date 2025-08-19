#!/usr/bin/env python3
import sys
import os
from unittest.mock import patch, Mock
import tempfile

# Create temp log file to avoid permission issues
temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
temp_log.close()

try:
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
        
        # Print all registered routes
        print("\nAll Routes in the Application:")
        print("=============================")
        
        routes = []
        for rule in flask_app.url_map.iter_rules():
            routes.append((rule.endpoint, rule.rule, rule.methods))
        
        # Sort by endpoint
        routes.sort(key=lambda x: x[0])
        
        for endpoint, rule, methods in routes:
            print(f"Endpoint: {endpoint:<25} Route: {rule:<30} Methods: {', '.join(sorted(methods - {'HEAD', 'OPTIONS'}))}")
        
        # Group routes by functionality
        print("\nRoutes by Category:")
        print("=================")
        
        categories = {
            "User Management": [r for r in routes if 'user' in r[1].lower()],
            "Group Management": [r for r in routes if 'group' in r[1].lower()],
            "Authentication": [r for r in routes if any(x in r[1].lower() for x in ['login', 'logout', 'auth'])],
            "API": [r for r in routes if '/api/' in r[1].lower()],
            "Static": [r for r in routes if 'static' in r[1].lower()],
            "Other": []
        }
        
        # Add remaining routes to "Other"
        for route in routes:
            if not any(route in category for category in categories.values()):
                categories["Other"].append(route)
        
        for category, category_routes in categories.items():
            if category_routes:
                print(f"\n{category}:")
                for endpoint, rule, methods in category_routes:
                    print(f"  {rule:<30} Methods: {', '.join(sorted(methods - {'HEAD', 'OPTIONS'}))}")
        
except Exception as e:
    print(f"Error discovering routes: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up temp file
    try:
        os.unlink(temp_log.name)
    except:
        pass
