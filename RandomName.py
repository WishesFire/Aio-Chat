import string
import random

def create_username():
    alphabet = string.ascii_lowercase + '123456789!@#$*'
    nicks = ''.join([random.choice(random.choice(alphabet)) for _ in range(random.randint(8, 14))])
    finally_nick = ''
    for x in nicks:
        choice = random.choice([True, False])
        if choice:
            finally_nick += x.upper()
        else:
            finally_nick += x

    return finally_nick