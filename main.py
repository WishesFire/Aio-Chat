from aiohttp import web
from jinja2 import FileSystemLoader
from cryptography import fernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from motor.motor_asyncio import AsyncIOMotorClient
from clear_chat import clear_chat
from urls import build_urls
from antispam.bot import antispam_bot
from antispam import antisexs
from config import SECRET_KEY_RECAPTCHA, SECRET_SITE_RECAPTCHA, BASE_DIR, MONGO_HOST, SECRET_KEY, PASSWORD_REDIS
from config import generate_key
import ssl
import aioredis
import base64
import logging
import aiohttp_jinja2


def main():
    app = web.Application()
    app['websockets'] = {}
    app['websockets_room'] = {}
    app['websockets_queue'] = {}
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

    build_urls(app=app)

    logging.basicConfig(level=logging.DEBUG)
    #sll_certificate = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #sll_certificate.load_cert_chain('domain_srv.crt', 'domain_srv.key')

    web.run_app(app)


async def start_back_tasks(app):
    app['db_redis'] = await aioredis.create_redis_pool('redis://localhost')
    app['clear_day'] = app.loop.create_task(clear_chat(app['db'], app['db_redis']))
    app['check_photo'] = app.loop.create_task(antisexs.sex_message_check(app['db_redis'], app['db']))
    #app['aio_bot'] = app.loop.create_task(antispam_bot(app['db']))


async def start_back_tasks_key(app):
    app['create_key'] = app.loop.create_task(generate_key())


async def stop_back_tasks(app):
    app['clear_day'].cancel()
    await app['clear_day']
    app['create_key'].cancel()
    await app['create_key']
    #app['aio_bot'].cancel()
    #await app['aio_bot']
    app['check_photo'].cancel()
    await app['check_photo']


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