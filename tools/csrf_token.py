import uuid


async def generate_token():
    salt = "22-_-22"
    uuid_token = uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')
    token = salt + ':' + str(uuid_token)
    return token


async def check_token(session_token, html_token):
    if session_token == html_token:
        return True
    else:
        return False