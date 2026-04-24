
import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from packages.ai.providers.openai_provider import OpenAIProvider
from packages.ai.providers.gemini_provider import GeminiProvider
from packages.ai.cache import ContentCache
from packages.ai.gpt_service import AwadeGPTService

class TestOpenAIProvider:
    @patch("packages.ai.providers.openai_provider.openai")
    def test_initialization(self, mock_openai):
        provider = OpenAIProvider(api_key="test-key")
        assert provider.client is not None
        mock_openai.OpenAI.assert_called_with(api_key="test-key")

    def test_get_model_name(self):
        provider = OpenAIProvider(api_key="test")
        assert provider._get_model_name("basic") == "gpt-4o-mini"
        assert provider._get_model_name("standard") == "gpt-4o"

class TestGeminiProvider:
    @patch("packages.ai.providers.gemini_provider.genai")
    def test_initialization(self, mock_genai):
        provider = GeminiProvider(api_key="test-key")
        assert provider.is_configured is True
        mock_genai.configure.assert_called_with(api_key="test-key")

    def test_get_model_name(self):
        provider = GeminiProvider(api_key="test")
        assert provider._get_model_name("basic") == "gemini-flash-latest"
        assert provider._get_model_name("standard") == "gemini-flash-latest"

class TestContentCache:
    @patch("packages.ai.cache.redis.Redis")
    def test_cache_miss(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        mock_client.get.return_value = None
        
        cache = ContentCache(host="localhost")
        result = cache.get("openai", "gpt-4", {"prompt": "hello"})
        
        assert result is None
        mock_client.get.assert_called()

    @patch("packages.ai.cache.redis.Redis")
    def test_cache_hit(self, mock_redis_cls):
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        mock_client.get.return_value = "cached content"
        
        cache = ContentCache(host="localhost")
        result = cache.get("openai", "gpt-4", {"prompt": "hello"})
        
        assert result == "cached content"

class TestGPTServiceIntegration:
    @patch("packages.ai.gpt_service.OpenAIProvider")
    @patch("packages.ai.gpt_service.ContentCache")
    def test_generation_flow(self, MockCache, MockProvider):
        # Setup Mocks
        mock_cache_instance = MockCache.return_value
        mock_cache_instance.get.return_value = None # Cache Miss
        
        mock_provider_instance = MockProvider.return_value
        mock_provider_instance.generate_content.return_value = '{"title_header": {}, "learning_objectives": [], "lesson_content": {}}'
        
        # Test
        service = AwadeGPTService(api_key="test", provider_type="openai")
        content, valid = service.generate_lesson_resource(
            subject="Math", grade="1", topic="Add", objectives=["Add numbers"]
        )
        
        # Verify
        assert valid is True
        mock_cache_instance.get.assert_called()
        mock_provider_instance.generate_content.assert_called()
        mock_cache_instance.set.assert_called()
