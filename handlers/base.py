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
        messages = await Message.get_all_message(db=db)

        return {'user': user, 'messages': messages}

    #async def post(self):
        #print('dgadgfadg')
        #data = await self.request.post()
        #session = await get_session(self.request)
        #if 'user' in session and data['chat-text']:
            #send_mess = data['chat-text']
            #session['send_message'] = {'send': send_mess}
            #return dict(session['send_message'])
        #else:
            #return web.HTTPForbidden()


class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        session = await get_session(self.request)
        db = self.request.app['db']
        user_name = await User.get_user(db=db, data=session.get('user'))
        self.request.app['websockets'][user_name] = ws

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    db = self.request.app['db']
                    status = await Message.save_message(db=db, user=user_name, message=str(msg.data.strip()))
                    if status:
                        await ws.send_json({'text': msg.data, 'user': user_name})
            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                break

        del self.request.app['websockets'][user_name]
        return ws