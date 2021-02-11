from tools.create_slug import create_slug
from tools.csrf_token import check_token
from models.database import Rooms
from aiohttp import web


async def room_check_data(data, db, user, session, request):
    if data['name-room'] and data['password']:
        room_name = data['name-room']
        name = await create_slug(user)
        slug = await create_slug(room_name)
        await auditing(data, db, user, room_name, name, slug, request, session)
    else:
        return web.HTTPForbidden()


async def auditing(data, db, user, room_name, name, slug, request, session):
    if data['password'] == '#':
        try:
            await Rooms.delete_room(db=db, username=user, room_name=room_name)
            return {}
        except RuntimeError:
            raise ValueError('Error with password')
    elif data['password'] == '1':
        status = await Rooms.find_room(db=db, username=user, room_name=room_name)
        if not status:
            return web.HTTPForbidden()
        return {}
    else:
        token = session['token']
        status = await check_token(session_token=token, html_token=data['csrf_token'])
        if status:
            room_password = data['password']
            status = await Rooms.save_room(db=db, username=user, room_name=room_name, password=room_password,
                                           name=name, slug=slug)
            if status:
                url = request.app.router['rooms'].url_for()
                return web.HTTPFound(location=url)
            else:
                return web.HTTPForbidden()
        else:
            return web.HTTPForbidden()