from aiohttp import web, WSMsgType
from aiohttp_session import get_session
from RandomName import create_username, create_file_name
from models.database import User, Message, Rooms
from handlers.commands import time_now, curs_now
from config import BASE_STATIC_DIR
import aiohttp_jinja2
import base64
import os

text_for_rules_ru = "Приветствую в аннонимном чате, чуствуй себя в безопасности " \
                         "1. Чат не несет ответственность за контент который в нем есть"
text_for_rules_en = " Greetings to the anonymous chat, feel safe" \
                    " 1. Chat is not responsible for the content it contains."


class Chat(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        db = self.request.app['db']
        session = await get_session(self.request)
        if 'user' in session:
            print('Юзер в сесіії')
            user = session['user']
        else:
            print('Строверння юзера')
            user = create_username()
            await User.create_user(db=db, data=user)
            session['user'] = user
        messages = await Message.get_all_message_users(db=db)

        return {'user': user, 'messages': messages}


class Rules(web.View):
    @aiohttp_jinja2.template('rules.html')
    async def get(self):
        session = await get_session(self.request)
        if 'flag-icon' not in session:
            session['flag-icon'] = 0

        if session['flag-icon'] == 0:
            session['flag-icon'] = 1
            return {'text': text_for_rules_ru, 'icon': '../static/img/american.png'}
        elif session['flag-icon'] == 1:
            session['flag-icon'] = 0
            return {'text': text_for_rules_en, 'icon': '../static/img/russian.png'}


class Messages(web.View):
    pass


class CreateRoom(web.View):
    @aiohttp_jinja2.template('rooms.html')
    async def get(self):
        session = await get_session(self.request)
        db = self.request.app['db']
        user = session['user']
        names_of_rooms = await Rooms.get_user_room(db=db, username=user)
        if names_of_rooms is None:
            return {'user': user, 'rooms': ''}
        else:
            return {'user': user, 'rooms': names_of_rooms['rooms']}

    async def post(self):
        data = await self.request.post()
        session = await get_session(self.request)
        db = self.request.app['db']
        user = session['user']
        print(data)
        print(data['name-room'])
        if data['name-room'] and data['password']:
            room_name = data['name-room']
            room_password = data['password']
            status = await Rooms.save_room(db=db, username=user, room_name=room_name, password=room_password)
            if status:
                url = self.request.app.router['rooms'].url_for()
                return web.HTTPFound(location=url)
            else:
                return web.HTTPForbidden()
        elif data['text']:
            room_name = data['text']
            await Rooms.delete_room(db=db, username=user, room_name=room_name)


class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        session = await get_session(self.request)
        db = self.request.app['db']
        user_name = await User.get_user(db=db, data=session.get('user'))
        if user_name:
            count_connection = len(self.request.app['websockets'])
            self.request.app['websockets'][user_name] = ws
            for wss in self.request.app['websockets'].values():
                await wss.send_json({'connection': count_connection + 1})
        else:
            print('Error')
            return web.HTTPForbidden()

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = msg.data
                if data == 'close':
                    await ws.close()
                elif len(str(data)) > 1000 and 'data:image' in str(data):
                    index_photo_name = data.find("data:image")
                    index_base_photo_content = data.find("base64,")
                    if index_photo_name == -1 or index_base_photo_content == -1:
                        continue

                    photo_names = data[:index_photo_name][:-1]
                    enlargement = len(str(photo_names))

                    photo_name = create_file_name() + photo_names[enlargement-4:]
                    base_photo_content = data[index_base_photo_content + 7:]
                    photo_name_url = os.path.join(BASE_STATIC_DIR + '\\photos\\' + photo_name)
                    send_name_url = f'static/photos/{photo_name}'

                    file = base64.b64decode(base_photo_content)

                    with open(photo_name_url, 'wb') as f:
                        f.write(file)

                    status = await Message.save_message(db=db, user=user_name, image=send_name_url)
                    if status:
                        for wss in self.request.app['websockets'].values():
                            await wss.send_json({'image': send_name_url, 'user': user_name})

                elif len(str(data)) > 400 or len(str(data)) == 0 or str(data) == '' or str(data) == ' ':
                    continue
                else:
                    if data.strip().startswith('/'):
                        command_text = await self.commands(data.strip())
                        if command_text is not None:
                            for wss in self.request.app['websockets'].values():
                                await wss.send_json({'text': command_text, 'user': user_name})
                        else:
                            await self.request.app['websockets'][user_name].send_json({'not_command': 'Not command'})
                    else:
                        db = self.request.app['db']
                        status = await Message.save_message(db=db, user=user_name, message=str(data.strip()))
                        if status:
                            for wss in self.request.app['websockets'].values():
                                await wss.send_json({'text': data, 'user': user_name})

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        del self.request.app['websockets'][user_name]
        count_connection = len(self.request.app['websockets'])
        for wss in self.request.app['websockets'].values():
            await wss.send_json({'disconnect': count_connection})
        return ws

    async def commands(self, text):
        if text == '/time':
            return await time_now()
        elif text == '/kurs':
            return await curs_now()
        else:
            return None