from aiohttp import web, WSMsgType
from handlers.room_chat.services_room_chat import audit_room
from handlers.chat.service_websocket_chat import prepare_date_socket, message_manager
from handlers.room_chat.services_websockets_room_chat import generate_key_room
from models.database import Rooms
from tools.get_base import get_base_needed
from tools.csrf_token import check_token
from handlers.commands import time_now, curs_now
from config import SITE_STORAGE
import aiohttp_jinja2


class ChatRoom(web.View):
    @aiohttp_jinja2.template('chat_room.html')
    async def get(self):
        name, slug = await get_name_slug(self.request)
        db, session = await get_base_needed(self.request)
        try:
            user = session['user']
        except KeyError:
            return web.HTTPFound('/')

        if name and slug:
            flag, status, message_token = await audit_room(session, db, user, name, slug)

            if flag == 'first':
                return {"slug": slug, 'name': name, 'status': True, "messages": message_token}
            elif flag == 'second':
                return {"slug": slug, "name": name, 'status': status, "messages": message_token}
            elif flag == 'third':
                return {"slug": slug, "name": name, "status": status, 'token': message_token}

        else:
            return web.HTTPFound('/')

    async def post(self):
        name, slug = await get_name_slug(self.request)
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


async def get_name_slug(request):
    name = str(request.match_info.get("name"))
    slug = str(request.match_info.get("slug"))
    return name, slug


class WebSocketRoom(web.View):
    async def get(self):
        redis, user_name, ws, db = await prepare_date_socket(request=self.request)

        if user_name:
            name, slug = await get_name_slug(self.request)

            if name and slug:
                room_id = (name + slug).replace('/', '')
                if room_id not in self.request.app['websockets_room']:
                    self.request.app['websockets_room'][room_id] = {}
                self.request.app['websockets_room'][room_id][user_name] = ws
                room_name = name + '_' + slug
                status = await redis.hgetall(room_name)

                if status == {}:
                    public_key = await generate_key_room(redis, room_name)

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
                    manager_flag, send_name_photo_url, _ = await message_manager(
                                                            'image', 'room', data, user_name,
                                                            redis, db, name, slug, None)
                    if not manager_flag:
                        continue
                    else:
                        await self.send_messages_room(send_name_photo_url, 'image', room_id, user_name)

                elif len(str(data)) > 1000 and 'data:audio' in str(data):
                    """
                        AUDIO 
                    """
                    manager_flag, send_name_audio_url, _ = await message_manager(
                                                        'audio', 'room', data, user_name, redis, db, name, slug, None)

                    if not manager_flag:
                        continue
                    else:
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
                    status, text = await message_manager('message', 'room', data, user_name,
                                                         redis, db, name, slug, room_name)

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