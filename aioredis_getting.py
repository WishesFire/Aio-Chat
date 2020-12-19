import aioredis
from config import PASSWORD_REDIS


async def listen_to_redis():
    try:
        redis = await aioredis.create_redis_pool(('localhost', 8080), password=PASSWORD_REDIS)
        return redis
    except:
        redis = await aioredis.create_redis_pool('redis://localhost', password=PASSWORD_REDIS)