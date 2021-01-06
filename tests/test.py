import asyncio
import aioredis
from cryptography.fernet import Fernet
import pickle


async def main():
    redis = await aioredis.create_redis_pool('redis://localhost')
    #user = 'fgsdgsdfg'
    user1 = 'fdsagdfag12412412'
    #user3 = 'gadfgadfg'
    #bb = 1
    #cc = 2
    ll = b'4124125125125125'

    #await redis.hmset(user, bb, 1)
    #await redis.hmset(user, cc, 6)

    await redis.hmset(user1, 'public_key', ll)

    #a = await redis.hgetall(user, encoding='utf-8')
    b = await redis.hgetall(user1)
    #c = await redis.hgetall(user3)
    #print(a)
    print(b[b'public_key'])
    #print(c)

                    #user, whom_to_send
    #await redis.hdel(user, cc)
    #a = await redis.hgetall(user, encoding='utf-8')
    #print(a)

    await redis.delete(user1)
    #a = await redis.hgetall(user, encoding='utf-8')
    #print(a)


    redis.close()
    await redis.wait_closed()

#asyncio.run(main())


def conver():
    #1.кому 2.нік 3.кімната
    # нік: [нік-слаг, кімната, кімната-слаг]
    a = {'kogksdfo.---.gsdfgafg': 'fas132.---.gdsfg432432', 'kogk2sdfo.---.gsdfgafg': 'fas132.---.gdsfg432432'}
    l = {}
    for i in a:
        words2 = a[i].split('.---.')
        words1 = i.split('.---.')
        l[words1[0]] = [str(words1[1]), str(words2[0]), str(words2[1])]


#conver()

a = [{'message': [1, 'al1']}, {'audio': [2, 'd312aa']}, {'image': [1, 'url:31']}]
for i in a:
    if 'message' in i:
        print(i['message'][0])
    elif 'audio' in i:
        print(i['audio'][0])
    elif 'image' in i:
        print(i['image'][0])


{'KN8b49vh1l': ['message', b'gAAAAABf9hT266jsiRbqEcmLn4kHCnN-2uLEW-WKv38BO1gdBbnLl3ZnPNvhybXBqf-nDpv0s23dNC9mS3PsJ7-An2NK6GuKWQ==']}

