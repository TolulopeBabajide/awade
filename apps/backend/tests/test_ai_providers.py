
import os
import pytest
from unittest.mock import patch

from packages.ai.providers.openai_provider import OpenAIProvider
from packages.ai.providers.gemini_provider import GeminiProvider
from packages.ai.cache import ContentCache


class TestOpenAIProvider:
    @patch("packages.ai.providers.openai_provider.openai")
    def test_initialization(self, mock_openai):
        provider = OpenAIProvider(api_key="test-key")
        assert provider.client is not None
        mock_openai.OpenAI.assert_called_with(
            api_key="test-key",
            timeout=OpenAIProvider.DEFAULT_TIMEOUT,
        )

    @patch("packages.ai.providers.openai_provider.openai")
    def test_initialization_custom_timeout(self, mock_openai):
        """OPENAI_TIMEOUT_SECONDS env var overrides the default timeout."""
        os.environ["OPENAI_TIMEOUT_SECONDS"] = "30"
        try:
            provider = OpenAIProvider(api_key="test-key")
            assert provider.timeout == 30.0
            mock_openai.OpenAI.assert_called_with(api_key="test-key", timeout=30.0)
        finally:
            del os.environ["OPENAI_TIMEOUT_SECONDS"]

    def test_get_model_name(self):
        provider = OpenAIProvider(api_key="test")
        assert provider._get_model_name("basic") == "gpt-4o-mini"
        assert provider._get_model_name("standard") == "gpt-4o"


class TestGeminiProvider:
    @patch("packages.ai.providers.gemini_provider.genai")
    def test_initialization(self, mock_genai):
        """Client is initialised with api_key and a default http_options timeout."""
        provider = GeminiProvider(api_key="test-key")
        assert provider.is_configured is True
        assert provider.timeout == GeminiProvider.DEFAULT_TIMEOUT
        mock_genai.Client.assert_called_once()
        call_kwargs = mock_genai.Client.call_args.kwargs
        assert call_kwargs.get("api_key") == "test-key"
        assert call_kwargs.get("http_options") is not None

    @patch("packages.ai.providers.gemini_provider.genai")
    def test_initialization_custom_timeout(self, mock_genai):
        """GEMINI_TIMEOUT_SECONDS env var overrides the default timeout."""
        os.environ["GEMINI_TIMEOUT_SECONDS"] = "45"
        try:
            provider = GeminiProvider(api_key="test-key")
            assert provider.timeout == 45.0
            call_kwargs = mock_genai.Client.call_args.kwargs
            http_opts = call_kwargs.get("http_options")
            assert http_opts is not None
            assert http_opts.timeout == 45.0
        finally:
            del os.environ["GEMINI_TIMEOUT_SECONDS"]

    def test_get_model_name(self):
        provider = GeminiProvider(api_key="test")
        assert provider._get_model_name("basic") == "gemini-flash-latest"
        assert provider._get_model_name("standard") == "gemini-flash-latest"


class TestContentCache:
    @patch("packages.ai.cache.redis.Redis")
    def test_cache_miss(self, mock_redis_cls):
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        mock_client.get.return_value = None

        cache = ContentCache(host="localhost")
        result = cache.get("openai", "gpt-4", {"prompt": "hello"})

        assert result is None
        mock_client.get.assert_called()

    @patch("packages.ai.cache.redis.Redis")
    def test_cache_hit(self, mock_redis_cls):
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        mock_client.get.return_value = "cached content"

        cache = ContentCache(host="localhost")
        result = cache.get("openai", "gpt-4", {"prompt": "hello"})

        assert result == "cached content"

    @patch("packages.ai.cache.redis.Redis")
    def test_cache_set_calls_setex(self, mock_redis_cls):
        """ContentCache.set() must call setex(key, ttl, content) — API contract for redis 8.x."""
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client

        cache = ContentCache(host="localhost", ttl=3600)
        cache.set("openai", "gpt-4", {"prompt": "hello"}, "generated text")

        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args
        # setex(key, time, value) — key is a string, ttl matches constructor arg
        key_arg, ttl_arg, value_arg = call_args.args
        assert key_arg.startswith("ai_cache:")
        assert ttl_arg == 3600
        assert value_arg == "generated text"

    @patch("packages.ai.cache.redis.Redis")
    def test_cache_disabled_on_redis_connection_error(self, mock_redis_cls):
        """When Redis.ping() raises, cache must disable itself and not surface the error."""
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_redis_cls.return_value = mock_client
        mock_client.ping.side_effect = Exception("connection refused")

        cache = ContentCache(host="localhost")

        assert cache.enabled is False
        # get/set must be no-ops — must not raise
        assert cache.get("openai", "gpt-4", {"prompt": "x"}) is None
        cache.set("openai", "gpt-4", {"prompt": "x"}, "content")
