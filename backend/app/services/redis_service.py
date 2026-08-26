import json
import asyncio
from typing import AsyncGenerator, Optional
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Redis pub/sub service with fallback to in-memory when Redis is unavailable."""

    def __init__(self, redis_url: str, enabled: bool = True):
        self.redis_url = redis_url
        self.enabled = enabled
        self.redis_client = None
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    async def connect(self):
        if not self.enabled:
            logger.info("Redis disabled — using in-memory pub/sub for development.")
            return

        try:
            import redis.asyncio as aioredis
            self.redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}), falling back to in-memory pub/sub.")
            self.redis_client = None

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.aclose()
            logger.info("Disconnected from Redis.")

    async def publish(self, channel: str, message: dict):
        if self.redis_client:
            try:
                await self.redis_client.publish(channel, json.dumps(message))
                return
            except Exception as e:
                logger.error(f"Failed to publish to Redis {channel}: {e}")

        # In-memory fallback
        if channel in self._subscribers:
            for queue in self._subscribers[channel]:
                await queue.put(message)

    async def subscribe(self, channel: str) -> AsyncGenerator[dict, None]:
        if self.redis_client:
            import redis.asyncio as aioredis
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            yield data
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON received on {channel}")
            finally:
                await pubsub.unsubscribe(channel)
                await pubsub.aclose()
        else:
            # In-memory fallback
            queue: asyncio.Queue = asyncio.Queue()
            if channel not in self._subscribers:
                self._subscribers[channel] = []
            self._subscribers[channel].append(queue)
            try:
                while True:
                    data = await queue.get()
                    yield data
            finally:
                self._subscribers[channel].remove(queue)
