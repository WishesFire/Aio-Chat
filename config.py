import os
from cryptography.fernet import Fernet
import pickle

SECRET_SITE_RECAPTCHA = '*'
SECRET_KEY_RECAPTCHA = '*'
SITE_STORAGE = {}
BASE_DIR = f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/templates'
BASE_STATIC_DIR = os.path.abspath(f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/static')
MONGO_HOST = 'mongodb+srv://WishesFire:1NQz6tTf8WUpKV7N@cluster.gmwe0.mongodb.net/AioDB?retryWrites=true&w=majority'
SECRET_KEY = '68028350928350928502899'
FORM_FIELD_NAME = '_csrf_token'
COOKIE_NAME = 'csrf_token'
PASSWORD_REDIS = 'gkFodk34@kG2p3Hgks342'
PUBLIC_KEY = b''
PRIVATE_KEY = b''
PRIVATE_KEY_PATH = BASE_STATIC_DIR + '/privat_key/private_key.pickle'


async def generate_key():
    global PRIVATE_KEY
    print('Launching back tasks keys')
    PRIVATE_KEY += Fernet.generate_key()
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        pickle.dump(PRIVATE_KEY, f)