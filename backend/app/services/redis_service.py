import json
import redis.asyncio as redis
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None

    async def connect(self):
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.aclose()
            logger.info("Disconnected from Redis.")

    async def publish(self, channel: str, message: dict):
        if self.redis_client:
            try:
                await self.redis_client.publish(channel, json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to publish to {channel}: {e}")

    async def subscribe(self, channel: str) -> AsyncGenerator[dict, None]:
        if not self.redis_client:
            return
            
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
