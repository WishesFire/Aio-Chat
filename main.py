from aiohttp import web
import base64
import logging
import aiohttp_jinja2
from jinja2 import FileSystemLoader
from cryptography import fernet
from handlers.base import Chat, WebSocket, Rules, CreateRoom, Messages
from handlers.room_handler import ChatRoom
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from motor.motor_asyncio import AsyncIOMotorClient
from clear_chat import clear_chat
from config import SECRET_KEY_RECAPTCHA, SECRET_SITE_RECAPTCHA, BASE_DIR, MONGO_HOST, SECRET_KEY
import ssl


def main():
    app = web.Application()
    app['websockets'] = {}
    app['config'] = SECRET_KEY
    client = AsyncIOMotorClient(MONGO_HOST)
    app['db'] = client['AioDB']
    app.on_startup.append(start_back_tasks)
    app.on_shutdown.append(stop_back_tasks)
    app.on_shutdown.append(shutdown)

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_jinja2.setup(app, loader=FileSystemLoader(BASE_DIR))
    setup(app, EncryptedCookieStorage(secret_key))

    app.router.add_route('GET', '/', Chat, name='main')
    app.router.add_route('GET', '/ws', WebSocket, name='sockets')
    app.router.add_route('GET', '/ws/{name}/{slug}', WebSocket, name='room_sockets')
    app.router.add_route('GET', '/rules', Rules, name='rules')
    app.router.add_route('*', '/rooms', CreateRoom, name='rooms')
    app.router.add_route('GET', r'/{name}/{slug}', ChatRoom, name='current_room')
    app.router.add_route('GET', '/messages', Messages, name='messages')
    app.router.add_static('/static', 'static', name='static')

    logging.basicConfig(level=logging.DEBUG)
    #sll_certificate = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #sll_certificate.load_cert_chain('domain_srv.crt', 'domain_srv.key')

    web.run_app(app)


async def start_back_tasks(app):
    app['clear_day'] = app.loop.create_task(clear_chat(app['db']))


async def stop_back_tasks(app):
    app['clear_day'].cancel()
    await app['clear_day']


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


if __name__ == '__main__':
    main()