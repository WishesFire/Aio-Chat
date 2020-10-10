from aiohttp import web
from aiohttp_session import get_session

async def index(request):
    if request.get:
        session = await get_session(request)
        return web.Response(text='Hello in my Chat!')


async def send_message(request):
    data = await request.post()
    send_mes = data['input-chat']


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)