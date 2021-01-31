from nudenet import NudeClassifier
from models.database import Message
import asyncio


async def sex_message_check(redis, db):
    classifier = NudeClassifier()
    while True:
        lst = await redis.hgetall('avr', encoding='utf-8')
        if not lst == {}:
            for i in lst.keys():
                path = lst[i]
                status = classifier.classify(path)
                if status[path]['safe'] < status[path]['unsafe']:
                    await Message.delete_image(db=db, user=i, image=path)

        await asyncio.sleep(10)