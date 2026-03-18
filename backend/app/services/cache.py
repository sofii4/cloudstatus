import json
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

async def set_service_status(service_id: int, data: dict):
    key = f"status:{service_id}"
    await redis_client.setex(key, 300, json.dumps(data))  # TTL: 5 min

async def get_service_status(service_id: int) -> dict | None:
    key = f"status:{service_id}"
    raw = await redis_client.get(key)
    return json.loads(raw) if raw else None

async def get_all_statuses() -> dict:
    keys = await redis_client.keys("status:*")
    if not keys:
        return {}
    values = await redis_client.mget(*keys)
    return {
        key.split(":")[1]: json.loads(val)
        for key, val in zip(keys, values)
        if val
    }