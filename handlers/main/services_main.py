from aiohttp import web
from random import randint
from tools.create_slug import create_slug
from aioredis_getting import redis_convert


async def invite_room(whom_to_send, whom_to_room, redis, user):
    if not whom_to_send or not whom_to_room:
        return web.HTTPError()

    user_ver_slug = await create_slug(user)
    whom_to_room_ver_slug = await create_slug(whom_to_room)

    lst_invite = await redis.hgetall(whom_to_send, encoding='utf-8')
    if lst_invite == {}:
        user = user + '.---.' + str(user_ver_slug)
        whom_to_room = whom_to_room + '.---.' + str(whom_to_room_ver_slug)
        await redis.hmset(whom_to_send, user, whom_to_room)
    else:
        user = user + '.---.' + str(user_ver_slug) + f'___-%-_{str(randint(10, 99))}'
        whom_to_room = whom_to_room + '.---.' + str(whom_to_room_ver_slug)
        await redis.hmset(whom_to_send, user, whom_to_room)


async def invite_message_redis(redis, user, ):
    lst_invite = await redis.hgetall(user, encoding='utf-8')
    lst_invite = await redis_convert(lst_invite)

    return lst_invite
