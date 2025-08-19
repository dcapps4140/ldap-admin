#!/usr/bin/env python3
# File: update_api_tests.py

import os
import re
import sys
import shutil
import argparse
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def update_api_test_file(file_path, dry_run=False):
    """Update API test files to use authenticated_client."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Keep track of changes
    changes = []
    
    # Pattern to match test function definitions with 'client' parameter
    # This pattern ensures we replace the whole 'client' word, not just part of it
    pattern = r'(def\s+test_\w+\s*\(\s*self\s*,\s*)client(\s*,.*?\))'
    
    # Function to replace matches
    def replace_func(match):
        func_def = match.group(1)
        params = match.group(2)
        
        # Replace client with authenticated_client in function definition
        new_func_def = func_def + 'authenticated_client' + params
        
        # Record the change
        changes.append({
            'original': match.group(0),
            'replacement': new_func_def
        })
        
        return new_func_def
    
    # Apply replacements
    new_content = re.sub(pattern, replace_func, content)
    
    # Look for client.get/post/etc patterns and replace them
    client_call_pattern = r'(client\.(get|post|put|delete)\s*\(\s*[\'"][^\'"]*[\'"]\s*.*?\))'
    
    def client_call_replace(match):
        client_call = match.group(1)
        new_client_call = client_call.replace('client.', 'authenticated_client.')
        
        # Record the change
        changes.append({
            'original': client_call,
            'replacement': new_client_call
        })
        
        return new_client_call
    
    new_content = re.sub(client_call_pattern, client_call_replace, new_content)
    
    # Report changes
    if changes:
        print(f"\nFound {len(changes)} changes to make in {file_path}:")
        for i, change in enumerate(changes, 1):
            print(f"\nChange {i}:")
            print(f"Original: {change['original'][:100]}..." if len(change['original']) > 100 else f"Original: {change['original']}")
            print(f"New:      {change['replacement'][:100]}..." if len(change['replacement']) > 100 else f"New:      {change['replacement']}")
        
        if not dry_run:
            # Write changes to file
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"\nUpdated {file_path}")
        else:
            print(f"\nDRY RUN: No changes written to {file_path}")
    else:
        print(f"No changes needed in {file_path}")
    
    return len(changes)

def find_api_test_files(directory):
    """Find all API test files in the directory."""
    api_test_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Check if file contains API tests
                with open(file_path, 'r') as f:
                    content = f.read()
                    if '/api/' in content and 'client.' in content:
                        api_test_files.append(file_path)
    
    return api_test_files

def main():
    parser = argparse.ArgumentParser(description='Update API tests to use authenticated_client')
    parser.add_argument('--dir', default='tests', help='Directory containing test files')
    parser.add_argument('--file', help='Specific test file to update')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    args = parser.parse_args()
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return 1
        
        # Backup the file
        if not args.dry_run:
            backup_file(args.file)
        
        # Update the file
        changes = update_api_test_file(args.file, args.dry_run)
        print(f"\nTotal changes: {changes}")
    else:
        if not os.path.isdir(args.dir):
            print(f"Error: Directory {args.dir} not found")
            return 1
        
        # Find API test files
        api_test_files = find_api_test_files(args.dir)
        
        if not api_test_files:
            print(f"No API test files found in {args.dir}")
            return 0
        
        print(f"Found {len(api_test_files)} API test files:")
        for file in api_test_files:
            print(f"- {file}")
        
        # Confirm before proceeding
        if not args.dry_run:
            confirm = input("\nUpdate these files? (y/n): ")
            if confirm.lower() != 'y':
                print("Operation cancelled")
                return 0
        
        # Update each file
        total_changes = 0
        for file in api_test_files:
            if not args.dry_run:
                backup_file(file)
            changes = update_api_test_file(file, args.dry_run)
            total_changes += changes
        
        print(f"\nTotal changes across all files: {total_changes}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
