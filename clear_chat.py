import datetime
import asyncio
from models.database import Message, User, Rooms, MessagesRoom
from config import BASE_STATIC_DIR, generate_key
import os


async def clear_chat(collection, redis):
    print('Launching back tasks!!!')
    try:
        current_time = datetime.datetime.now()
        clear_day = current_time + datetime.timedelta(days=2)
        print('Run - (clear_chat)')
        while True:
            if current_time == clear_day:
                # Clear redis
                users_lst = []
                users = await User.get_all_user(collection)
                for users in users:
                    users_lst.append(users['username'])
                await redis.delete(*users_lst)

                # Clear bd
                await Message.delete_all_messages(collection)
                await User.delete_all_users(collection)
                await Rooms.delete_all_room(collection)
                await MessagesRoom.delete_all_message_room(collection)

                # Clear static
                await clear_photos()
                await clear_photos_room()
                await clear_audio()
                await clear_audio_room()

                # Clear privat key
                await generate_key()

            else:
                await asyncio.sleep(172800)
    except asyncio.CancelledError:
        print('Ошибка таска')


async def clear_photos():
    path = BASE_STATIC_DIR + '\\photos'
    for file in os.listdir(path):
        os.remove(path + f'\\{file}')


async def clear_photos_room():
    path = BASE_STATIC_DIR + '\\photos_room'
    for file in os.listdir(path):
        os.rmdir(path + f'\\{file}')


async def clear_audio():
    path = BASE_STATIC_DIR + '\\audio'
    for file in os.listdir(path):
        os.remove(path + f'\\{file}')


async def clear_audio_room():
    path = BASE_STATIC_DIR + '\\audio_room'
    for file in os.listdir(path):
        os.rmdir(path + f'\\{file}')