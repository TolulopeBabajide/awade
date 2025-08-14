#!/usr/bin/env python3
"""
Test script for GPT-5 features in the Awade AI service.

This script demonstrates:
- GPT-5 configuration and capabilities
- Different reasoning effort levels
- Verbosity control
- The new Responses API method
"""

import os
import sys
import json
from typing import Dict, Any

# Add parent directories to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

from packages.ai.gpt_service import AwadeGPTService

def test_gpt5_configuration():
    """Test GPT-5 configuration and capabilities."""
    print("=== Testing GPT-5 Configuration ===")
    
    # Initialize service
    service = AwadeGPTService()
    
    print(f"Model: {service.model}")
    print(f"Reasoning Effort: {service.reasoning_effort}")
    print(f"Verbosity: {service.verbosity}")
    print(f"Client Initialized: {bool(service.client)}")
    
    # Test GPT-5 capabilities
    capabilities = service.get_gpt5_capabilities()
    print("\nGPT-5 Capabilities:")
    print(json.dumps(capabilities, indent=2))
    
    return service

def test_connection_status(service: AwadeGPTService):
    """Test connection status and GPT-5 features."""
    print("\n=== Testing Connection Status ===")
    
    status = service.test_openai_connection()
    print("Connection Status:")
    print(json.dumps(status, indent=2))
    
    if status.get("supports_gpt5_features"):
        print("\n✅ GPT-5 features are supported!")
    else:
        print("\n❌ GPT-5 features are not supported")

def test_different_configurations():
    """Test different GPT-5 configurations."""
    print("\n=== Testing Different GPT-5 Configurations ===")
    
    # Test with minimal reasoning effort
    service_minimal = AwadeGPTService()
    service_minimal.reasoning_effort = "minimal"
    service_minimal.verbosity = "low"
    
    print(f"Minimal Configuration:")
    print(f"  Reasoning Effort: {service_minimal.reasoning_effort}")
    print(f"  Verbosity: {service_minimal.verbosity}")
    
    # Test with high reasoning effort
    service_high = AwadeGPTService()
    service_high.reasoning_effort = "high"
    service_high.verbosity = "high"
    
    print(f"\nHigh Configuration:")
    print(f"  Reasoning Effort: {service_high.reasoning_effort}")
    print(f"  Verbosity: {service_high.verbosity}")

def test_responses_api_method(service: AwadeGPTService):
    """Test the new GPT-5 Responses API method."""
    print("\n=== Testing GPT-5 Responses API Method ===")
    
    if not service.client:
        print("❌ OpenAI client not available - cannot test API calls")
        return
    
    try:
        # Test the new method
        result = service.generate_lesson_resource_gpt5_responses_api(
            subject="Mathematics",
            grade="Grade 5",
            topic="Fractions",
            learning_objectives=["Understand parts of whole", "Compare fractions"],
            contents=["Fraction concepts", "Visual representation"],
            duration=45,
            local_context="Nigerian classroom with basic resources"
        )
        
        print("✅ GPT-5 Responses API method executed successfully!")
        print(f"Status: {result.get('status')}")
        print(f"Response ID: {result.get('response_id', 'N/A')}")
        
        if result.get('reasoning_items'):
            print(f"Reasoning Items: {len(result['reasoning_items'])} items")
        
    except Exception as e:
        print(f"❌ Error testing Responses API method: {e}")

def main():
    """Main test function."""
    print("🚀 Testing Awade GPT-5 AI Service Features")
    print("=" * 50)
    
    # Test basic configuration
    service = test_gpt5_configuration()
    
    # Test connection status
    test_connection_status(service)
    
    # Test different configurations
    test_different_configurations()
    
    # Test Responses API method
    test_responses_api_method(service)
    
    print("\n" + "=" * 50)
    print("✅ GPT-5 feature testing completed!")
    
    # Print configuration summary
    print("\n📋 Configuration Summary:")
    print(f"  Model: {service.model}")
    print(f"  Reasoning Effort: {service.reasoning_effort}")
    print(f"  Verbosity: {service.verbosity}")
    print(f"  Max Tokens: {service.max_tokens}")
    
    if service.model.startswith("gpt-5"):
        print("\n🎯 GPT-5 is configured and ready!")
        print("   - Use reasoning_effort to control response quality")
        print("   - Use verbosity to control response length")
        print("   - Use generate_lesson_resource_gpt5_responses_api() for best performance")
    else:
        print("\n⚠️  Not using GPT-5 model")

if __name__ == "__main__":
    main()
