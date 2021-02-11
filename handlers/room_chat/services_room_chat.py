from tools.csrf_token import generate_token
from tools.dh_key import decrypt_base
from models.database import Rooms, MessagesRoom, User
from config import PRIVATE_KEY_PATH
import pickle


async def audit_room(session, db, user, name, slug):
    if 'flag-password-iteration' in session:
        with open(PRIVATE_KEY_PATH, 'rb') as f:
            privat_key = pickle.load(f)

        del session['flag-password-iteration']
        messages = await get_message_room(db=db, user=user, slug=slug, privat_key=privat_key)

        return 'first', True, messages

    else:
        status = await Rooms.check_owner(db=db, username=user, name=name, slug=slug)
        if status:
            with open(PRIVATE_KEY_PATH, 'rb') as f:
                privat_key = pickle.load(f)
            messages = await get_message_room(db=db, user=user, slug=slug, privat_key=privat_key)
            return 'second', status, messages

        else:
            token = await generate_token()
            session['token'] = token
            return 'third', status, token


async def get_message_room(db, user, slug, privat_key):
    messages = await MessagesRoom.get_messages_from_room(db=db, username=user, slug=slug)
    for mess in messages:
        for el in mess:
            if mess[el][0] == 'message':
                new_message = await decrypt_base(mess[el][1], privat_key)
                print(new_message)
                mess[el][1] = new_message.decode('utf-8')

    return messages


