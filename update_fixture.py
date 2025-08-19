#!/usr/bin/env python3
import os
import re
import shutil

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def update_fixture():
    """Update the authenticated_client fixture in conftest.py."""
    conftest_path = 'tests/conftest.py'
    
    if not os.path.exists(conftest_path):
        print(f"Error: {conftest_path} not found")
        return False
    
    # Backup the file
    backup_file(conftest_path)
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    # Find the authenticated_client fixture
    fixture_match = re.search(r'@pytest\.fixture\s+def\s+authenticated_client.*?return client', content, re.DOTALL)
    
    if fixture_match:
        fixture_code = fixture_match.group(0)
        print("Found existing authenticated_client fixture:")
        print("=" * 40)
        print(fixture_code)
        print("=" * 40)
        
        # Update the fixture to use yield instead of return
        updated_fixture = fixture_code.replace('return client', 'yield client')
        
        # Update the content
        new_content = content.replace(fixture_code, updated_fixture)
        
        # Create a new combined fixture
        combined_fixture = '''
@pytest.fixture
def authenticated_client_no_rate_limits(authenticated_client, disable_rate_limits):
    """Create an authenticated client with rate limits disabled."""
    yield authenticated_client
'''
        
        # Add the combined fixture to the end of the file
        new_content += combined_fixture
        
        with open(conftest_path, 'w') as f:
            f.write(new_content)
        
        print("\nFixture updated successfully!")
        print("Added new combined fixture: authenticated_client_no_rate_limits")
        return True
    else:
        print("Could not find the authenticated_client fixture with 'return client'. Manual update required.")
        return False

if __name__ == "__main__":
    update_fixture()
