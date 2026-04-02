import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def init_cache():
    global _redis
    try:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis.ping()
        logger.info("Redis cache connected.")
    except Exception as e:
        logger.warning(f"Redis unavailable, caching disabled: {e}")
        _redis = None


async def close_cache():
    global _redis
    if _redis:
        await _redis.aclose()
        logger.info("Redis connection closed.")


async def get_cached(key: str) -> Optional[Any]:
    if not _redis:
        return None
    try:
        value = await _redis.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Cache GET error for key '{key}': {e}")
    return None


async def set_cached(key: str, value: Any, ttl: int):
    if not _redis:
        return
    try:
        await _redis.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.warning(f"Cache SET error for key '{key}': {e}")


async def invalidate(key: str):
    if not _redis:
        return
    try:
        await _redis.delete(key)
    except Exception as e:
        logger.warning(f"Cache DELETE error for key '{key}': {e}")
