from aiohttp import web
import base64
import logging
import aiohttp_jinja2
from jinja2 import FileSystemLoader
from cryptography import fernet
from handlers.base import Chat, WebSocket, Rules, CreateRoom, Messages
from handlers.room_handler import ChatRoom, WebSocketRoom
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from motor.motor_asyncio import AsyncIOMotorClient
from clear_chat import clear_chat
from antispam.bot import antispam_bot
from config import SECRET_KEY_RECAPTCHA, SECRET_SITE_RECAPTCHA, BASE_DIR, MONGO_HOST, SECRET_KEY, PASSWORD_REDIS
from config import generate_key
import ssl
import aioredis


def main():
    app = web.Application()
    app['websockets'] = {}
    app['websockets_room'] = {}
    app['config'] = SECRET_KEY
    client = AsyncIOMotorClient(MONGO_HOST)
    app['db'] = client['AioDB']
    app.on_startup.append(start_back_tasks)
    app.on_startup.append(start_back_tasks_key)
    app.on_shutdown.append(stop_back_tasks)
    app.on_shutdown.append(shutdown)

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_jinja2.setup(app, loader=FileSystemLoader(BASE_DIR))
    setup(app, EncryptedCookieStorage(secret_key))

    app.router.add_route('*', '/', Chat, name='main')
    app.router.add_route('GET', '/ws', WebSocket, name='sockets')
    app.router.add_route('GET', '/ws/{name}/{slug}', WebSocketRoom, name='room_sockets')
    app.router.add_route('GET', '/rules', Rules, name='rules')
    app.router.add_route('*', '/rooms', CreateRoom, name='rooms')
    app.router.add_route('*', r'/{name}/{slug}', ChatRoom, name='current_room')
    app.router.add_route('*', '/messages', Messages, name='messages')
    app.router.add_static('/static', 'static', name='static')

    logging.basicConfig(level=logging.DEBUG)
    #sll_certificate = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #sll_certificate.load_cert_chain('domain_srv.crt', 'domain_srv.key')

    web.run_app(app)


async def start_back_tasks(app):
    app['db_redis'] = await aioredis.create_redis_pool('redis://localhost')
    app['clear_day'] = app.loop.create_task(clear_chat(app['db'], app['db_redis']))
    app['aio_bot'] = app.loop.create_task(antispam_bot())


async def start_back_tasks_key(app):
    app['create_key'] = app.loop.create_task(generate_key())


async def stop_back_tasks(app):
    app['clear_day'].cancel()
    await app['clear_day']
    app['create_key'].cancel()
    await app['create_key']


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    for ws in app['websockets_room'].values():
        await ws.close()
    app['websockets'].clear()
    app['websockets_room'].clear()
    await app['db_redis'].close()
    await app['db_redis'].wait_closed()

if __name__ == '__main__':
    main()