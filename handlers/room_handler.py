from aiohttp import web, WSMsgType
from models.database import Rooms, MessagesRoom, User
from tools.get_base import get_base_needed
from tools.csrf_token import generate_token, check_token
from tools.RandomName import create_file_name
from handlers.commands import time_now, curs_now
from config import BASE_STATIC_DIR
import aiohttp_jinja2
import os
import base64


class ChatRoom(web.View):
    @aiohttp_jinja2.template('chat_room.html')
    async def get(self):
        self.name = str(self.request.match_info.get("name"))
        self.slug = str(self.request.match_info.get("slug"))

        self.db, self.session = await get_base_needed(self.request)
        self.user = self.session['user']

        if self.name and self.slug:
            if 'flag-password-iteration' in self.session:
                messages = await MessagesRoom.get_messages_from_room(db=self.db, username=self.user, slug=self.slug)
                del self.session['flag-password-iteration']
                return {"room_name": self.slug, 'status': True, "messages": messages}
            else:
                status = await Rooms.check_owner(db=self.db, username=self.user, name=self.name, slug=self.slug)
                if status:
                    messages = await MessagesRoom.get_messages_from_room(db=self.db, username=self.user, slug=self.slug)
                    return {"slug": self.slug, "name": self.name, 'status': status, "messages": messages}
                else:
                    token = await generate_token()
                    self.session['token'] = token
                    return {"slug": self.slug, "name": self.name, "status": status, 'token': token}
        else:
            print('Шо таке!')
            return web.HTTPFound('/')

    async def post(self):
        data = await self.request.post()
        token = self.session['token']
        status = await check_token(session_token=token, html_token=data['csrf_token'])
        if status:
            password = data['password']
            status = await Rooms.check_password(db=self.db, username=self.user, name=self.name, slug=self.slug,
                                                password=password)
            if status:
                self.session['flag-password-iteration'] = 'pull-password'
                location = self.request.app.router['current_room'].url_for(name=self.name, slug=self.slug)
                return web.HTTPFound(location=location)
        else:
            return web.HTTPError()


class WebSocketRoom(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        db, session = await get_base_needed(self.request)
        self.user_name = await User.get_user(db=db, data=session.get('user'))
        if self.user_name:
            name = self.request.match_info.get("name")
            slug = self.request.match_info.get("slug")
            if name and slug:
                self.room_id = (name + slug).replace('/', '')
                if self.room_id not in self.request.app['websockets_room']:
                    self.request.app['websockets_room'][self.room_id] = {}
                self.request.app['websockets_room'][self.room_id][self.user_name] = ws
                for ws_iter in self.request.app['websockets_room'][self.room_id].values():
                    await ws_iter.send_json({'text': "User connect", "user": self.user_name})
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
                    normal_path = BASE_STATIC_DIR + '\\photos_room\\' + f'\\{path}'
                    os.mkdir(normal_path)
                    photo_name_url = os.path.join(normal_path + '\\' + photo_name)
                    send_name_photo_url = f'static/photos_room/{path}/{photo_name}'

                    file = await self.read_file(base_photo_content)

                    with open(photo_name_url, 'wb') as f:
                        f.write(file)

                    status = await MessagesRoom.save_message(db=db, username=self.user_name, slug=slug,
                                                             image=send_name_photo_url)
                    if status:
                        await self.send_messages_room(send_name_photo_url, 'image')

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
                    normal_path = BASE_STATIC_DIR + '\\audio_room\\' + f'\\{path}'
                    os.mkdir(normal_path)
                    audio_name_url = os.path.join(normal_path + '\\' + audio_name)
                    send_name_audio_url = f'static/audio_room/{str(path)}/{audio_name}'

                    file = await self.read_file(base_audio_content)

                    with open(audio_name_url, 'wb') as f:
                        f.write(file)

                    status = await MessagesRoom.save_message(db=db, username=self.user_name, slug=slug,
                                                             audio=send_name_audio_url)
                    if status:
                        await self.send_messages_room(send_name_audio_url, 'audio')

                elif len(str(data)) > 400 or len(str(data)) == 0 or str(data) == '' or str(data) == ' ':
                    continue
                else:
                    if data.strip().startswith('/'):
                        """
                            COMMAND
                        """
                        command_text = await self.commands(data.strip())
                        if command_text is not None:
                            await self.send_messages_room(command_text, 'text')
                        else:
                            await self.request.app['websockets'][self.user_name].send_json({'not_command': 'Not command'})
                    else:
                        """
                            TEXT
                        """
                        status = await MessagesRoom.save_message(db=db, username=self.user_name, slug=slug,
                                                                 message=str(data.strip()))
                        if status:
                            await self.send_messages_room(data, 'text')

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        print(self.request.app['websockets_room'])
        del self.request.app['websockets_room'][self.room_id][self.user_name]
        for wss in self.request.app['websockets'][self.room_id].values():
            await wss.send_json({'text': "disconnect", "user": self.user_name})
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

    async def send_messages_room(self, message, type_message):
        for ws_iter in self.request.app['websockets_room'][self.room_id].values():
            await ws_iter.send_json({type_message: message, "user": self.user_name})