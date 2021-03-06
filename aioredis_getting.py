import aioredis
from config import PASSWORD_REDIS


async def listen_to_redis():
    try:
        print('Normal Redis')
        redis = await aioredis.create_redis_pool(('localhost', 8080), password=PASSWORD_REDIS)
        return redis
    except:
        print('Error Redis')
        redis = await aioredis.create_redis_pool('redis://localhost', password=PASSWORD_REDIS)


async def redis_convert(dct):
    new_redis_dict = {}

    for i in dct:
        words1 = i.split('.---.')
        words2 = dct[i].split('.---.')
        status = words1[1].find('___-%-_')
        if status != -1:
            from_whom = words1[1][:status]
            new_redis_dict[words1[0] + f'-({len(new_redis_dict)})'] = [from_whom, str(words2[0]), str(words2[1])]
            continue

        new_redis_dict[words1[0]] = [str(words1[1]), str(words2[0]), str(words2[1])]

    return new_redis_dict
