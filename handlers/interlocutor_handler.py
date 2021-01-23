from aiohttp import web
from tools.RandomName import create_file_name
import numpy as np
from aiohttp_session import get_session
import aiohttp_jinja2
import asyncio

QUEUE_STORAGE = np.array([])


class Companion(web.View):
    @aiohttp_jinja2.template('companion.html')
    async def get(self):
        username = await get_username(self.request)
        return {'user': username}

    async def post(self):
        global QUEUE_STORAGE
        username = await get_username(self.request)
        data = await self.request.post()
        if data['status'] == 'go':
            if username not in QUEUE_STORAGE:
                QUEUE_STORAGE = np.append(QUEUE_STORAGE, username)

        elif data['status'] == 'leave':
            index = np.where(QUEUE_STORAGE == username)
            QUEUE_STORAGE = np.delete(QUEUE_STORAGE, index)
            return

        while True:
            count = len(QUEUE_STORAGE)
            index = np.where(QUEUE_STORAGE == username)
            if index < count:
                name, slug = await create_room()
                location = self.request.app.router['room_sockets'].url_for(name=name, slug=slug)
                return web.HTTPFound(location=location)
            else:
                await asyncio.sleep(5)


async def get_username(request):
    session = await get_session(request)
    return session['user']


async def create_room():
    name = await create_file_name()
    slug = await create_file_name()
    return name, slug
