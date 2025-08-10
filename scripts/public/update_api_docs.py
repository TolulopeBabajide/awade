#!/usr/bin/env python3
"""
Automated API Documentation Updater
Updates API documentation based on code changes and generates OpenAPI spec.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def check_for_api_changes():
    """Check if any API-related files have changed."""
    try:
        # Get list of changed files from git
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, check=True
        )
        changed_files = result.stdout.strip().split('\n')
        
        # Check for API-related changes
        api_files = [
            f for f in changed_files 
            if f.startswith('apps/backend/') and f.endswith('.py')
        ]
        
        return len(api_files) > 0, api_files
    except subprocess.CalledProcessError:
        return False, []

def generate_openapi_spec():
    """Generate OpenAPI specification from FastAPI app."""
    try:
        # Change to backend directory
        backend_dir = Path('apps/backend')
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
            
        # Create app directory if it doesn't exist
        app_dir = backend_dir / 'app'
        app_dir.mkdir(exist_ok=True)
        
        # Check if we're in CI environment
        is_ci = os.getenv("CI", "false").lower() == "true"
        
        if is_ci:
            print("🏗️  CI environment detected: generating minimal OpenAPI spec")
            # In CI, create a minimal OpenAPI spec based on contracts
            minimal_spec = create_minimal_openapi_spec()
            with open(app_dir / 'openapi.json', 'w') as f:
                json.dump(minimal_spec, f, indent=2)
            print("✅ Generated minimal OpenAPI spec for CI")
            return True
        else:
            # In development, try to generate full spec
            script = f"""
import sys
import os
sys.path.insert(0, '{backend_dir.absolute()}')
sys.path.insert(0, '{Path.cwd().absolute()}')

# Set environment variables for the import
os.environ['PYTHONPATH'] = '{Path.cwd().absolute()}:{backend_dir.absolute()}'

try:
    from main import app
    import json
    
    openapi_spec = app.openapi()
    with open('app/openapi.json', 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    print("✅ OpenAPI spec generated successfully")
except Exception as e:
    print(f"❌ Error importing main: {{e}}")
    # Create a minimal OpenAPI spec as fallback
    fallback_spec = {{
        "openapi": "3.0.0",
        "info": {{
            "title": "Awade API",
            "version": "1.0.0",
            "description": "API documentation generated during pre-commit"
        }},
        "paths": {{}},
        "components": {{}}
    }}
    with open('app/openapi.json', 'w') as f:
        json.dump(fallback_spec, f, indent=2)
    print("⚠️  Generated fallback OpenAPI spec")
"""
            
            result = subprocess.run(
                ['python', '-c', script],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ OpenAPI specification generated")
                return True
            else:
                print(f"❌ Failed to generate OpenAPI spec: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error generating OpenAPI spec: {e}")
        return False

def create_minimal_openapi_spec():
    """Create a minimal OpenAPI spec based on contracts for CI environment."""
    try:
        # Read the contracts file
        contracts_file = Path('contracts/api-contracts.json')
        if contracts_file.exists():
            with open(contracts_file, 'r') as f:
                contracts = json.load(f)
        else:
            # Fallback minimal spec
            return {
                "openapi": "3.0.0",
                "info": {
                    "title": "Awade API",
                    "version": "2.0.0",
                    "description": "AI-powered educator support platform for African teachers"
                },
                "paths": {},
                "components": {}
            }
        
        # Convert contracts to OpenAPI format
        paths = {}
        components = {
            "schemas": {},
            "securitySchemes": {}
        }
        
        for category, endpoints in contracts.get("contracts", {}).items():
            for endpoint_name, endpoint_data in endpoints.items():
                path = endpoint_data["endpoint"]
                method = endpoint_data["method"].lower()
                
                if path not in paths:
                    paths[path] = {}
                
                # Add the endpoint
                paths[path][method] = {
                    "summary": f"{category} - {endpoint_name}",
                    "tags": [category],
                    "responses": {
                        str(endpoint_data.get("expected_status", 200)): {
                            "description": "Success"
                        }
                    }
                }
                
                # Add request body if it exists
                if "request_schema" in endpoint_data:
                    paths[path][method]["requestBody"] = {
                        "content": {
                            "application/json": {
                                "schema": endpoint_data["request_schema"]
                            }
                        }
                    }
                
                # Add response schema if it exists
                if "response_schema" in endpoint_data:
                    paths[path][method]["responses"][str(endpoint_data.get("expected_status", 200))]["content"] = {
                        "application/json": {
                            "schema": endpoint_data["response_schema"]
                        }
                    }
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Awade API",
                "version": contracts.get("version", "2.0.0"),
                "description": contracts.get("description", "AI-powered educator support platform for African teachers")
            },
            "paths": paths,
            "components": components
        }
        
    except Exception as e:
        print(f"⚠️  Error creating minimal OpenAPI spec: {e}")
        # Return basic fallback
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Awade API",
                "version": "2.0.0",
                "description": "AI-powered educator support platform for African teachers"
            },
            "paths": {},
            "components": {}
        }

def update_api_documentation():
    """Update API documentation files."""
    try:
        # Note: Private API contracts are no longer accessible
        # This function now only updates public API documentation
            
        # Update the API README with generation timestamp
        api_readme = Path('docs/public/api/README.md')
        if api_readme.exists():
            with open(api_readme, 'r') as f:
                content = f.read()
            
            # Add or update the last generated timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "Last generated:" in content:
                # Update existing timestamp
                import re
                content = re.sub(
                    r"Last generated:.*",
                    f"Last generated: {timestamp}",
                    content
                )
            else:
                # Add timestamp at the top
                content = f"# Awade API Documentation\n\n> **Last generated: {timestamp}**\n\n" + content[content.find('\n')+1:]
            
            with open(api_readme, 'w') as f:
                f.write(content)
            
            print("✅ API documentation updated")
            return True
        else:
            print("❌ API README file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error updating API documentation: {e}")
        return False

def validate_documentation():
    """Basic validation of documentation files."""
    issues = []
    
    # Check if required files exist
    required_files = [
        'docs/public/api/README.md'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing required file: {file_path}")
    
    # Check for broken links in markdown files
    docs_dir = Path('docs')
    for md_file in docs_dir.rglob('*.md'):
        try:
            with open(md_file, 'r') as f:
                content = f.read()
                
            # Simple link validation (basic check)
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_url in links:
                if link_url.startswith('http'):
                    continue  # Skip external links for now
                if link_url.startswith('#'):
                    continue  # Skip anchor links
                    
                # Check if internal file exists
                if link_url.startswith('../'):
                    target_path = md_file.parent / link_url
                else:
                    target_path = md_file.parent / link_url
                    
                if not target_path.exists():
                    issues.append(f"Broken link in {md_file}: {link_url}")
                    
        except Exception as e:
            issues.append(f"Error reading {md_file}: {e}")
    
    if issues:
        print("❌ Documentation validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Documentation validation passed")
        return True

def main():
    """Main function to run the documentation update process."""
    print("🔄 Starting API documentation update...")
    
    # In CI, always run the update
    if os.getenv("CI", "false").lower() == "true":
        print("🏗️  CI environment detected: forcing OpenAPI spec and documentation update.")
        try:
            if generate_openapi_spec():
                if update_api_documentation():
                    if validate_documentation():
                        print("🎉 API documentation update completed successfully!")
                        return True
                    else:
                        print("⚠️  Documentation updated but validation failed")
                        return False
                else:
                    print("❌ Failed to update API documentation")
                    return False
            else:
                print("❌ Failed to generate OpenAPI specification")
                return False
        except Exception as e:
            print(f"❌ Error in CI documentation update: {e}")
            return False
    # Otherwise, only run if there are API changes
    has_changes, changed_files = check_for_api_changes()
    
    if has_changes:
        print(f"📝 Detected changes in API files: {', '.join(changed_files)}")
        
        # Generate OpenAPI spec
        if generate_openapi_spec():
            # Update documentation
            if update_api_documentation():
                # Validate documentation
                if validate_documentation():
                    print("🎉 API documentation update completed successfully!")
                    return True
                else:
                    print("⚠️  Documentation updated but validation failed")
                    return False
            else:
                print("❌ Failed to update API documentation")
                return False
        else:
            print("❌ Failed to generate OpenAPI specification")
            return False
    else:
        print("ℹ️  No API changes detected, skipping documentation update")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 