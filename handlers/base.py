from aiohttp import web, WSMsgType
from aiohttp_session import get_session
from RandomName import create_username
from models.database import User, Message
from handlers.commands import time_now
import aiohttp_jinja2

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


class CreateRoom(web.View):
    pass


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
                if msg.data == 'close':
                    await ws.close()
                elif len(str(msg.data)) > 400 or str(msg.data) == ('' or ' '):
                    continue
                else:
                    if msg.data.strip().startswith('/'):
                        command_text = await self.commands(msg.data.strip())
                        if command_text is not None:
                            for wss in self.request.app['websockets'].values():
                                await wss.send_json({'text': command_text, 'user': user_name})
                    else:
                        db = self.request.app['db']
                        status = await Message.save_message(db=db, user=user_name, message=str(msg.data.strip()))
                        if status:
                            for wss in self.request.app['websockets'].values():
                                await wss.send_json({'text': msg.data, 'user': user_name})

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        del self.request.app['websockets'][user_name]
        return ws

    async def commands(self, text):
        if text == '/time':
            return await time_now()
        else:
            return None