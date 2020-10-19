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


class Message:

    @staticmethod
    async def save_message(db: AsyncIOMotorDatabase,  user, message: str):
        await db.Aiocollection.insert_one({'user': user, 'message': message})
        return True

    @staticmethod
    async def get_all_message_users(db: AsyncIOMotorDatabase):
        cursor = db.Aiocollection.find().to_list(length=None)
        return await cursor