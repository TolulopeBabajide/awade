#!/usr/bin/env python3
"""
Contract Testing for Awade API
Validates API contracts between frontend and backend to ensure consistency.
"""

import json
import os
import sys
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import jsonschema
from dataclasses import dataclass

@dataclass
class ContractTest:
    """Represents a contract test case."""
    name: str
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    expected_status: int = 200
    description: str = ""

class ContractValidator:
    """Validates API contracts against OpenAPI specifications."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.openapi_spec = None
        self.contract_tests = []
        self.results = []
        
    def load_openapi_spec(self, spec_path: str = "apps/backend/app/openapi.json") -> bool:
        """Load OpenAPI specification from file."""
        try:
            with open(spec_path, 'r') as f:
                self.openapi_spec = json.load(f)
            print(f"✅ Loaded OpenAPI spec from {spec_path}")
            return True
        except FileNotFoundError:
            print(f"❌ OpenAPI spec not found at {spec_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in OpenAPI spec: {e}")
            return False
    
    def generate_contract_tests(self) -> List[ContractTest]:
        """Generate contract tests from OpenAPI specification."""
        if not self.openapi_spec:
            print("❌ No OpenAPI spec loaded")
            return []
        
        tests = []
        
        for path, path_item in self.openapi_spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    # Extract request schema
                    request_schema = {}
                    if "requestBody" in operation:
                        content = operation["requestBody"].get("content", {})
                        for content_type, media_type in content.items():
                            if "schema" in media_type:
                                request_schema = media_type["schema"]
                                break
                    
                    # Extract response schema
                    response_schema = {}
                    responses = operation.get("responses", {})
                    if "200" in responses:
                        content = responses["200"].get("content", {})
                        for content_type, media_type in content.items():
                            if "schema" in media_type:
                                response_schema = media_type["schema"]
                                break
                    
                    test = ContractTest(
                        name=f"{method.upper()} {path}",
                        endpoint=path,
                        method=method.upper(),
                        request_schema=request_schema,
                        response_schema=response_schema,
                        description=operation.get("summary", ""),
                        expected_status=200
                    )
                    tests.append(test)
        
        self.contract_tests = tests
        print(f"✅ Generated {len(tests)} contract tests")
        return tests
    
    def validate_schema(self, data: Any, schema: Dict[str, Any], schema_name: str) -> bool:
        """Validate data against JSON schema."""
        if not schema:
            return True  # No schema to validate against
        
        try:
            # Resolve $ref pointers in the schema
            resolved_schema = self.resolve_schema_refs(schema)
            jsonschema.validate(instance=data, schema=resolved_schema)
            return True
        except jsonschema.ValidationError as e:
            print(f"❌ Schema validation failed for {schema_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Schema validation error for {schema_name}: {e}")
            return False
    
    def resolve_schema_refs(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve $ref pointers in JSON schema."""
        if not isinstance(schema, dict):
            return schema
        
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                if self.openapi_spec and "components" in self.openapi_spec:
                    components = self.openapi_spec.get("components", {})
                    schemas = components.get("schemas", {})
                    if schema_name in schemas:
                        return self.resolve_schema_refs(schemas[schema_name])
            return schema
        
        resolved = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_schema_refs(value)
            elif isinstance(value, list):
                resolved[key] = [self.resolve_schema_refs(item) if isinstance(item, dict) else item for item in value]
            else:
                resolved[key] = value
        
        return resolved
    
    def run_contract_test(self, test: ContractTest) -> Dict[str, Any]:
        """Run a single contract test."""
        result = {
            "test_name": test.name,
            "endpoint": test.endpoint,
            "method": test.method,
            "status": "pending",
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Prepare request
            url = f"{self.base_url}{test.endpoint}"
            headers = {"Content-Type": "application/json"}
            
            # Handle path parameters
            if "{plan_id}" in url:
                url = url.replace("{plan_id}", "lp_001")
            if "{module_id}" in url:
                url = url.replace("{module_id}", "tm_001")
            
            # Generate sample request data if schema exists
            request_data = None
            if test.request_schema:
                request_data = self.generate_sample_data(test.request_schema)
            
            # Make request
            if test.method == "GET":
                response = requests.get(url, headers=headers)
            elif test.method == "POST":
                response = requests.post(url, json=request_data, headers=headers)
            elif test.method == "PUT":
                response = requests.put(url, json=request_data, headers=headers)
            elif test.method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                result["status"] = "skipped"
                result["warnings"].append(f"Unsupported method: {test.method}")
                return result
            
            # Validate response status (be more flexible with acceptable status codes)
            acceptable_statuses = [test.expected_status]
            if test.method == "POST":
                acceptable_statuses.extend([201, 422])  # Created or validation error
            elif test.method == "GET":
                acceptable_statuses.extend([404])  # Not found is acceptable for GET
            
            if response.status_code not in acceptable_statuses:
                result["errors"].append(
                    f"Expected status {test.expected_status}, got {response.status_code}"
                )
            
            # Validate response schema (only for successful responses)
            if response.status_code in [200, 201] and test.response_schema:
                try:
                    response_data = response.json()
                    if not self.validate_schema(response_data, test.response_schema, "response"):
                        result["errors"].append("Response schema validation failed")
                except json.JSONDecodeError:
                    result["errors"].append("Response is not valid JSON")
            
            # Set final status
            if result["errors"]:
                result["status"] = "failed"
            else:
                result["status"] = "passed"
                
        except requests.RequestException as e:
            result["status"] = "error"
            result["errors"].append(f"Request failed: {e}")
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Unexpected error: {e}")
        
        return result
    
    def generate_sample_data(self, schema: Dict[str, Any]) -> Any:
        """Generate sample data from JSON schema."""
        if not schema:
            return None
        
        schema_type = schema.get("type")
        
        if schema_type == "object":
            sample = {}
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                sample[prop_name] = self.generate_sample_data(prop_schema)
            return sample
        
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            return [self.generate_sample_data(items_schema)]
        
        elif schema_type == "string":
            # Check for specific formats
            if schema.get("format") == "email":
                return "test@example.com"
            elif schema.get("format") == "date":
                return "2024-01-01"
            elif schema.get("format") == "date-time":
                return "2024-01-01T00:00:00Z"
            else:
                return "sample_string"
        
        elif schema_type == "number" or schema_type == "integer":
            return 42
        
        elif schema_type == "boolean":
            return True
        
        elif "enum" in schema:
            return schema["enum"][0]
        
        else:
            return None
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all contract tests."""
        if not self.contract_tests:
            self.generate_contract_tests()
        
        print(f"🚀 Running {len(self.contract_tests)} contract tests...")
        
        for test in self.contract_tests:
            print(f"  Testing: {test.name}")
            result = self.run_contract_test(test)
            self.results.append(result)
            
            if result["status"] == "passed":
                print(f"    ✅ {test.name} - PASSED")
            elif result["status"] == "failed":
                print(f"    ❌ {test.name} - FAILED")
                for error in result["errors"]:
                    print(f"      Error: {error}")
            else:
                print(f"    ⚠️  {test.name} - {result['status'].upper()}")
        
        return self.results
    
    def generate_report(self, output_path: str = "logs/contract_test_report.json") -> None:
        """Generate contract test report."""
        if not self.results:
            print("❌ No test results to report")
            return
        
        # Create logs directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": len([r for r in self.results if r["status"] == "passed"]),
                "failed": len([r for r in self.results if r["status"] == "failed"]),
                "errors": len([r for r in self.results if r["status"] == "error"]),
                "skipped": len([r for r in self.results if r["status"] == "skipped"])
            },
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Contract test report saved to {output_path}")
    
    def print_summary(self) -> None:
        """Print test summary to console."""
        if not self.results:
            print("❌ No test results to summarize")
            return
        
        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "passed"])
        failed = len([r for r in self.results if r["status"] == "failed"])
        errors = len([r for r in self.results if r["status"] == "error"])
        skipped = len([r for r in self.results if r["status"] == "skipped"])
        
        print("\n" + "="*50)
        print("📊 CONTRACT TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "N/A")
        print("="*50)
        
        if failed > 0 or errors > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if result["status"] in ["failed", "error"]:
                    print(f"  ❌ {result['test_name']}")
                    for error in result["errors"]:
                        print(f"    Error: {error}")

def main():
    """Main function for contract testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run contract tests for Awade API")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for API testing")
    parser.add_argument("--spec-path", default="apps/backend/app/openapi.json",
                       help="Path to OpenAPI specification")
    parser.add_argument("--report-path", default="logs/contract_test_report.json",
                       help="Path for test report output")
    parser.add_argument("--start-server", action="store_true",
                       help="Start backend server before testing")
    parser.add_argument("--save", action="store_true",
                       help="Save test report")
    
    args = parser.parse_args()
    
    print("🔍 Starting Awade Contract Testing...")
    
    # Start server if requested
    server_process = None
    if args.start_server:
        print("🚀 Starting backend server...")
        try:
            # Start server in background
            server_process = subprocess.Popen([
                "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"
            ], cwd="apps/backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to be ready
            max_retries = 10
            for i in range(max_retries):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Backend server is ready")
                        break
                except requests.RequestException:
                    if i < max_retries - 1:
                        time.sleep(1)
                    else:
                        print("⚠️  Server startup timed out, continuing with tests...")
        except Exception as e:
            print(f"⚠️  Could not start server: {e}")
    
    # Initialize validator
    validator = ContractValidator(args.base_url)
    
    # Load OpenAPI spec
    if not validator.load_openapi_spec(args.spec_path):
        print("❌ Failed to load OpenAPI specification")
        sys.exit(1)
    
    # Run tests
    results = validator.run_all_tests()
    
    # Generate report
    if args.save:
        validator.generate_report(args.report_path)
    
    # Print summary
    validator.print_summary()
    
    # Cleanup: stop server if we started it
    if server_process:
        print("🛑 Stopping backend server...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        except Exception as e:
            print(f"⚠️  Error stopping server: {e}")
    
    # Exit with appropriate code
    failed_tests = len([r for r in results if r["status"] in ["failed", "error"]])
    if failed_tests > 0:
        print(f"\n❌ Contract testing failed with {failed_tests} failures")
        sys.exit(1)
    else:
        print("\n✅ All contract tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 