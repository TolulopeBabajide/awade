#!/usr/bin/env python3
"""
Script to fix import issues in all service files by adding the path setup.
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    print(f"Fixing imports in {file_path}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file already has the path setup
    if "sys.path.extend" in content:
        print(f"  {file_path} already has path setup, skipping...")
        return
    
    # Check if the file has apps.backend imports
    if "from apps.backend." not in content:
        print(f"  {file_path} has no apps.backend imports, skipping...")
        return
    
    # Find the first import line
    lines = content.split('\n')
    insert_index = 0
    
    # Find where to insert the path setup (after the docstring and before imports)
    for i, line in enumerate(lines):
        if line.strip().startswith('from ') or line.strip().startswith('import '):
            insert_index = i
            break
    
    # Insert the path setup
    path_setup = [
        "import sys",
        "import os",
        "",
        "# Add parent directories to Python path for imports",
        "current_dir = os.path.dirname(__file__)",
        "parent_dir = os.path.dirname(current_dir)",
        "root_dir = os.path.dirname(parent_dir)",
        "sys.path.extend([parent_dir, root_dir])",
        ""
    ]
    
    # Insert the path setup
    for i, setup_line in enumerate(path_setup):
        lines.insert(insert_index + i, setup_line)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✅ Fixed {file_path}")

def main():
    """Fix imports in all service files."""
    services_dir = "services"
    
    if not os.path.exists(services_dir):
        print(f"Services directory {services_dir} not found!")
        return
    
    # Get all Python files in the services directory
    service_files = [f for f in os.listdir(services_dir) if f.endswith('.py') and f != '__init__.py']
    
    print(f"Found {len(service_files)} service files to check...")
    
    for service_file in service_files:
        file_path = os.path.join(services_dir, service_file)
        fix_imports_in_file(file_path)
    
    print("✅ All service files processed!")

if __name__ == "__main__":
    main()
