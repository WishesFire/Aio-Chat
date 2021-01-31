import asyncio
import aioredis


async def main():
    redis = await aioredis.create_redis_pool('redis://localhost')
    user = 'fgsdgsdfg'
    user1 = 'fdsagdfag12412412'
    user3 = 'gadfgadfg'
    bb = 1
    cc = 2
    ll = 3

    await redis.hmset('avr', 1, 'url:123')
    await redis.hmset('avr', 3, 'url:321')
    a = await redis.hgetall('a', encoding='utf-8')
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

asyncio.run(main())