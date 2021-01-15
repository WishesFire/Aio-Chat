from aiohttp import web, WSMsgType
from models.database import Rooms, MessagesRoom, User
from tools.get_base import get_base_needed
from tools.csrf_token import generate_token, check_token
from tools.RandomName import create_file_name
from handlers.commands import time_now, curs_now
from tools.dh_key import decrypt_base
from config import BASE_STATIC_DIR, PRIVATE_KEY, PRIVATE_KEY_PATH, SITE_STORAGE
from cryptography.fernet import Fernet
from random import randint, sample
import string
import pickle
import aiohttp_jinja2
import os
import base64


class ChatRoom(web.View):
    @aiohttp_jinja2.template('chat_room.html')
    async def get(self):
        name = str(self.request.match_info.get("name"))
        slug = str(self.request.match_info.get("slug"))

        db, session = await get_base_needed(self.request)
        try:
            user = session['user']
        except KeyError:
            return web.HTTPFound('/')

        if name and slug:
            if 'flag-password-iteration' in session:
                with open(PRIVATE_KEY_PATH, 'rb') as f:
                    privat_key = pickle.load(f)

                del session['flag-password-iteration']
                messages = await get_message_room(db=db, user=user, slug=slug, privat_key=privat_key)

                return {"slug": slug, 'name': name, 'status': True, "messages": messages}
            else:
                status = await Rooms.check_owner(db=db, username=user, name=name, slug=slug)
                if status:
                    with open(PRIVATE_KEY_PATH, 'rb') as f:
                        privat_key = pickle.load(f)
                    messages = await get_message_room(db=db, user=user, slug=slug, privat_key=privat_key)

                    return {"slug": slug, "name": name, 'status': status, "messages": messages}
                else:
                    token = await generate_token()
                    session['token'] = token
                    return {"slug": slug, "name": name, "status": status, 'token': token}
        else:
            return web.HTTPFound('/')

    async def post(self):
        name = str(self.request.match_info.get("name"))
        slug = str(self.request.match_info.get("slug"))
        db, session = await get_base_needed(self.request)
        data = await self.request.post()
        token, user = session['token'], session['user']
        whom_user = SITE_STORAGE[user]
        status = await check_token(session_token=token, html_token=data['csrf_token'])
        if status:
            password = data['password']
            status = await Rooms.check_password(db=db, username=whom_user, name=name, slug=slug,
                                                password=password)
            if status:
                session['flag-password-iteration'] = 'pull-password'
                del SITE_STORAGE[user]
                location = self.request.app.router['current_room'].url_for(name=name, slug=slug)
                return web.HTTPFound(location=location)
            else:
                return web.HTTPFound(location='/messages')
        else:
            return web.HTTPError()


async def get_message_room(db, user, slug, privat_key):
    messages = await MessagesRoom.get_messages_from_room(db=db, username=user, slug=slug)
    for mess in messages:
        for el in mess:
            if mess[el][0] == 'message':
                new_message = await decrypt_base(mess[el][1], privat_key)
                print(new_message)
                mess[el][1] = new_message.decode('utf-8')

    return messages


class WebSocketRoom(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        db, session = await get_base_needed(self.request)
        redis = self.request.app['db_redis']
        user_name = await User.get_user(db=db, data=session.get('user'))
        if user_name:
            name = self.request.match_info.get("name")
            slug = self.request.match_info.get("slug")
            if name and slug:
                room_id = (name + slug).replace('/', '')
                if room_id not in self.request.app['websockets_room']:
                    self.request.app['websockets_room'][room_id] = {}
                self.request.app['websockets_room'][room_id][user_name] = ws
                room_name = name + '_' + slug
                status = await redis.hgetall(room_name)
                if status == {}:
                    public_key = Fernet.generate_key()
                    await redis.hmset(room_name, 'public_key', public_key)

                    chose = randint(0, 1)
                    chars = ''.join(sample(string.ascii_letters, 10))
                    public_key = public_key.decode('utf-8')

                    if chose == 0:
                        public_key += str(chars) + '@'
                    else:
                        public_key = '@' + str(chars) + public_key

                    for ws_iter in self.request.app['websockets_room'][room_id].values():
                        await ws_iter.send_json({'text': "User connect", "user": user_name, 'info': public_key})
                else:
                    for ws_iter in self.request.app['websockets_room'][room_id].values():
                        await ws_iter.send_json({'text': "User connect", "user": user_name, 'info': status[b'public_key'].decode('utf-8')})
            else:
                return web.HTTPForbidden()
        else:
            print('Error')
            return web.HTTPForbidden()

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = msg.data
                if data == 'close':
                    await ws.close()

                elif len(str(data)) > 1000 and 'data:image' in str(data):
                    """
                        IMAGE
                    """
                    index_photo_name = data.find("data:image")
                    index_base_photo_content = data.find("base64,")
                    if index_photo_name == -1 or index_base_photo_content == -1:
                        continue

                    photo_names = data[:index_photo_name][:-1]
                    enlargement = len(str(photo_names))

                    photo_name = create_file_name() + photo_names[enlargement - 4:]
                    base_photo_content = data[index_base_photo_content + 7:]
                    path = name + slug
                    normal_path = BASE_STATIC_DIR + '\\photos_room\\' + f'{path}'
                    os.mkdir(normal_path)
                    photo_name_url = os.path.join(normal_path + '\\' + photo_name)
                    send_name_photo_url = f'../static/photos_room/{path}/{photo_name}'

                    file = await self.read_file(base_photo_content)

                    with open(photo_name_url, 'wb') as f:
                        f.write(file)

                    status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                             image=send_name_photo_url)
                    if status:
                        await self.send_messages_room(send_name_photo_url, 'image', room_id, user_name)

                elif len(str(data)) > 1000 and 'data:audio' in str(data):
                    """
                        AUDIO 
                    """
                    index_audio_name = data.find('data:audio')
                    index_base_audio_content = data.find("base64,")
                    if index_audio_name == -1 or index_base_audio_content == -1:
                        continue

                    audio_name = create_file_name() + '.mp3'
                    base_audio_content = data[index_base_audio_content + 7:]
                    path = name + slug
                    normal_path = BASE_STATIC_DIR + '\\audio_room\\' + f'{path}'
                    os.mkdir(normal_path)
                    audio_name_url = os.path.join(normal_path + '\\' + audio_name)
                    send_name_audio_url = f'../static/audio_room/{str(path)}/{audio_name}'

                    file = await self.read_file(base_audio_content)

                    with open(audio_name_url, 'wb') as f:
                        f.write(file)

                    status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                             audio=send_name_audio_url)
                    if status:
                        await self.send_messages_room(send_name_audio_url, 'audio', room_id, user_name)

                elif data.strip().startswith('/'):
                    """
                        COMMAND
                    """
                    command_text = await self.commands(data.strip())
                    if command_text is not None:
                        await self.send_messages_room(command_text, 'text', room_id, user_name)
                    else:
                        await self.request.app['websockets'][user_name].send_json({'not_command': 'Not command'})

                elif len(str(data)) > 400 or len(str(data)) == 0 or str(data) == '' or str(data) == ' ':
                    continue

                else:
                    """
                        TEXT
                    """
                    # get key
                    public_key = await redis.hgetall(room_name)
                    public_key = public_key[b'public_key']
                    # main text
                    text = await decrypt_base(data, public_key)
                    text_bd = text
                    text = text.decode('utf-8')
                    # encrypt_text and get private_key
                    with open(PRIVATE_KEY_PATH, 'rb') as f:
                        privat_key = pickle.load(f)

                    cipher = Fernet(privat_key)
                    encrypted_text_bd = cipher.encrypt(text_bd)

                    status = await MessagesRoom.save_message(db=db, username=user_name, slug=slug,
                                                                     message=encrypted_text_bd)
                    if status:
                        await self.send_messages_room(text, 'text', room_id, user_name)

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        del self.request.app['websockets_room'][room_id][user_name]
        if len(self.request.app['websockets_room'][room_id]) == 0:
            return ws
        else:
            for wss in self.request.app['websockets'][room_id].values():
                await wss.send_json({'text': "disconnect", "user": user_name})
            return ws

    async def read_file(self, file):
        return base64.b64decode(file)

    async def commands(self, text):
        if text == '/time':
            return await time_now()
        elif text == '/kurs':
            return await curs_now()
        else:
            return None

    async def send_messages_room(self, message, type_message, room_id, user_name):
        for ws_iter in self.request.app['websockets_room'][room_id].values():
            await ws_iter.send_json({type_message: message, "user": user_name})