from random import randint, sample
from cryptography.fernet import Fernet
import string


async def generate_key_room(redis, room_name):
    public_key = Fernet.generate_key()
    chose = randint(0, 1)
    chars = ''.join(sample(string.ascii_letters, 10))
    public_key = public_key.decode('utf-8')

    if chose == 0:
        public_key += str(chars) + '@'
    else:
        public_key = '@' + str(chars) + public_key

    await redis.hmset(room_name, 'public_key', public_key.encode())

    return public_key
