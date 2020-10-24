from aiohttp import web
import base64
import logging
import os
import aiohttp_jinja2
from jinja2 import FileSystemLoader
from cryptography import fernet
from handlers.base import Chat, WebSocket, Rules
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

BASE_DIR = f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/templates'
MONGO_HOST = '*'
SECRET_KEY = '68028350928350928502899'

def main():
    app = web.Application()
    app['websockets'] = {}
    app['config'] = SECRET_KEY
    client = AsyncIOMotorClient(MONGO_HOST)
    app['db'] = client['AioDB']
    app.on_shutdown.append(shutdown)

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_jinja2.setup(app, loader=FileSystemLoader(BASE_DIR))
    setup(app, EncryptedCookieStorage(secret_key))

    app.router.add_route('GET', '/', Chat, name='main')
    app.router.add_route('GET', '/ws', WebSocket, name='sockets')
    app.router.add_route('GET', '/rules', Rules, name='rules')
    app.router.add_static('/static', 'static', name='static')

    logging.basicConfig(level=logging.DEBUG)
    #sll_certificate = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #sll_certificate.load_cert_chain('domain_srv.crt', 'domain_srv.key')

    web.run_app(app)


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


if __name__ == '__main__':
    main()