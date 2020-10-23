from aiohttp import web, WSMsgType
from aiohttp_session import get_session
from RandomName import create_username
from models.database import User, Message
import aiohttp_jinja2


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
        pass


class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        session = await get_session(self.request)
        db = self.request.app['db']
        user_name = await User.get_user(db=db, data=session.get('user'))
        if user_name:
            self.request.app['websockets'][user_name] = ws
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