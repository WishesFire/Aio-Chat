from aiohttp import web
from models.database import MessagesRoom
import aiohttp_jinja2


class ChatRoom(web.View):
    @aiohttp_jinja2.template('chat_room.html')
    async def get(self):
        """ ПРОВЕРКА НА ВЛАСНИКА, ЯКЩО ВЛАСНИК ТО НЕ ТРЕБА ПИСАТИ ПАРОЛЬ, ЯКЩО НІ ТО ПИШЕШ ПАРОЛЬ
        ВИВОДИТИ ВСІ ПОВІДОМЛЕННЯ І ЮЗЕРІВ"""
        name = self.request.match_info.get("slug", "Anonymous")
        print(name)
        #messages = await MessagesRoom.get_messages_from_room()
        return {"room_name": name}

    async def post(self):
        pass