import json
import logging

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._pool = None
        self._client = None

    async def connect(self):
        try:
            self._pool = aioredis.ConnectionPool.from_url(
                f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
                if settings.REDIS_PASSWORD
                else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                max_connections=20,
            )
            self._client = aioredis.Redis(connection_pool=self._pool)
            await self._client.ping()
        except Exception:
            self._pool = None
            self._client = None
            logger.warning("Redis connection failed; cache and rate limit are disabled", exc_info=True)

    async def disconnect(self):
        if self._client:
            await self._client.close()
        self._client = None
        self._pool = None

    async def set(self, key: str, value, ttl: int | None = None):
        if not self._client:
            return
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, default=str)
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception:
            logger.warning("Redis set failed key=%s", key, exc_info=True)

    async def get(self, key: str):
        if not self._client:
            return None
        try:
            val = await self._client.get(key)
        except Exception:
            logger.warning("Redis get failed key=%s", key, exc_info=True)
            return None
        if val is None:
            return None
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val.decode("utf-8") if isinstance(val, bytes) else val

    async def delete(self, key: str):
        if not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception:
            logger.warning("Redis delete failed key=%s", key, exc_info=True)

    async def ping(self) -> bool:
        if not self._client:
            return False
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    @property
    def client(self):
        return self._client


redis_client = RedisClient()
