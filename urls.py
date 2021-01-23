from handlers.base import Chat, WebSocket, Rules, CreateRoom, Messages
from handlers.room_handler import ChatRoom, WebSocketRoom
from handlers.interlocutor_handler import Companion


def build_urls(app):
    app.router.add_route('*', '/', Chat, name='main')
    app.router.add_route('GET', '/ws', WebSocket, name='sockets')
    app.router.add_route('GET', '/ws/{name}/{slug}', WebSocketRoom, name='room_sockets')
    app.router.add_route('GET', '/rules', Rules, name='rules')
    app.router.add_route('*', '/rooms', CreateRoom, name='rooms')
    app.router.add_route('*', r'/{name}/{slug}', ChatRoom, name='current_room')
    app.router.add_route('*', '/messages', Messages, name='messages')
    app.router.add_route('*', '/companion', Companion, name='companion')
    app.router.add_static('/static', 'static', name='static')