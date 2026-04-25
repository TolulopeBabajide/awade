import hashlib
import json
import logging
import os
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed. Caching disabled.")

class ContentCache:
    """
    Redis-based cache for AI generated content.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 2592000):
        """
        Initialize the cache.
        
        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis DB index
            ttl (int): Time to live in seconds (default 30 days)
        """
        self.ttl = ttl
        self.enabled = False
        self.client = None
        
        if REDIS_AVAILABLE:
            try:
                # Allow override from env vars
                host = os.getenv("REDIS_HOST", host)
                port = int(os.getenv("REDIS_PORT", port))
                
                self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                self.client.ping()
                self.enabled = True
                logger.info(f"ContentCache initialized (Redis: {host}:{port})")
            except Exception as e:
                logger.error(f"Failed to connect to Redis for caching: {e}")
                
    def _generate_key(self, provider: str, model: str, prompt_data: Dict[str, Any]) -> str:
        """
        Generate a deterministic cache key.
        Key includes provider and model to avoid serving GPT-3.5 quality for GPT-4 requests.
        """
        # Sort keys to ensure deterministic string
        prompt_str = json.dumps(prompt_data, sort_keys=True)
        
        # Create hash
        payload = f"{provider}:{model}:{prompt_str}"
        hash_digest = hashlib.sha256(payload.encode()).hexdigest()
        
        return f"ai_cache:{hash_digest}"

    def get(self, provider: str, model: str, prompt_data: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve content from cache.
        """
        if not self.enabled:
            return None
            
        try:
            key = self._generate_key(provider, model, prompt_data)
            cached_val = self.client.get(key)
            
            if cached_val:
                logger.info(f"Cache HIT for key: {key}")
                return cached_val
            
            logger.debug(f"Cache MISS for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            return None

    def set(self, provider: str, model: str, prompt_data: Dict[str, Any], content: str) -> None:
        """
        Save content to cache.
        """
        if not self.enabled:
            return
            
        try:
            key = self._generate_key(provider, model, prompt_data)
            self.client.setex(key, self.ttl, content)
            logger.debug(f"Cache SAVED for key: {key}")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
