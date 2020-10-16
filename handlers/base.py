from aiohttp import web
from aiohttp_session import get_session
from RandomName import create_username
from models.database import User
import aiohttp_jinja2
import datetime


@aiohttp_jinja2.template('index.html')
async def index(request):
    if request.get:
        db = request.app['db']
        session = await get_session(request)
        if 'user' in session:
            print('Юзер в сесіії')
            user = session['user']
        else:
            print('Строверння юзера')
            user = create_username()
            #await User.create_user(db=db, data=user)
            session['user'] = user

        session['last_visit'] = str(datetime.datetime.now())
        last_visit = session['last_visit']

        return dict(text=f'Last Visit = {last_visit}', user=user)

    elif request.post:
        data = await request.post()
        send_mess = data['input-chat']
        session = await get_session(request)
        session['send_message'] = {'send': send_mess}
        return dict(session['send_message'])


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)