import asyncio
import aioredis
import numpy as np
from cryptography.fernet import Fernet
import pickle


async def main():
    redis = await aioredis.create_redis_pool('redis://localhost')
    user = 'fgsdgsdfg'
    user1 = 'fdsagdfag12412412'
    user3 = 'gadfgadfg'
    bb = 1
    cc = 2
    ll = 3

    await redis.hmset('queue', 1, 1)
    await redis.hmset('queue', 3, 6)
    a = await redis.hgetall('queue', encoding='utf-8')
    print(a)

    #await redis.hdel(user, cc)
    #a = await redis.hgetall(user, encoding='utf-8')
    #print(a)

    await redis.delete(user)
    await redis.delete(user1)
    await redis.delete(user3)
    #a = await redis.hgetall(user, encoding='utf-8')
    #print(a)


    redis.close()
    await redis.wait_closed()

#asyncio.run(main())

a = np.array([])
a = np.append(a, )