import datetime
import asyncio
from models.database import Message


async def clear_chat(collection):
    try:
        current_time = datetime.datetime.now()
        clear_day = current_time + datetime.timedelta(days=2)
        print('Run - (clear_chat)')
        while True:
            if current_time == clear_day:
                await Message.delete_all_messages(collection)
            else:
                await asyncio.sleep(172800)
    except asyncio.CancelledError:
        print('Ошибка таска')