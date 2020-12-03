import os

SECRET_SITE_RECAPTCHA = '*'
SECRET_KEY_RECAPTCHA = '*'
BASE_DIR = f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/templates'
BASE_STATIC_DIR = os.path.abspath(f'{os.path.dirname(os.path.dirname(__file__))}/aiochat/static')
MONGO_HOST = '*'
SECRET_KEY = '68028350928350928502899'
FORM_FIELD_NAME = '_csrf_token'
COOKIE_NAME = 'csrf_token'