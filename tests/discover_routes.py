#!/usr/bin/env python3
"""
Script to discover available routes in the Flask application.
"""
import sys
import os

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
        
        # Print all registered routes
        print("Available routes in the application:")
        print("===================================")
        
        for rule in flask_app.url_map.iter_rules():
            print(f"Route: {rule.rule} - Methods: {', '.join(rule.methods)}")
        
        print("\nSuggested test endpoints:")
        print("=======================")
        
        # Group routes by functionality
        user_routes = [rule for rule in flask_app.url_map.iter_rules() if 'user' in rule.rule.lower()]
        group_routes = [rule for rule in flask_app.url_map.iter_rules() if 'group' in rule.rule.lower()]
        auth_routes = [rule for rule in flask_app.url_map.iter_rules() if any(x in rule.rule.lower() for x in ['login', 'logout', 'auth'])]
        
        print("\nUser Management Routes:")
        for rule in user_routes:
            print(f"  {rule.rule} - {', '.join(rule.methods)}")
            
        print("\nGroup Management Routes:")
        for rule in group_routes:
            print(f"  {rule.rule} - {', '.join(rule.methods)}")
            
        print("\nAuthentication Routes:")
        for rule in auth_routes:
            print(f"  {rule.rule} - {', '.join(rule.methods)}")
            
        print("\nOther Routes:")
        other_routes = [rule for rule in flask_app.url_map.iter_rules() 
                        if rule not in user_routes and rule not in group_routes and rule not in auth_routes]
        for rule in other_routes:
            print(f"  {rule.rule} - {', '.join(rule.methods)}")
            
except Exception as e:
    print(f"Error discovering routes: {e}")
    import traceback
    traceback.print_exc()
