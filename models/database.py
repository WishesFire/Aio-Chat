from motor.motor_asyncio import AsyncIOMotorDatabase


class User:

    @staticmethod
    async def check_user(db: AsyncIOMotorDatabase, data):
        user = await db.Usercollection.find_one({'username': data['username']})
        if user:
            return dict()

    @staticmethod
    async def create_user(db: AsyncIOMotorDatabase, data):
        await db.Usercollection.insert_one({'username': data})
        return {'status': 200}


class Message:

    @staticmethod
    async def save_message(db: AsyncIOMotorDatabase,  user, message):
        await db.Aiocollection.insert_one({'user': user, 'message': message})
        return {'status': 200}

    @staticmethod
    async def get_all_message(db: AsyncIOMotorDatabase):
        lst = []
        cursor = db.Aiocollection.find()
        for elem in await cursor:
            lst.append(elem)
        return lst