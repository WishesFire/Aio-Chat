from tools.csrf_token import generate_token
from handlers.chat.services_room_chat import room_check_data
from handlers.chat.service_websocket_chat import prepare_date_socket, message_manager
from tools.get_base import get_base_needed
from handlers.commands import time_now, curs_now
from models.database import Rooms
from aiohttp import web, WSMsgType
import aiohttp_jinja2


class CreateRoom(web.View):
    @aiohttp_jinja2.template('rooms.html')
    async def get(self):
        db, session = await get_base_needed(self.request)
        token = await generate_token()
        session['token'] = token
        user = session['user']
        names_of_rooms = await Rooms.get_user_room(db=db, username=user)
        if names_of_rooms is None:
            return {'user': user, 'rooms': '', 'token': token}
        else:
            return {'user': user, 'rooms': names_of_rooms['rooms'], 'token': token}

    async def post(self):
        try:
            data = await self.request.post()
            db, session = await get_base_needed(self.request)
            user = session['user']
            await room_check_data(data, db, user, session, self.request)
        except RuntimeError:
            raise ValueError


class WebSocket(web.View):
    async def get(self):
        self.redis, user_name, ws, db = await prepare_date_socket(request=self.request)

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
                    """
                        IMAGE
                    """
                    manager_flag, send_name_photo_url, ls = await message_manager(
                                                            'image', None, data, user_name,
                                                            self.redis, db, None, None, None)
                    if not manager_flag:
                        continue
                    else:
                        for wss in self.request.app['websockets'].values():
                            await wss.send_json({'image': send_name_photo_url, 'user': user_name, 'name_rooms': ls})

                elif len(str(data)) > 1000 and 'data:audio' in str(data):
                    """
                        AUDIO 
                    """
                    manager_flag, send_name_audio_url, ls = await message_manager(
                        'image', None, data, user_name, self.redis, db, None, None, None)

                    if not manager_flag:
                        continue
                    else:
                        for wss in self.request.app['websockets'].values():
                            await wss.send_json({'audio': send_name_audio_url, 'user': user_name, 'name_rooms': ls})

                elif len(str(data)) > 400 or len(str(data)) == 0 or str(data) == '' or str(data) == ' ':
                    continue
                else:
                    if data.strip().startswith('/'):
                        """
                            COMMAND
                        """
                        command_text = await self.commands(data.strip())
                        if command_text is not None:
                            for wss in self.request.app['websockets'].values():
                                await wss.send_json({'text': command_text, 'user': user_name})
                        else:
                            await self.request.app['websockets'][user_name].send_json({'not_command': 'Not command'})
                    else:
                        """
                            TEXT
                        """
                        _, _, ls = await message_manager('message', None, data, user_name,
                                                         self.redis, db, None, None, None)

                        for wss in self.request.app['websockets'].values():
                            await wss.send_json({'text': data, 'user': user_name, 'name_rooms': ls})

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        del self.request.app['websockets'][user_name]
        count_connection = len(self.request.app['websockets'])
        if count_connection == 0:
            return ws
        else:
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
