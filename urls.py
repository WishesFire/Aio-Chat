from handlers.main.base import Chat, WebSocket, Rules, CreateRoom, Messages
from handlers.room_chat.room_handler import ChatRoom, WebSocketRoom
from handlers.interlocutor_handler import Companion


routes = [
    ('*', '/', Chat, 'main'),
    ('GET', '/ws', WebSocket, 'sockets'),
    ('GET', '/ws/{name}/{slug}', WebSocketRoom, 'room_sockets'),
    ('GET', '/rules', Rules, 'rules'),
    ('*', '/rooms', CreateRoom, 'rooms'),
    ('*', r'/{name}/{slug}', ChatRoom, 'current_room'),
    ('*', '/messages', Messages, 'messages'),
    ('*', '/companion', Companion, 'companion'),
]