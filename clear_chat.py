import datetime
import asyncio
from models.database import Message, User, Rooms, MessagesRoom
from config import BASE_STATIC_DIR
import os


async def clear_chat(collection):
    try:
        current_time = datetime.datetime.now()
        clear_day = current_time + datetime.timedelta(days=2)
        print('Run - (clear_chat)')
        while True:
            if current_time == clear_day:
                await Message.delete_all_messages(collection)
                await User.delete_all_users(collection)
                await Rooms.delete_all_room(collection)
                await MessagesRoom.delete_all_message_room(collection)
                await clear_photo()
            else:
                await asyncio.sleep(172800)
    except asyncio.CancelledError:
        print('Ошибка таска')


async def clear_photo():
    path = BASE_STATIC_DIR + '\\photos'
    for file in os.listdir(path):
        os.remove(path + f'\\{file}')