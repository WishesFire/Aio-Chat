from motor.motor_asyncio import AsyncIOMotorDatabase


class User:

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
    async def delete_all_users(db: AsyncIOMotorDatabase):
        await db.Usercollection.delete_many({})


class Message:

    @staticmethod
    async def save_message(db: AsyncIOMotorDatabase,  user, message=None, image=None):
        if image is not None:
            await db.Aiocollection.insert_one({'user': user, 'image': image})
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

    @staticmethod
    async def get_user_room(db: AsyncIOMotorDatabase, username):
        cursor = db.Roomcollection.find_one({'username': username})
        if cursor:
            return await cursor
        else:
            return None

    @staticmethod
    async def save_room(db: AsyncIOMotorDatabase, username,  room_name, password):
        cursor = await db.Roomcollection.find_one({'username': username})
        if cursor == None:
            new_room = {
                'username': username,
                'rooms': {room_name: password}
            }
            await db.Roomcollection.insert_one(new_room)
            return True
        else:
            if len(cursor['rooms']) < 5:
                await db.Roomcollection.update_one({'username': username}, {'$set': {f'rooms.{room_name}': password}})
                return True
            else:
                return False

    @staticmethod
    async def delete_room(db: AsyncIOMotorDatabase, username, room_name):
        await db.Roomcollection.delete_one({'username': username}, {'$unset': {'rooms': room_name}})

    @staticmethod
    async def delete_all_room(db: AsyncIOMotorDatabase):
        await db.Roomcollection.delete_many({})