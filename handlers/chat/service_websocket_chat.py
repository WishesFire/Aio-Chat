from models.database import User, Message, Rooms, MessagesRoom
from config import PRIVATE_KEY_PATH
from cryptography.fernet import Fernet
import pickle
from tools.dh_key import decrypt_base
from tools.get_base import get_base_needed
from tools.RandomName import create_file_name
from aiohttp import web
from config import BASE_STATIC_DIR
import os
import base64


async def prepare_date_socket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    redis = request.app['db_redis']
    db, session = await get_base_needed(request)
    user_name = await User.get_user(db=db, data=session.get('user'))

    return redis, user_name, ws, db


async def message_manager(flag, index_room, data, user_name, redis, db, name, slug, room_name):
    if flag == 'message':
        """ 
            MESSAGE
        """
        if index_room == 'room' and room_name is not None:
            encrypted_text_bd, text = await text_message(redis, room_name, data)
            status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                     message=encrypted_text_bd)
            return status, text
        else:
            status = await Message.save_message(db=db, user=user_name, message=str(data.strip()))
            ls = await check_status_message(status, user_name, db)

            return ls

    else:
        index_file = data.find(f"data:{flag}")
        index_base = data.find("base64,")

        if index_file == -1 or index_base == -1:
            return False

        if flag == 'image':
            """
                IMAGE
            """
            send_name_photo_url = await image_message(
                data, index_room, index_file, index_base, user_name, redis, name, slug)
            if index_room == 'room':
                status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                         image=send_name_photo_url)
                return status, send_name_photo_url
            else:
                status = await Message.save_message(db=db, user=user_name, image=send_name_photo_url)
                ls = await check_status_message(status, user_name, db)

                return True, send_name_photo_url, ls

        elif flag == 'audio':
            """
                AUDIO
            """
            send_name_audio_url = await audio_message(data, index_room, index_base, name, slug)
            if index_room == 'room':
                status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                         audio=send_name_audio_url)
                return status, send_name_audio_url
            else:
                status = await Message.save_message(db=db, user=user_name, audio=send_name_audio_url)
                ls = await check_status_message(status, user_name, db)

                return True, send_name_audio_url, ls


async def image_message(data, index_room, index_photo_name, index_base_photo_content, user_name, redis, name, slug):
    photo_names = data[:index_photo_name][:-1]
    enlargement = len(str(photo_names))
    photo_name = create_file_name() + photo_names[enlargement - 4:]
    base_photo_content = data[index_base_photo_content + 7:]

    if index_room == 'room':
        path = name + slug
        normal_path = BASE_STATIC_DIR + '\\photos_room\\' + f'{path}'
        os.mkdir(normal_path)
        photo_name_url = os.path.join(normal_path + '\\' + photo_name)
        send_name_photo_url = f'../static/photos_room/{path}/{photo_name}'

        file = await read_file(base_photo_content)

        with open(photo_name_url, 'wb') as f:
            f.write(file)

        return send_name_photo_url

    else:
        photo_name_url = os.path.join(BASE_STATIC_DIR + '\\photos\\' + photo_name)
        send_name_photo_url = f'static/photos/{photo_name}'

        file = await read_file(base_photo_content)

        with open(photo_name_url, 'wb') as f:
            f.write(file)

        await save_check_photo(send_name_photo_url, user_name, redis)

        return send_name_photo_url


async def audio_message(data, index_room, index_base_audio_content, name, slug):
    audio_name = create_file_name() + '.mp3'
    base_audio_content = data[index_base_audio_content + 7:]

    if index_room == 'room':
        path = name + slug
        normal_path = BASE_STATIC_DIR + '\\audio_room\\' + f'{path}'
        os.mkdir(normal_path)
        audio_name_url = os.path.join(normal_path + '\\' + audio_name)
        send_name_audio_url = f'../static/audio_room/{str(path)}/{audio_name}'

        file = await read_file(base_audio_content)

        with open(audio_name_url, 'wb') as f:
            f.write(file)

        return send_name_audio_url

    else:
        audio_name_url = os.path.join(BASE_STATIC_DIR + '\\audio\\' + audio_name)
        send_name_audio_url = f'static/audio/{audio_name}'

        file = await read_file(base_audio_content)

        with open(audio_name_url, 'wb') as f:
            f.write(file)

        return send_name_audio_url


async def text_message(redis, room_name, data):
    # get key
    public_key = await redis.hgetall(room_name)
    public_key = public_key[b'public_key'].decode('utf-8')
    index = public_key[-1]
    if index == '@':
        public_key = public_key[:44]
    else:
        public_key = public_key[11:]
    public_key = public_key.encode()
    # main text
    text = await decrypt_base(data, public_key)
    text_bd = text
    text = text.decode('utf-8')
    # encrypt_text and get private_key
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        privat_key = pickle.load(f)
    cipher = Fernet(privat_key)
    encrypted_text_bd = cipher.encrypt(text_bd)

    return encrypted_text_bd, text


# TOOLS
async def check_status_message(status, user_name, db):
    if status:
        name_rooms = await Rooms.get_user_room(db=db, username=user_name)
        if name_rooms is None:
            ls = ''
        else:
            ls = []
            for room in name_rooms['rooms']:
                ls.append(room)

        return ls


async def read_file(file):
    return base64.b64decode(file)


async def save_check_photo(path, user_name, redis):
    await redis.hmset('avr', path, user_name)
