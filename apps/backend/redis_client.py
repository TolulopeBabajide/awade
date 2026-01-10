
import os
from arq.connections import RedisSettings, ArqRedis, create_pool

# Get Redis configuration from environment
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

async def get_redis_settings() -> RedisSettings:
    """
    Get Redis configuration settings.
    """
    return RedisSettings(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )

async def create_redis_pool() -> ArqRedis:
    """
    Create and return a Redis connection pool.
    """
    settings = await get_redis_settings()
    return await create_pool(settings)
