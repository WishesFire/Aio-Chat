from aiohttp import web
import base64
import logging
import os
import aiohttp_jinja2
from jinja2 import FileSystemLoader
from cryptography import fernet
from handlers.base import index
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

BASE_DIR = f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/templates'

def main():
    app = web.Application()
    app['websocket'] = {}
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    aiohttp_jinja2.setup(app, loader=FileSystemLoader(BASE_DIR))
    setup(app, EncryptedCookieStorage(secret_key))

    app.add_routes([web.route('*', '/', index, name='root')])
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)


if __name__ == '__main__':
    main()