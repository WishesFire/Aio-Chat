from motor.motor_asyncio import AsyncIOMotorDatabase


class User:
    """
    A model for a user who visits the site.
    """
    @staticmethod
    async def get_user(db: AsyncIOMotorDatabase, data):
        user = await db.Usercollection.find_one({'username': data})
        if user:
            return user['username']
        else:
            return False

    @staticmethod
    async def create_user(db: AsyncIOMotorDatabase, data):
        await db.Usercollection.insert_one({'username': str(data)})
        return {'status': 200}

    @staticmethod
    async def get_all_user(db: AsyncIOMotorDatabase):
        return await db.Usercollection.find()

    @staticmethod
    async def delete_all_users(db: AsyncIOMotorDatabase):
        await db.Usercollection.delete_many({})


class Message:
    """
    A model for saving messages from general chat
    """
    @staticmethod
    async def save_message(db: AsyncIOMotorDatabase,  user, message=None, image=None, audio=None):
        if image is not None:
            await db.Aiocollection.insert_one({'user': user, 'image': image})
        elif audio is not None:
            await db.Aiocollection.insert_one({'user': user, 'audio': audio})
        else:
            if message is not None:
                await db.Aiocollection.insert_one({'user': user, 'message': message})
            else:
                return False
        return True

    @staticmethod
    async def get_all_message_users(db: AsyncIOMotorDatabase):
        cursor = db.Aiocollection.find().to_list(length=None)
        return await cursor

    @staticmethod
    async def delete_all_messages(db: AsyncIOMotorDatabase):
        await db.Aiocollection.delete_many({})


class Rooms:
    """
    A model for saving, deleting rooms
    """
    @staticmethod
    async def get_user_room(db: AsyncIOMotorDatabase, username):
        cursor = db.Roomcollection.find_one({'username': username})
        if cursor:
            return await cursor
        else:
            return None

    @staticmethod
    async def find_room(db: AsyncIOMotorDatabase, username, room_name):
        cursor = await db.Roomcollection.find_one({'username': username})
        if room_name in cursor['rooms']:
            return True
        else:
            return False

    @staticmethod
    async def check_owner(db: AsyncIOMotorDatabase, username, name, slug):
        cursor = await db.Roomcollection.find_one({'username': username})
        if cursor is not None:
            for room in cursor['rooms']:
                if name == cursor['rooms'][room][1] and slug == cursor['rooms'][room][2]:
                    return True
            return False
        else:
            return False

    @staticmethod
    async def check_password(db: AsyncIOMotorDatabase, username, password, name, slug):
        cursor = await db.Roomcollection.find_one({'username': username})
        for room in cursor['rooms']:
            if name == cursor['rooms'][room][1] and slug == cursor['rooms'][room][2]:
                if password == cursor['rooms'][room][0]:
                    return True
                else:
                    return False
            else:
                return False

    @staticmethod
    async def save_room(db: AsyncIOMotorDatabase, username,  room_name, password, name, slug):
        cursor = await db.Roomcollection.find_one({'username': username})
        if cursor == None:
            new_room = {
                'username': username,
                'rooms': {room_name: [password, name, slug]}
            }
            await db.Roomcollection.insert_one(new_room)
            return True
        else:
            if len(cursor['rooms']) < 5:
                if room_name in cursor['rooms']:
                    return False
                else:
                    await db.Roomcollection.update_one({'username': username}, {'$set': {f'rooms.{room_name}':
                                                                                             [password, name, slug]}})
                return True
            else:
                return False

    @staticmethod
    async def delete_room(db: AsyncIOMotorDatabase, username, room_name):
        p = await db.Roomcollection.find_one({'username': username})
        password = p['rooms'][room_name][0]
        name = p['rooms'][room_name][1]
        slug = p['rooms'][room_name][2]
        await db.Roomcollection.update_one({'username': username}, {'$unset': {f'rooms.{room_name}':
                                                                                   [password, name, slug]}})

    @staticmethod
    async def delete_all_room(db: AsyncIOMotorDatabase):
        await db.Roomcollection.delete_many({})


class MessagesRoom:
    """
        Messages from specific room
    """
    @staticmethod
    async def get_messages_from_room(db: AsyncIOMotorDatabase, username, slug):
        cursor = await db.MessagesRoomcollection.find_one({'username': username, 'slug': slug})
        if cursor is None:
            new_message_box = {
                'username': username,
                'slug': slug,
                'messages': []
            }
            await db.MessagesRoomcollection.insert_one(new_message_box)
            return ''
        else:
            return cursor['messages']

    @staticmethod
    async def save_message(db: AsyncIOMotorDatabase, username, slug, message=None, image=None, audio=None):
        if image is not None:
            await db.MessagesRoomcollection.update_one({'username': username, 'slug': slug},
                                               {'$push': {'messages': {username: ["image", image]}}})
        elif audio is not None:
            await db.MessagesRoomcollection.update_one({'username': username, 'slug': slug},
                                               {'$push': {'messages': {username: ["audio", audio]}}})
        elif message is not None:
            await db.MessagesRoomcollection.update_one({'username': username, 'slug': slug},
                                                   {'$push': {'messages': {username: ["message", message]}}})
        else:
            return False
        return True

    @staticmethod
    async def delete_all_message_room(db: AsyncIOMotorDatabase):
        await db.MessagesRoomcollection.delete_many({})


class BanUsers:
    """
        Ban users list
    """
    @staticmethod
    async def add_one(db: AsyncIOMotorDatabase, username, status):
        await db.Usercollection.insert_one({'username': username, 'status': status})
        return True

    @staticmethod
    async def get_all(db: AsyncIOMotorDatabase):
        pass