from aiohttp import web
from handlers.chat_rules import text_for_rules_en, text_for_rules_ru
from handlers.main.services_main import invite_room, invite_message_redis
from aiohttp_session import get_session
from tools.RandomName import create_username
from tools.get_base import get_base_needed
from models.database import User, Message, Rooms
from config import SITE_STORAGE
import aiohttp_jinja2


class Chat(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        db, session = await get_base_needed(self.request)
        messages = await Message.get_all_message_users(db=db)
        if 'user' in session:
            user = session['user']
            name_rooms = await Rooms.get_user_room(db=db, username=user)
            if name_rooms is not None:
                return {'user': user, 'messages': messages, 'name_rooms': name_rooms['rooms']}
            else:
                return {'user': user, 'messages': messages, 'name_rooms': ''}
        else:
            user = await create_username()
            await User.create_user(db=db, data=user)
            session['user'] = user
            return {'user': user, 'messages': messages}

    async def post(self):
        session, user, redis = await messages_handler_needed(self.request)
        data = await self.request.post()

        whom_to_send = data['whom_to_send']
        whom_to_room = data['room_name']

        await invite_room(whom_to_send, whom_to_room, redis, user)


class Rules(web.View):
    @aiohttp_jinja2.template('rules.html')
    async def get(self):
        session = await get_session(self.request)
        if 'flag-icon' not in session:
            session['flag-icon'] = 0

        if session['flag-icon'] == 0:
            session['flag-icon'] = 1
            return {'text': text_for_rules_ru, 'icon': '../static/img/american.png'}
        elif session['flag-icon'] == 1:
            session['flag-icon'] = 0
            return {'text': text_for_rules_en, 'icon': '../static/img/russian.png'}


class Messages(web.View):
    @aiohttp_jinja2.template('messages.html')
    async def get(self):
        session, user, redis = await messages_handler_needed(self.request)
        lst_invite = await invite_message_redis(redis, user)

        return {'lst_invite': lst_invite}

    async def post(self):
        session, user, redis = await messages_handler_needed(self.request)
        data = await self.request.post()
        whom_to_send = data['whom_to_send']

        if whom_to_send == '1-1':
            await redis.delete(user)
        else:
            SITE_STORAGE[user] = whom_to_send
            await redis.hdel(user, whom_to_send)
        return {'status': 200}


async def messages_handler_needed(request):
    _, session = await get_base_needed(request)
    user = session['user']
    redis = request.app['db_redis']
    return session, user, redis
